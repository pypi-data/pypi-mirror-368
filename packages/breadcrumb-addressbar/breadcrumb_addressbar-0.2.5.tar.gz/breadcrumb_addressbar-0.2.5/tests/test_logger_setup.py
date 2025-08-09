"""
Logger setup tests.
"""

import logging
from pathlib import Path

from breadcrumb_addressbar.logger_setup import (
    critical,
    debug,
    error,
    get_logger,
    info,
    setup_logger,
    warning,
)


def test_setup_logger_configures_console_handler():
    name = "breadcrumb_addressbar.test.logger1"
    logger = setup_logger(name=name, level=logging.DEBUG)

    assert logger.name == name
    assert logger.level == logging.DEBUG
    # 少なくとも1つはコンソールハンドラが付与される
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_setup_logger_with_file(tmp_path):
    name = "breadcrumb_addressbar.test.logger2"
    log_file = tmp_path / "test.log"

    logger = setup_logger(
        name=name,
        level=logging.INFO,
        log_file=str(log_file),
    )
    logger.info("hello file")

    assert Path(log_file).exists()
    content = Path(log_file).read_text(encoding="utf-8")
    assert "hello file" in content


def test_get_logger_returns_configured_logger():
    name = "breadcrumb_addressbar.test.logger3"
    setup_logger(name=name, level=logging.WARNING)
    logger = get_logger(name)
    assert logger.name == name
    assert logger.level == logging.WARNING


def test_wrapper_functions_and_handler_clearing(tmp_path):
    name = "breadcrumb_addressbar.test.logger4"
    logger = setup_logger(name=name, level=logging.DEBUG)
    # ハンドラを意図的に追加してから再セット -> clearing 分岐を通す
    logger.addHandler(logging.StreamHandler())
    logger = setup_logger(name=name, level=logging.INFO)

    # ラッパー呼び出しで例外が出ないこと（出力は不要）
    debug("d")
    info("i")
    warning("w")
    error("e")
    critical("c")
