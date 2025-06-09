import re

import spellbind


def test_version_exists():
    assert hasattr(spellbind, '__version__')
    assert spellbind.__version__ is not None


def test_version_format():
    version = spellbind.__version__
    # Should be semver-like: 0.1.0, 0.1.0.dev1+g123abc, etc.
    pattern = r'^\d+\.\d+\.\d+(?:\.dev\d+\+g[a-f0-9]+)?$'
    assert re.match(pattern, version), f"Version '{version}' doesn't match expected format"
