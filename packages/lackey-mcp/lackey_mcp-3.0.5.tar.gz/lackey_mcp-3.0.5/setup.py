#!/usr/bin/env python
"""Setup script for backward compatibility.

Modern pip versions use pyproject.toml directly, but setup.py
is included for compatibility with older tools and editable installs.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()
