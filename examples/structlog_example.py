import structlog
import logging
import sys
# Setup rich logging
from rich.console import Console
from rich.traceback import install as install_rich_traceback

install_rich_traceback()  # Pretty tracebacks in terminal

# Setup standard logging
logging.basicConfig(
    format="%(message)s",
    stream=sys.stderr,
    level=logging.DEBUG,
)

# Wrap standard logger with structlog
structlog.configure(
    processors=[
        structlog.threadlocal.merge_threadlocal,      # Optional: if you're using thread-local context
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(colors=True),   # Pretty print with colors (like screenshot)
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    cache_logger_on_first_use=True,
)

# Simulate a class for demo
class SomeClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"SomeClass(x={self.x!r}, y={self.y!r})"


log = structlog.get_logger("some_logger")
log2 = structlog.get_logger("another_logger")

log.debug("debugging is hard")
log.info("informative!", some_key="some_value")
log.warning("uh-uh!")
log.error("omg", a_dict={"a": 42, "b": "foo"})
log.critical("wtf", what=SomeClass(x=1, y="z"))

try:
    def make_call_stack_more_impressive():
        try:
            d = {"x": 42}
            print(SomeClass(d["y"], "foo"))  # KeyError here
        except Exception:
            log2.exception("poor me")
        log.info("all better now!")

    make_call_stack_more_impressive()

except Exception as e:
    log.error("still broken", error=str(e))
