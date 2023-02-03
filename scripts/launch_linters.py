import argparse
import logging
import os
import subprocess as sp

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--static', action='store_true', help='Will not fix errors, or format code')

arguments = parser.parse_args()
my_args = vars(arguments)

DIR_PATH = os.path.dirname(__file__)
FLAKE_CONFIG = os.path.join(DIR_PATH, '.flake8')
RUFF_CONFIG = os.path.join(DIR_PATH, 'ruff.toml')
logger = logging.getLogger(__name__)


def get_commands():
    black = ['black', '--skip-string-normalization', '-l', '120', '.']
    ruff = ['ruff', '--fix', '--config', RUFF_CONFIG, '.']
    flake8 = ['flake8', '--config', FLAKE_CONFIG, '.']

    if my_args.get('static'):
        ruff.remove('--fix')
        return ruff, flake8
    return black, ruff, flake8


def main():
    commands = get_commands()
    for command in commands:
        try:
            sp.call(command)
        except Exception as e:
            logger.error(f'Error: {e}')


if __name__ == '__main__':
    exit(main())
