from dassco_utils.guid import create_guid
from datetime import datetime as RealDatetime

def test_create_guid(monkeypatch):
    class FixedDatetime(RealDatetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2025, 8, 11, 14, 3, 5, 123456)

    module = create_guid.__module__
    monkeypatch.setattr(f"{module}.datetime", FixedDatetime)
    monkeypatch.setattr(f"{module}.random.randint", lambda a, b: 12345678)

    constant = '040ck2b86'

    expected_components = [
        '040ck2b86',
        '7e9',
        '8'
        '0b',
        '0e',
        '03',
        '05',
        '07b',
        'bc614e',
    ]

    guid = create_guid(constant)
    expected_guid = ''.join(expected_components)
    assert guid == expected_guid



