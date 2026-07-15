from __future__ import annotations

import logging

from .config import LOGS_DIR

LOG_FILE_NAME = "pipeline.log"
_CONFIGURED = False


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configura logging de aplicacao para stdout e para outputs/logs/pipeline.log.

    Idempotente: chamadas repetidas nao duplicam handlers, permitindo que cada
    script de execucao chame esta funcao no inicio sem efeitos colaterais.
    """
    global _CONFIGURED
    root_logger = logging.getLogger()

    if _CONFIGURED:
        return root_logger

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOGS_DIR / LOG_FILE_NAME, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    _CONFIGURED = True
    return root_logger
