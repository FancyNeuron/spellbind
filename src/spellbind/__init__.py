try:
    from .version import __version__
except ImportError:
    from importlib.metadata import version
    __version__ = version("spellbind")
