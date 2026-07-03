"""
Logger qui filtre automatiquement les valeurs sensibles (tokens) pour
éviter qu'elles ne finissent dans des logs partagés (console d'hébergeur,
fichiers, services tiers, etc.).
"""

import logging
import os
import re

TOKEN_PATTERN = re.compile(r"[\w-]{24,28}\.[\w-]{6}\.[\w-]{27,}")


class RedactSecretsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = TOKEN_PATTERN.sub("[REDACTED_TOKEN]", record.msg)
        if record.args:
            record.args = tuple(
                TOKEN_PATTERN.sub("[REDACTED_TOKEN]", str(arg))
                if isinstance(arg, str)
                else arg
                for arg in record.args
            )
        return True


def get_logger(name: str = "discord-bot") -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
        logger.setLevel(level)

        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(levelname)-5s] %(asctime)s - %(name)s - %(message)s")
        )
        handler.addFilter(RedactSecretsFilter())
        logger.addHandler(handler)

    return logger
