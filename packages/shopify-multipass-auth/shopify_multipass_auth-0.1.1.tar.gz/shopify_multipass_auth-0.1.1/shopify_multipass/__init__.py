try:
    from ._version import __version__
except ImportError:
    # fallback for development/editable installs
    try:
        from setuptools_scm import get_version

        __version__ = get_version(root="..", relative_to=__file__)
    except ImportError:
        __version__ = "unknown"

from .multipass import MultiPass

__all__ = ["MultiPass"]
