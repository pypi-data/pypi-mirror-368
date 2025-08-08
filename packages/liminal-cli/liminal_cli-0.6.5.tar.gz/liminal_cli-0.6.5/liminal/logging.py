
import builtins
import io
import logging
import logging.config
from pathlib import Path
import sys

from liminal import LIMINAL_CLI_NAME, LIMINAL_DIR



LIMINAL_LOG_DIR = LIMINAL_DIR / 'logs'
INSTALL_LOG_PATH = Path(LIMINAL_LOG_DIR) / 'install-log.txt'

def setup_logging() -> logging.Logger:

	LIMINAL_LOG_DIR.mkdir(parents=True, exist_ok=True)

	root_log_config = {
		"version": 1,
		"disable_existing_loggers": False,
		"formatters": {
			# https://docs.python.org/3/library/logging.html#logrecord-attributes
			f"{LIMINAL_CLI_NAME}_basicFormatter": {
				"format": "[%(asctime)s %(levelname)s] - %(message)s",
				"datefmt": "%H:%M:%S",
			},
			f"{LIMINAL_CLI_NAME}_verboseFormatter": {
				"format":
					"[%(asctime)s %(levelname)s %(process)d %(name)s %(filename)s:%(funcName)s:%(lineno)d] - %(message)s",
				"datefmt": "%Y-%m-%dT%H:%M:%S%z",
			},
			f"{LIMINAL_CLI_NAME}_syslogFormatter": {
				"format": "%(levelname)s %(name)s %(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
			}
		},
		"handlers": {
			f"{LIMINAL_CLI_NAME}_consoleHandler": {
				"level": logging.INFO,
				"class": "logging.StreamHandler",
				"formatter": f"{LIMINAL_CLI_NAME}_basicFormatter",
				"stream": sys.stdout,
			},
			f"{LIMINAL_CLI_NAME}_plaintextFileHandler": {
				"level": "DEBUG",
				"class": "logging.handlers.RotatingFileHandler",
				"formatter": f"{LIMINAL_CLI_NAME}_verboseFormatter",
				"filename": INSTALL_LOG_PATH,
				"maxBytes": 5e6, # 5MB
				"backupCount": 5,
			},
			f"{LIMINAL_CLI_NAME}_syslogHandler": {
				"level": logging.INFO,
				"class": "logging.handlers.SysLogHandler",
				"formatter": f"{LIMINAL_CLI_NAME}_syslogFormatter",
			},
		},
		"loggers": {
			LIMINAL_CLI_NAME: {
				"level": "DEBUG",
				"handlers": [f'{LIMINAL_CLI_NAME}_consoleHandler', f'{LIMINAL_CLI_NAME}_plaintextFileHandler', f'{LIMINAL_CLI_NAME}_syslogHandler'],
			},
		},
	}

	logging.config.dictConfig(config=root_log_config)
	return logging.getLogger(LIMINAL_CLI_NAME)

LOGGER = setup_logging()


def enable_sending_prints_to_logger(logger):
    """
    Overrides the built-in print() function to redirect its output to a logger.
    
    This version correctly handles print() arguments like 'sep' and 'end',
    and uses stacklevel=2 to report the correct caller line number.
    """
    original_print = builtins.print

    def new_print(*args, **kwargs):
        original_print(*args, **kwargs)
        # To handle 'sep', 'end', 'file' etc. correctly, we can capture the
        # output of the original print function in a string buffer.

		# include in log file
        string_io = io.StringIO()
        kwargs['file'] = string_io
        original_print(*args, **kwargs)
        message = string_io.getvalue().rstrip('\n')
        logger.debug(message, stacklevel=2)

    builtins.print = new_print
