"""Файл запуска Timer 2 из исходников и при сборке PyInstaller."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

from timer_3.main import main


if __name__ == "__main__":
    main()
