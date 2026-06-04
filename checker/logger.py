import datetime as dt
import json
import logging
import traceback
from typing import Any, Optional, Union
from overrides import override

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class MyJSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: Optional[dict[str, str]] = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        if record.levelno >= logging.ERROR:
            return json.dumps(message, default=str, indent=2, ensure_ascii=False)
        return json.dumps(message, default=str, ensure_ascii=False)

    def _format_exception(self, record: logging.LogRecord) -> Optional[dict[str, Any]]:
        if record.exc_info is not None:
            exc_type, exc_value, exc_tb = record.exc_info
        elif record.exc_text:
            return {"traceback_lines": record.exc_text.splitlines()}
        else:
            return None

        frames = [
            {
                "file": frame.filename,
                "line": frame.lineno,
                "function": frame.name,
                "code": frame.line,
            }
            for frame in traceback.extract_tb(exc_tb)
        ]
        tb_lines: list[str] = []
        for chunk in traceback.format_exception(exc_type, exc_value, exc_tb):
            tb_lines.extend(line for line in chunk.rstrip("\n").split("\n") if line)

        return {
            "type": exc_type.__name__ if exc_type else None,
            "module": getattr(exc_type, "__module__", None) if exc_type else None,
            "message": str(exc_value) if exc_value else None,
            "frames": frames,
            "traceback_lines": tb_lines,
        }

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(record.created).isoformat(),
        }
        if exception := self._format_exception(record):
            always_fields["exception"] = exception

        if record.stack_info is not None:
            always_fields["stack_info"] = [
                line for line in self.formatStack(record.stack_info).splitlines() if line
            ]

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> Union[bool, logging.LogRecord]:
        return record.levelno <= logging.INFO