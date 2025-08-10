from dotenv import load_dotenv
load_dotenv()

from collections.abc import Callable
from loglocal._loglocal import LogLocal
from opentelemetry.trace import Tracer as _Tracer
from loglocal._trace import get_tracer as _get_tracer

# logger = LogLocal.default()
# tracer = logger.get_tracer()
Logger: Callable[..., LogLocal] = LogLocal.from_config
Tracer: Callable[..., _Tracer] = _get_tracer
__all__ = [
    # "logger",
    "Logger",
    # "tracer",
    "Tracer",
    "LogLocal"
]