import sys

_PYTHON_VERSION = sys.version_info[:2]
if _PYTHON_VERSION < (3, 4):
    # -- NEED: pathlib.Path.write_text()/.read_text()
    from pathlib2 import Path  # pragma: no cover
else:
    from pathlib import Path   # noqa: F401
