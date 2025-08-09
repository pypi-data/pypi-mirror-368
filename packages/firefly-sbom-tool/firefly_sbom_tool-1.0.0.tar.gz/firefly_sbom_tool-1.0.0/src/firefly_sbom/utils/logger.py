"""Logging utilities - Copyright 2024 Firefly OSS"""

import logging
import sys


def setup_logger(name="firefly-sbom"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(name):
    return logging.getLogger(name)
