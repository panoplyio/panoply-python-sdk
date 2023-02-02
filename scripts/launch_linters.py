import logging
import os
import subprocess as sp

DIR_PATH = os.path.dirname(__file__)
FLAKE_CONFIG = os.path.join(DIR_PATH, ".flake8")
RUFF_CONFIG = os.path.join(DIR_PATH, "ruff.toml")
logger = logging.getLogger(__name__)


def main():
    black = ["black", "--skip-string-normalization", "-l", "120", "."]
    ruff = ["ruff", "--fix", "--config", RUFF_CONFIG, "."]
    flake8 = ["flake8", "--config", FLAKE_CONFIG, "."]
    for conf in (black, ruff, flake8):
        try:
            sp.call(conf)
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    exit(main())
