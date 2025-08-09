import sys
from . import conftest as _conftest  # noqa: F401

# Allow `from conftest import ...` and `from .conftest import ...`
sys.modules.setdefault("conftest", _conftest) 