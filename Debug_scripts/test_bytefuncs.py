"""
Round-trip tests: verify that every write_* function produces bytes that
the corresponding get_* function can read back correctly.
"""
import io
import math
import pytest

from stdf_parser.ByteFuncs import (
    get_r, get_r_arr,
    get_u, get_u_arr,
    get_i,
    get_cn, get_cn_arr,
    get_c,
    get_b,
    get_bn,
    get_dn,
    write_r, write_r_arr,
    write_u, write_u_arr,
    write_i,
    write_cn, write_cn_arr,
    write_c,
    write_b,
    write_bn,
    write_dn,
)


def reader(data: bytes) -> io.BytesIO:
    """Wrap raw bytes in a file-like object for the get_* functions."""
    return io.BytesIO(data)


# ── R*4 / R*8 ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("value", [0.0, 1.0, -1.5, 3.14159, 1e10, -1e-5])
def test_r4_roundtrip(value):
    result = get_r(4, reader(write_r(4, value)))
    assert math.isclose(result, value, rel_tol=1e-6), f"R*4: {value!r} → {result!r}"


@pytest.mark.parametrize("value", [0.0, 1.0, -1.5, 3.14159265358979, 1e100, -1e-100])
def test_r8_roundtrip(value):
    result = get_r(8, reader(write_r(8, value)))
    assert math.isclose(result, value, rel_tol=1e-15), f"R*8: {value!r} → {result!r}"


def test_r_arr_r4_roundtrip():
    values = [1.0, 2.5, -3.14, 0.0]
    result = get_r_arr(4, len(values), reader(write_r_arr(4, values)))
    for orig, got in zip(values, result):
        assert math.isclose(got, orig, rel_tol=1e-6), f"kxR*4: {orig!r} → {got!r}"


def test_r_arr_r8_roundtrip():
    values = [1.0, -2.5, 1e50]
    result = get_r_arr(8, len(values), reader(write_r_arr(8, values)))
    for orig, got in zip(values, result):
        assert math.isclose(got, orig, rel_tol=1e-15), f"kxR*8: {orig!r} → {got!r}"


# ── U*1 / U*2 / U*4 ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("val, value", [
    (1, 0), (1, 1), (1, 127), (1, 255),
    (2, 0), (2, 1000), (2, 65535),
    (4, 0), (4, 123456), (4, 0xFFFFFFFF),
])
def test_u_roundtrip(val, value):
    result = get_u(val, reader(write_u(val, value)))
    assert result == value, f"U*{val*8}: {value!r} → {result!r}"


def test_u_arr_roundtrip():
    values = [0, 1, 1000, 65535]
    result = get_u_arr(2, len(values), reader(write_u_arr(2, values)))
    assert result == values


# ── I*1 / I*2 / I*4 ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("val, value", [
    (1,  0),  (1,  127),  (1, -128),
    (2,  0),  (2,  32767), (2, -32768),
    (4,  0),  (4,  2147483647), (4, -2147483648), (4, -1),
])
def test_i_roundtrip(val, value):
    result = get_i(val, reader(write_i(val, value)))
    assert result == value, f"I*{val*8}: {value!r} → {result!r}"


# ── C*n (variable-length string) ─────────────────────────────────────────────

@pytest.mark.parametrize("value", ["", "A", "hello", "test string 123", "x" * 255])
def test_cn_roundtrip(value):
    result = get_cn(reader(write_cn(value)))
    assert result == value, f"C*n: {value!r} → {result!r}"


def test_cn_arr_roundtrip():
    values = ["abc", "def", "xyz", ""]
    result = get_cn_arr(len(values), reader(write_cn_arr(values)))
    assert result == values


# ── C*f (fixed-length string, left-justified, space-padded) ──────────────────

@pytest.mark.parametrize("val, value, expected", [
    (12, "hello",        "hello       "),
    (12, "hello world!", "hello world!"),
    (12, "",             " " * 12),
    ( 6, "ABC",          "ABC   "),
    ( 4, "TOOLONG",      "TOOL"),   # truncated to val bytes
])
def test_c_roundtrip(val, value, expected):
    result = get_c(val, reader(write_c(val, value)))
    assert result == expected, f"C*{val}: {value!r} → {result!r}"


# ── B*n (variable-length binary) ─────────────────────────────────────────────

@pytest.mark.parametrize("value", [b'', b'\x00', b'\xAB\xCD\xEF', bytes(range(10))])
def test_bn_roundtrip(value):
    result = get_bn(reader(write_bn(value)))
    assert result == value, f"B*n: {value!r} → {result!r}"


# ── B*6 (fixed-length binary) ────────────────────────────────────────────────

@pytest.mark.parametrize("val, value", [
    (6, b'\x01\x02\x03\x04\x05\x06'),
    (6, b'\xFF' * 6),
    (6, b'\x00' * 6),
    (6, b'\xAB'),               # shorter → zero-padded to 6 bytes
])
def test_b_roundtrip(val, value):
    expected = bytes(value)[:val] + b'\x00' * (val - len(value))
    result = get_b(val, reader(write_b(val, value)))
    assert result == expected, f"B*{val}: {value!r} → {result!r}"


# ── D*n (variable-length bit field) ──────────────────────────────────────────

@pytest.mark.parametrize("value, bit_count", [
    (b'\xFF',             8),
    (b'\xAB\xCD',        16),
    (b'\x01\x02\x03',    24),
    (b'\xAB\xCD',       None),   # defaults to len(value) * 8
])
def test_dn_roundtrip(value, bit_count):
    result = get_dn(reader(write_dn(value, bit_count)))
    assert result == value, f"D*n: {value!r} bit_count={bit_count} → {result!r}"
