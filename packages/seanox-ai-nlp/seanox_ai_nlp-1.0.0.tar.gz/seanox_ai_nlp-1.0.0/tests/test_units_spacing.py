# tests/test_units_spacing.py

from seanox_ai_nlp.units import spacing

import re
import pytest


def _generate_spacing_variants(base: str, pattern: str, effect_expected: bool):
    match = re.search(pattern, base)
    position = match.start()
    result = []
    for space in ["", " ", "  "]:
        input = base[:position] + space + base[position:]
        expected_space = " " if effect_expected else space
        expected = base[:position] + expected_space + base[position:]
        result.append((input, expected))
    return result


# simple units


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("100m", r"(?<=100)(?=m)", True))
def test_spacing_01(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("100km", r"(?<=100)(?=km)", True))
def test_spacing_02(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("100km/s", r"(?<=100)(?=km)", True))
def test_spacing_03(input, expected):
    assert spacing(input) == expected


# simple units with invalid prefix


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100m", r"(?<=100)(?=m)", True))
def test_spacing_04(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100km", r"(?<=100)(?=km)", True))
def test_spacing_05(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100km/s", r"(?<=100)(?=km)", True))
def test_spacing_06(input, expected):
    assert spacing(input) == expected


# simple units with invalid suffix


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100mx", r"(?<=100)(?=m)", False))
def test_spacing_07(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100kmx", r"(?<=100)(?=km)", False))
def test_spacing_08(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100km/sx", r"(?<=100)(?=km)", False))
def test_spacing_09(input, expected):
    assert spacing(input) == expected


# simple units with downstream text


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100m xxx", r"(?<=100)(?=m)", True))
def test_spacing_10(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100km xxx", r"(?<=100)(?=km)", True))
def test_spacing_11(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("x100km/s xxx", r"(?<=100)(?=km)", True))
def test_spacing_12(input, expected):
    assert spacing(input) == expected


# simple units embedded


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100m xxx", r"(?<=100)(?=m)", True))
def test_spacing_13(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100km xxx", r"(?<=100)(?=km)", True))
def test_spacing_14(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100km/s xxx", r"(?<=100)(?=km)", True))
def test_spacing_15(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100km\u00B7s/ft", r"(?<=100)(?=km)", True))
def test_spacing_16(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100km\u00B7s", r"(?<=100)(?=km)", True))
def test_spacing_17(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100km/s/ft", r"(?<=100)(?=km)", True))
def test_spacing_18(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100km/s", r"(?<=100)(?=km)", True))
def test_spacing_19(input, expected):
    assert spacing(input) == expected


# simple units without values (invalid)


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxxkm/s", r"(?<=x)(?=km)", False))
def test_spacing_20(input, expected):
    assert spacing(input) == expected


# simple units with commas in values


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,m xxx", r"(?<=100,)(?=m)", False))
def test_spacing_21(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,km xxx", r"(?<=100,)(?=km)", False))
def test_spacing_22(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,km/s xxx", r"(?<=100,)(?=km)", False))
def test_spacing_22(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,km\u00B7s/ft", r"(?<=100,)(?=km)", False))
def test_spacing_22(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,km\u00B7s", r"(?<=100,)(?=km)", False))
def test_spacing_23(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,km/s/ft", r"(?<=100,)(?=km)", False))
def test_spacing_24(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,km/s", r"(?<=100,)(?=km)", False))
def test_spacing_25(input, expected):
    assert spacing(input) == expected


# simple units with commas as decimals

@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,0m xxx", r"(?<=100,0)(?=m)", True))
def test_spacing_21(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,0km xxx", r"(?<=100,0)(?=km)", True))
def test_spacing_22(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,0km/s xxx", r"(?<=100,0)(?=km)", True))
def test_spacing_23(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,0km\u00B7s/ft", r"(?<=100,0)(?=km)", True))
def test_spacing_24(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,0km\u00B7s", r"(?<=100,0)(?=km)", True))
def test_spacing_25(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,0km/s/ft", r"(?<=100,0)(?=km)", True))
def test_spacing_26(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100,0km/s", r"(?<=100,0)(?=km)", True))
def test_spacing_27(input, expected):
    assert spacing(input) == expected


# simple units with decimal point but without decimal place


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.m xxx", r"(?<=100\.)(?=m)", False))
def test_spacing_28(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.km xxx", r"(?<=100\.)(?=km)", False))
def test_spacing_29(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.km/s xxx", r"(?<=100\.)(?=km)", False))
def test_spacing_30(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.km\u00B7s/ft", r"(?<=100\.)(?=km)", False))
def test_spacing_31(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.km\u00B7s", r"(?<=100\.)(?=km)", False))
def test_spacing_32(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.km/s/ft", r"(?<=100\.)(?=km)", False))
def test_spacing_33(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.km/s", r"(?<=100\.)(?=km)", False))
def test_spacing_34(input, expected):
    assert spacing(input) == expected


# simple units with decimal point

@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0m xxx", r"(?<=100\.0)(?=m)", True))
def test_spacing_35(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0km xxx", r"(?<=100\.0)(?=km)", True))
def test_spacing_36(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0km/s xxx", r"(?<=100\.0)(?=km)", True))
def test_spacing_37(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0km\u00B7s/ft", r"(?<=100\.0)(?=km)", True))
def test_spacing_38(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0km\u00B7s", r"(?<=100\.0)(?=km)", True))
def test_spacing_39(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0km/s/ft", r"(?<=100\.0)(?=km)", True))
def test_spacing_40(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0km/s", r"(?<=100\.0)(?=km)", True))
def test_spacing_41(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0Ah/s", r"(?<=100\.0)(?=Ah)", True))
def test_spacing_42(input, expected):
    assert spacing(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    _generate_spacing_variants("xxx 100.0hW/s", r"(?<=100\.0)(?=hW)", True))
def test_spacing_43(input, expected):
    assert spacing(input) == expected
