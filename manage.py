#!/usr/bin/env python
"""Entry point for the ``site/`` project — mdjango's self-hosted docs site (and dev harness)."""

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # the project package (config) lives under site/, like walden's site
    sys.path.insert(0, str(Path(__file__).resolve().parent / "site"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
