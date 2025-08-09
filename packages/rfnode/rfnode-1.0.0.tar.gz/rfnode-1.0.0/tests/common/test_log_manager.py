import logging

from rfnode.common.log_manager import LogManager


def test_singleton():
    manager1: LogManager = LogManager()
    manager2: LogManager = LogManager()
    manager3: LogManager = LogManager()
    assert manager1 is manager2  # same instance
    assert manager2 is manager3


def test_config():
    manager: LogManager = LogManager()
    manager.config_logger(3, "./")
    logger = logging.getLogger("rstsdl")
    assert logger is not None
