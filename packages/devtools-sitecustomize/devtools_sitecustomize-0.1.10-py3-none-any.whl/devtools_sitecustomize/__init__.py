__version__ = '0.1.10'
import builtins
import sys


def add_debug_to_builtins():
    # Follow the instructions at
    # https://python-devtools.helpmanual.io/usage/#manual-install
    # only we are sure that devtools is already installed as a dependency.
    if sys.argv[0].endswith(('pytest', 'pytest.exe')):
        # we don't install here for pytest as it breaks pytest, it is
        # installed later by a pytest fixture
        return
    from devtools import debug

    setattr(builtins, 'debug', debug)
