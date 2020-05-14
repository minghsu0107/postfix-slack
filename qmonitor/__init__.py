import sys
from functools import wraps
from datetime import datetime

#: Boolean to control activation of the :func:`debug` decorator.
DEBUG = False

#: Current version of the package as :class:`str`.
VERSION = "1.0.0"

#: Module configuration as :class:`dict`.
CONFIG = {
    "core": {
        "postfix_spool": "/var/spool/postfix"
    },
    "commands": {
        "use_sudo": False,
        "list_queue": ["mailq"],
        "cat_message": ["postcat", "-qv"],
        "hold_message": ["postsuper", "-h"],
        "release_message": ["postsuper", "-H"],
        "requeue_message": ["postsuper", "-r"],
        "delete_message": ["postsuper", "-d"]
    }
}


def debug(function):
    """
    Decorator to print some call informations and timing debug on stderr.
    Function's name, passed args and kwargs are printed to stderr. Elapsed time
    is also print at the end of call. This decorator is based on the value of
    :data:`DEBUG`. If ``True``, the debug informations will be displayed.
    """
    @wraps(function)
    def run(*args, **kwargs):
        name = function.__name__
        if DEBUG is True:
            sys.stderr.write("[DEBUG] Running {0}\n".format(name))
            sys.stderr.write("[DEBUG]     args: {0}\n".format(args))
            sys.stderr.write("[DEBUG]   kwargs: {0}\n".format(kwargs))
            start = datetime.now()

        ret = function(*args, **kwargs)

        if DEBUG is True:
            stop = datetime.now()
            sys.stderr.write("[DEBUG] Exectime of {0}: {1} seconds\n".format(
                                        name, (stop - start).total_seconds()))

        return ret

    return run