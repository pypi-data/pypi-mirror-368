from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def test_log_rotation_rollover(tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    logger = logging.getLogger("obk.test.rotation")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(log_file, maxBytes=128, backupCount=1, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)

    for i in range(200):
        logger.info("line %03d: %s", i, "x" * 40)

    logger.handlers.clear()
    handler.close()

    assert log_file.exists()
    rotated = log_file.with_suffix(".log.1")
    alt_rotated = log_file.with_name(log_file.name + ".1")
    assert rotated.exists() or alt_rotated.exists()
