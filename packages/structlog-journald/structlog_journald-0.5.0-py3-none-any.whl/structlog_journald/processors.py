from typing import Any, TypedDict

from structlog import DropEvent
from structlog.processors import CallsiteParameter
from structlog.typing import EventDict, WrappedLogger

from .consts import CY, LEVEL_TO_PRIORITY
from .detect import is_journald_connected


# Items in EventDict, which are used by other processors
# and should not be rendered by us.
OTHER_PROCESSOR_KEYS = ('message', 'event', 'exec_info', 'exception', 'level', 'timestamp', 'stack', 'stack_info')


class CallsiteInfo(TypedDict, total=False):
    MODULE: str
    # These fields follow name convention from https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html
    CODE_FUNC: str
    CODE_FILE: str
    CODE_LINE: int
    TID: int


class JournaldProcessor:
    """Processor for sending log events to journald.

    ``journald`` allows to attach extra fields to a log entry. These fields are extracted from *structlog*'s ``event_dict``.
    The selection is based on the keys starting with the specified prefix.
    For example, if the prefix is ``'f_'``, the items with ``'f_blah'``, ``'f_baz'`` keys will be sent to *journald* as extra fields.
    Note that, by *journald* convention, these keys will be converted to uppercase, so ``'f_blah'`` will be sent as ``'F_BLAH'``.
    """

    syslog_identifier: str | None
    """The identifier to use when sending events to journald."""

    extra_field_prefix: str
    """The items in ``event_dict`` having key with this prefix will be sent to journald."""

    drop: bool
    """Whether to drop the event after sending it to journald."""

    def __init__(self, syslog_identifier: str | None = None, extra_field_prefix: str = 'f_', drop: bool = True) -> None:
        """
        Args:
            syslog_identifier (str | None): The identifier to use when sending events to journald.
            extra_field_prefix (str): The items in ``event_dict`` having key with this prefix will be sent to journald.
            drop (bool): Whether to drop the event after sending it to journald.
        """
        # We are not allowed to send extra fields starting with '_', because those keys are reserved for journald's internal use.
        if extra_field_prefix.startswith('_'):
            raise ValueError("extra_field_prefix cannot start with '_'")
        self.syslog_identifier = syslog_identifier
        self.extra_field_prefix = extra_field_prefix
        self.drop = drop

    def _extract_common_fields(self, event_dict: EventDict) -> dict[str, Any]:
        # This field is populated by `add_logger_name` processor.
        if logger_name := event_dict.get('logger'):
            return {'LOGGER': logger_name}
        return {}

    def _extract_extra_fields(self, event_dict: EventDict) -> dict[str, Any]:
        if not self.extra_field_prefix:
            return {}
        return {k.upper(): v for k, v in event_dict.items() if k.startswith(self.extra_field_prefix)}

    def _extract_callsite_info(self, event_dict: EventDict) -> CallsiteInfo:
        """
        Retrieve callsite info which CallsiteParameterAdder has added
        """
        info: CallsiteInfo = {}
        if module_name := event_dict.get(CallsiteParameter.MODULE.value):
            info['MODULE'] = module_name
        if func_name := event_dict.get(CallsiteParameter.FUNC_NAME.value):
            info['CODE_FUNC'] = func_name
        if code_file := event_dict.get(CallsiteParameter.PATHNAME.value):
            info['CODE_FILE'] = code_file
        if code_line := event_dict.get(CallsiteParameter.LINENO.value):
            info['CODE_LINE'] = code_line
        if thread_id := event_dict.get(CallsiteParameter.THREAD.value):
            info['TID'] = thread_id
        return info

    def _format_extra_items(self, event_dict: EventDict) -> str:
        """
        Format extra items (other than the message) in event_dict as key=value.
        """
        ignored_keys: set[str] = {*OTHER_PROCESSOR_KEYS, *[p.value for p in CallsiteParameter]}
        if self.extra_field_prefix:
            ignored_keys.update(k for k in event_dict.keys() if k.startswith(self.extra_field_prefix))
        pairs: list[str] = []
        for k, v in event_dict.items():
            # We also skip keys which start with '_'. They are for structlog internal use.
            if k.startswith('_') or k in ignored_keys:
                continue
            pairs.append(f'{k}={v!r}')
        return ' '.join(pairs)

    def __call__(self, logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
        if not is_journald_connected():
            return event_dict
        # Originally, the message will be at event_dict['event'], but sometimes the EventRenamer processor is used,
        # which renames the message key to 'message'. We try both.
        message = event_dict.get('message')
        if message is None:
            message = event_dict.pop('event')
        # Message is not found
        if message is None:
            return event_dict
        default_priority = LEVEL_TO_PRIORITY['info']
        priority = LEVEL_TO_PRIORITY.get(method_name, default_priority)
        journal_extra_fields = self._extract_common_fields(event_dict)
        callsite_info = self._extract_callsite_info(event_dict)
        journal_extra_fields.update(self._extract_extra_fields(event_dict))
        journal_extra_fields.update(callsite_info)
        if self.syslog_identifier:
            journal_extra_fields['SYSLOG_IDENTIFIER'] = self.syslog_identifier

        # Though that we expect `message` to be string, library user may not apply type-checking
        # and pass arbitrary data, so we will convert to string.
        message_str = message if isinstance(message, str) else str(message, errors='replace')

        if key_value_extra := self._format_extra_items(event_dict):
            message_str += '\n' + key_value_extra

        # When the logger was called with `exception()` or `aexception()` methods, we also send the exception information.
        # Note: When testing, the method name then is still 'error'. I don't know how structlog defines the method name.
        if method_name in ('exception', 'aexception', 'error', 'aerror'):
            # The event_dict may already be populated an "exception" item by `format_exc_info` processor.
            if exc_str := event_dict.get('exception'):
                message_str += f'\n{exc_str}'
            # In case `format_exc_info` was not in the chain, we just send "exc_info" to the `EXCEPTION_INFO` field like
            # JournalHandler (from systemd-python) does.
            elif exc_info := event_dict.get('exc_info'):
                message_str += f'\n{exc_info}'
                journal_extra_fields['EXCEPTION_INFO'] = exc_info
            elif method_name in ('exception', 'aexception'):
                message_str += '\n(Missing exception information)'

        if CY:
            send_to_cysystemd_journal(message_str, priority, **journal_extra_fields)
        else:
            send_to_standard_journal(message_str, priority, **journal_extra_fields)
        if self.drop:
            raise DropEvent
        return event_dict


def send_to_standard_journal(message: str, priority: int, **extra_fields: dict[str, Any]) -> None:
    from systemd import journal

    journal.send(message, PRIORITY=priority, **extra_fields)


def send_to_cysystemd_journal(message: str, priority: int, **extra_fields: dict[str, Any]) -> None:
    try:
        from cysystemd import journal

        # cysystemd doesn't allow positional arguments.
        journal.send(message=message, priority=priority, **extra_fields)
    except ModuleNotFoundError:
        pass
