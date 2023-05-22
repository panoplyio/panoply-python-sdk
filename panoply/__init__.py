import logging

from sys import stdout
from traceback import print_exception as _print_exception

from .datasource import *
from .sdk import *
from .ssh import SSHTunnel


logging.basicConfig(stream=stdout)


def custom_excepthook(args, /):
    """
    Handle uncaught Thread.run() exception
    and print error text to STDOUT instead of STDERR.

    "It's always assumed that
    the runnner is single-threaded and synchronuous such that `result` events
    are only assigned to the last executed request".
    see https://github.com/panoplyio/legacy-source-wrapper/blob/master/src/sources-runner/index.js#L74
    """
    if args.exc_type == SystemExit:
        # silently ignore SystemExit
        return

    logging.error(f"Caught an exception in thread:")
    _print_exception(args.exc_type, args.exc_value, args.exc_traceback,
                     file=stdout)


threading.excepthook = custom_excepthook
