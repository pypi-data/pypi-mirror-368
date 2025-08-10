itry:
    from importlib.metadata import version, PackageNotFoundError  # Py3.8+
except Exception:  # pragma: no cover
    version = None
    PackageNotFoundError = Exception

__all__ = ["__version__"]

try:
    __version__ = version("eqnlint") if version else "0+unknown"
except PackageNotFoundError:
    __version__ = "0+unknown"
