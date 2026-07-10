# STDF Parser

A Python library for parsing and writing STDF (Standard Test Data Format) files, commonly used in semiconductor testing and manufacturing.

## Features

- **High-level API**: Parse an entire STDF file into a single structured object with one call
- **Low-level API**: Stream individual records for memory-efficient processing of large files
- **Write support**: Create STDF files programmatically
- **Multi-site aware**: Correctly handles simultaneous multi-site test data
- **NumPy integration**: Efficient array operations for MPR pin-level data

## Installation

```bash
git clone <repository-url>
cd stdf_parser
pip install .
```

## Requirements

- Python >= 3.8
- NumPy >= 1.21

## Quick Start

### High-level: parse an entire file

```python
from stdf_parser import parse

data = parse("myfile.stdf")

# Lot information (from MIR record)
print(data.lot_info["LOT_ID"])
print(data.lot_info["PART_TYP"])

# Per-unit results
for unit in data.units:
    print(unit["PART_ID"], "bin:", unit["HARD_BIN"])

# Test limits and metadata
for key, meta in data.tests.items():
    print(f"{meta.test_txt}: {meta.lo_limit} – {meta.hi_limit} {meta.units}")

# Bin summaries
for bin_num, hbin in data.hbin.items():
    print(f"HBin {bin_num}: {hbin.HBIN_CNT} units")
```

### Mid-level: stream records one by one

```python
from stdf_parser import RECFuncs, PTRRecord

with open("myfile.stdf", "rb") as f:
    while True:
        pos, rec = RECFuncs.RecordSelect(f)
        if rec is None:
            break
        if isinstance(rec, PTRRecord):
            print(rec.TEST_NUM, rec.TEST_TXT, rec.RESULT)
```

### Writing an STDF file

```python
from stdf_parser import Writer

w = Writer("output.stdf")
w.write_FAR({"CPU_TYPE": 2, "STDF_VER": 4})
w.write_MIR({"LOT_ID": "LOT001", "PART_TYP": "MyChip", "NODE_NAM": "Tester1"})
w.write_PIR({"HEAD_NUM": 1, "SITE_NUM": 1})
w.write_PTR({
    "TEST_NUM": 1000, "HEAD_NUM": 1, "SITE_NUM": 1,
    "TEST_TXT": "VDD_current", "RESULT": 0.0042,
    "LO_LIMIT": 0.001, "HI_LIMIT": 0.010, "UNITS": "A",
})
w.write_PRR({"HEAD_NUM": 1, "SITE_NUM": 1, "HARD_BIN": 1, "SOFT_BIN": 1, "NUM_TEST": 1})
w.write_MRR({"FINISH_T": 0})
w.save()
```

## StdfData reference

| Attribute | Type | Contents |
|-----------|------|----------|
| `lot_info` | `dict` | All MIR fields (LOT_ID, PART_TYP, NODE_NAM, …) |
| `finish_info` | `dict` | All MRR fields (FINISH_T, DISP_COD, …) |
| `wafers` | `list[dict]` | One dict per WIR/WRR pair |
| `units` | `list[dict]` | One dict per device; keys include PART_ID, HARD_BIN, SOFT_BIN, X_COORD, Y_COORD, and one key per test result |
| `tests` | `dict` | `(TEST_NUM, TEST_TXT) → TestMeta` with limits, units, scale |
| `hbin` | `dict` | `HBIN_NUM → HBRRecord` |
| `sbin` | `dict` | `SBIN_NUM → SBRRecord` |
| `tsr` | `list` | TSR summary records |

Test results in `units` are keyed by `(TEST_NUM, TEST_TXT)` and already have `RES_SCAL` applied. Limits in `TestMeta` are also pre-scaled. Missing limits are `float("nan")`.

## Project Structure

```
stdf_parser/
├── parse.py          # High-level parse() API
├── RECFuncs.py       # Mid-level record streaming
├── ByteFuncs.py      # Low-level byte read/write functions
├── RECRecipes.py     # Record format specifications
├── RecordTuples.py   # NamedTuple definitions for all record types
├── STDFWriter.py     # STDF file writer
└── Debugger.py       # Debugging utilities
```

## Development

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows
pip install -e ".[dev]"
pytest
```

## License

MIT License

## Version

0.1.12
