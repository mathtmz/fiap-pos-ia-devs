import logging

from pcos_fase2 import logging_setup
from pcos_fase2.config import LOGS_DIR


def test_configure_logging_creates_log_file_and_is_idempotent():
    logging_setup._CONFIGURED = False
    root_logger = logging.getLogger()
    handlers_before = list(root_logger.handlers)

    try:
        logging_setup.configure_logging()
        handlers_after_first_call = len(root_logger.handlers)
        logging_setup.configure_logging()
        handlers_after_second_call = len(root_logger.handlers)

        assert handlers_after_first_call == handlers_after_second_call
        assert (LOGS_DIR / logging_setup.LOG_FILE_NAME).exists()
    finally:
        root_logger.handlers = handlers_before
        logging_setup._CONFIGURED = False
