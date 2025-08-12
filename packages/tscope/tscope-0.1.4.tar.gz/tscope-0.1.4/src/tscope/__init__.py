"""
TerminalScope - A simple Python oscilloscope for displaying 1-dim dynamic data in the command line
"""

from .main import TerminalScope

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

__author__ = "Henrik"
__email__ = "im.zhangxc@gmail.com"

__all__ = ["TerminalScope"]

del main
