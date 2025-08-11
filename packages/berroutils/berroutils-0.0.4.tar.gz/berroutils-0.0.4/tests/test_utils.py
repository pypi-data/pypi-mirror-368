import pytest

from berroutils.utils import is_empty_or_nan


@pytest.mark.parametrize("entry, expected", [
    ('  ', True),
    ([], True),
    (set(), True),
    (float('nan'), True),
    ('nan', True),
    ('3', False),
    (3, False)
])
def test_is_empty_or_nan(entry, expected):
    assert is_empty_or_nan(entry) == expected
