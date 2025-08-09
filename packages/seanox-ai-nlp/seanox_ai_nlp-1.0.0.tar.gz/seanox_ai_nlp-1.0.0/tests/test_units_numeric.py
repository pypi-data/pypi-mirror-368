# tests/test_units_numeric.py

from seanox_ai_nlp.units import NUMERIC_VALIDATION_PATTERN

import pytest


def _assert_numeric_pattern(pattern, valid, invalid, label):
    for numeric in valid:
        assert pattern.match(numeric), f"[{label}] Should match: {numeric}"
    for numeric in invalid:
        assert not pattern.match(numeric), f"[{label}] Should NOT match: {numeric}"


@pytest.mark.parametrize("pattern, valid, invalid", [
    (NUMERIC_VALIDATION_PATTERN,
     ["1.234", "12.345,67", "123456", "1.000.000,99"],
     [])
])
def test_numeric_de_patterns(pattern, valid, invalid):
    _assert_numeric_pattern(pattern, valid, invalid, "DE")


@pytest.mark.parametrize("pattern, valid, invalid", [
    (NUMERIC_VALIDATION_PATTERN,
     ["1,234", "12,345.67", "123456", "1,000,000.99"],
     [])])
def test_numeric_en_patterns(pattern, valid, invalid):
    _assert_numeric_pattern(pattern, valid, invalid, "EN")


@pytest.mark.parametrize("pattern, valid, invalid", [
    (NUMERIC_VALIDATION_PATTERN,
     ["1’234", "12’345,67", "123456", "1’000’000,99"],
     [])
])
def test_numeric_ch_patterns(pattern, valid, invalid):
    _assert_numeric_pattern(pattern, valid, invalid, "CH")


@pytest.mark.parametrize("pattern, valid, invalid", [
    (NUMERIC_VALIDATION_PATTERN,
     ["1 234", "12 345,67", "123456", "1 000 000,99"],
     [])
])
def test_numeric_fr_patterns(pattern, valid, invalid):
    _assert_numeric_pattern(pattern, valid, invalid, "FR")


@pytest.mark.parametrize("pattern, valid, invalid", [
    (NUMERIC_VALIDATION_PATTERN,
     ["1,23,456", "12,34,567.89", "123456", "1,00,00,000.99"],
     [])
])
def test_numeric_in_patterns(pattern, valid, invalid):
    _assert_numeric_pattern(pattern, valid, invalid, "IN")


@pytest.mark.parametrize("pattern, valid, invalid", [
    (NUMERIC_VALIDATION_PATTERN,
     ["12345.67", "12\u202F345.67", "12345", "1\u202F234\u202F567.89"],
     ["12\u202F345,67", "1\u202F234\u202F567,89"])
])
def test_numeric_iso_patterns(pattern, valid, invalid):
    _assert_numeric_pattern(pattern, valid, invalid, "ISO")
