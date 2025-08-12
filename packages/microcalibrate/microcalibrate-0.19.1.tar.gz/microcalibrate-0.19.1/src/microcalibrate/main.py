"""
MicroCalibrate Package

A package for calibrating microdata.
"""

__version__ = "0.1.0"

from microcalibrate.config import configure_logging


def main():
    # Logging configuration
    configure_logging()


if __name__ == "__main__":
    main()
