import logging.config
import structlog

# Taken from: https://www.structlog.org/en/stable/standard-library.html

initialized = False

def setup(config):
    global initialized
    # Only setup logging once
    if initialized:
        print("Logging already initalized")
        return
    initialized = True

    # if no config given, use a empty config
    if config is None:
        config = {}

    # Setup logging!
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
    pre_chain = [
        # Add the log.py level and a timestamp to the event_dict if the log.py entry
        # is not from structlog.
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    global_log_level = "DEBUG"
    serial_log_level = "DEBUG"
    bluetooth_log_level = "DEBUG"
    bleak_log_level = "INFO"

    if "global_level" in config:
        global_log_level = config["global_level"]
    if "serial_level" in config:
        serial_log_level = config["serial_level"]
    if "bluetooth_level" in config:
        bluetooth_log_level = config["bluetooth_level"]
    if "bleak_level" in config:
        bleak_log_level = config["bleak_level"]

    logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "plain": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(colors=False),
                    "foreign_pre_chain": pre_chain,
                },
                "colored": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(colors=True),
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "colored",
                },
                "file": {
                    "level": "DEBUG",
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": "ds_gui.log",
                    "formatter": "plain",
                },
            },
            "loggers": {
                # use the following to control log levels
                "": {
                    # "handlers": ["default"],
                    "handlers": ["default", "file"],
                    "level": global_log_level,
                    "propagate": True,
                },
                "communication.serial": {
                    # "handlers": ["default"],
                    "handlers": ["default", "file"],
                    "level": serial_log_level,
                    "propagate": True,
                },
                "communication.bluetooth": {
                    # "handlers": ["default"],
                    "handlers": ["default", "file"],
                    "level": bluetooth_log_level,
                    "propagate": True,

                },
                "bleak": {
                    # "handlers": ["default"],
                    "handlers": ["default", "file"],
                    "level": bleak_log_level,
                    "propagate": True,
                }
            }
    })

    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )