"""Version information for vibe."""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installations
    __version__ = "0.1.0+dev"

__all__ = ["__version__"]
