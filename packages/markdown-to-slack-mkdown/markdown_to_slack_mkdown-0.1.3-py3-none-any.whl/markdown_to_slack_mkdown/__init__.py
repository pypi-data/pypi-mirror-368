from .converter import slack_convert, SlackConvertOptions

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"

__all__ = ["slack_convert", "SlackConvertOptions", "__version__"]
