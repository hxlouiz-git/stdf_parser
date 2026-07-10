# stdf_parser — Reference

Version **0.1.12** · Python ≥ 3.8 · Dependency: numpy ≥ 1.21

---

## Table of Contents

1. [Package Layout](#package-layout)
2. [Quick Start — Reading](#quick-start--reading)
3. [Quick Start — Writing](#quick-start--writing)
4. [High-Level API: `stdf_parse.parse()`](#high-level-api-stdf_parseparse)
   - [StdfData](#stdfdata)
   - [TestMeta](#testmeta)
   - [Unit dict keys](#unit-dict-keys)
5. [Low-Level API: `RECFuncs`](#low-level-api-recfuncs)
   - [RecordSelect](#recordselect)
   - [RecordContainer](#recordcontainer)
   - [Parser functions](#parser-functions)
   - [Dispatch table](#dispatch-table)
6. [Record Types (NamedTuples)](#record-types-namedtuples)
   - [File-level records](#file-level-records)
   - [Lot-level records](#lot-level-records)
   - [Wafer-level records](#wafer-level-records)
   - [Part-level records](#part-level-records)
   - [Test records](#test-records)
   - [Summary records](#summary-records)
   - [Miscellaneous records](#miscellaneous-records)
7. [Writing STDF: `STDFWriter` & Recipes](#writing-stdf-stdfwriter--recipes)
   - [Writer class](#writer-class)
   - [Using Recipe classes directly](#using-recipe-classes-directly)
   - [Recipe field reference](#recipe-field-reference)
8. [Binary Codec: `ByteFuncs`](#binary-codec-bytefuncs)
   - [Read functions](#read-functions)
   - [Write functions](#write-functions)
9. [Exceptions](#exceptions)
10. [STDF Type → Python Type mapping](#stdf-type--python-type-mapping)
11. [Known Limitations & Notes](#known-limitations--notes)

---

## Package Layout

```
stdf_parser/
├── __init__.py        # imports all submodules
├── ByteFuncs.py       # binary read/write primitives
├── RECFuncs.py        # record parsers + RecordSelect loop
├── RecordTuples.py    # NamedTuple definitions for every record type
├── RECRecipes.py      # record encoders (write side)
└── STDFWriter.py      # high-level Writer class

stdf_parse.py          # standalone high-level parser (not part of installed package)
```

Import the installed package:

```python
import stdf_parser                   # exposes submodules as stdf_parser.RECFuncs etc.
from stdf_parser import RECFuncs, RecordTuples, ByteFuncs, RECRecipes, STDFWriter
```

Import the high-level helper (from the repo root, not installed):

```python
import stdf_parse                    # parse() lives here
```

---

## Quick Start — Reading

### High-level (recommended)

```python
import stdf_parse

data = stdf_parse.parse("myfile.stdf")

# Lot info from MIR
print(data.lot_info["LOT_ID"], data.lot_info["PART_TYP"])

# Iterate parts
for unit in data.units:
    print(unit["PART_ID"], unit["SOFT_BIN"], unit["HARD_BIN"])
    # Access a test result by (TEST_NUM, TEST_TXT) key
    val = unit.get((1000, "Vdd_current"))
    print(val)

# Bin summaries
for hbin_num, hbr in data.hbin.items():
    print(hbin_num, hbr.HBIN_NAM, hbr.HBIN_CNT)
```

### Low-level (record-by-record)

```python
from stdf_parser import RECFuncs, RecordTuples

with open("myfile.stdf", "rb") as f:
    while True:
        pos = f.tell()
        chunk = f.read(4)
        if len(chunk) < 4:
            break
        header = RECFuncs.get_headers(chunk, 4)
        body = f.read(header.REC_LEN)
        record = RECFuncs.RecordSelect.__wrapped__(f)   # or use the loop below

# Easier: use RecordSelect directly
with open("myfile.stdf", "rb") as f:
    while True:
        pos, record = RECFuncs.RecordSelect(f)
        if record is None:
            break
        if isinstance(record, RecordTuples.PTRRecord):
            print(record.TEST_NUM, record.RESULT)
```

---

## Quick Start — Writing

```python
from stdf_parser.STDFWriter import Writer
import time

w = Writer("output.stdf")

w.write_FAR({"CPU_TYPE": 2, "STDF_VER": 4})
w.write_MIR({
    "SETUP_T": int(time.time()),
    "START_T": int(time.time()),
    "STAT_NUM": 1,
    "MODE_COD": "P",
    "RTST_COD": " ",
    "PROT_COD": " ",
    "BURN_TIM": 65535,
    "CMOD_COD": " ",
    "LOT_ID":   "LOT001",
    "PART_TYP": "MY_DEVICE",
})

for part_id in range(10):
    w.write_PIR({"HEAD_NUM": 1, "SITE_NUM": 0})
    w.write_PTR({
        "TEST_NUM": 1000,
        "HEAD_NUM": 1,
        "SITE_NUM": 0,
        "TEST_FLG": b"\x00",
        "PARM_FLG": b"\x00",
        "RESULT":   3.14,
        "TEST_TXT": "Vdd_current",
        "UNITS":    "mA",
        "LO_LIMIT": 2.0,
        "HI_LIMIT": 5.0,
    })
    w.write_PRR({
        "HEAD_NUM": 1,
        "SITE_NUM": 0,
        "PART_FLG": b"\x00",
        "NUM_TEST": 1,
        "HARD_BIN": 1,
        "SOFT_BIN": 1,
        "X_COORD":  0,
        "Y_COORD":  part_id,
        "TEST_T":   100,
        "PART_ID":  str(part_id),
    })

w.write_MRR({"FINISH_T": int(time.time())})
w.save()
```

---

## High-Level API: `stdf_parse.parse()`

```python
def parse(path: str) -> StdfData
```

Reads the entire STDF file into memory, locates the FAR record (searches for the byte sequence `b'\x00\x0a'`, falls back to `b'\x05\x0a'`), then streams through all records building a structured result.

Multi-site files are handled correctly: in-progress units are buffered per `(HEAD_NUM, SITE_NUM)` key so simultaneous plunges on different sites stay isolated.

### StdfData

```python
@dataclass
class StdfData:
    lot_info:    dict           # MIR fields as a plain dict
    finish_info: dict           # MRR fields as a plain dict
    wafers:      list[dict]     # one dict per WIR/WRR pair
    units:       list[dict]     # one dict per PIR/PRR pair (includes test results)
    tests:       dict           # (TEST_NUM, TEST_TXT) -> TestMeta
    tsr:         list           # list of TSRRecord
    sbin:        dict           # SBIN_NUM (int) -> SBRRecord
    hbin:        dict           # HBIN_NUM (int) -> HBRRecord
```

#### `lot_info` keys (from MIR)

All MIR field names in upper-case: `LOT_ID`, `PART_TYP`, `START_T`, `SETUP_T`, `NODE_NAM`, `TSTR_TYP`, `JOB_NAM`, `JOB_REV`, `OPER_NAM`, `EXEC_TYP`, `EXEC_VER`, `TEST_COD`, `TST_TEMP`, `FAMILY_ID`, `PROC_ID`, `SPEC_NAM`, `SPEC_VER`, `FLOW_ID`, `SETUP_ID`, `DSGN_REV`, etc.

#### `finish_info` keys (from MRR)

`FINISH_T`, `DISP_COD`, `USR_DESC`, `EXC_DESC`

#### `wafers` entries

Each dict has keys from WIR + WRR: `HEAD_NUM`, `SITE_GRP`, `START_T`, `WAFER_ID`, `FINISH_T`, `PART_CNT`, `RTST_CNT`, `ABRT_CNT`, `GOOD_CNT`, `FUNC_CNT`, `FABWF_ID`, `FRAME_ID`, `MASK_ID`, `USR_DESC`, `EXC_DESC`

### Unit dict keys

Each entry in `StdfData.units` is a dict with:

| Key | Type | Source | Description |
|---|---|---|---|
| `HEAD_NUM` | int | PRR | test head number |
| `SITE_NUM` | int | PRR | test site number |
| `WAFER_ID` | str | WIR | wafer ID (empty for non-wafer tests) |
| `PART_ID` | str | PRR | part / serial number |
| `SOFT_BIN` | int | PRR | software bin number |
| `HARD_BIN` | int | PRR | hardware bin number |
| `X_COORD` | int | PRR | die X coordinate |
| `Y_COORD` | int | PRR | die Y coordinate |
| `TEST_T` | float | PRR | test time in seconds |
| `NUM_TEST` | int | PRR | number of tests executed |
| `(TEST_NUM, TEST_TXT)` | float / list / int | PTR/MPR/FTR | per-test result (see below) |

Test result values by record type:

- **PTR** → `float` — scaled result: `RESULT × 10^RES_SCAL`
- **MPR** → `list[float]` — one scaled float per return pin
- **FTR** → `int` — `1` = pass, `0` = fail

### TestMeta

Populated from the first occurrence of each PTR/MPR for a test (subsequent records are usually truncated and carry no metadata).

```python
@dataclass
class TestMeta:
    test_num:  int
    test_txt:  str
    units:     str   = ""
    lo_limit:  float = float("nan")  # already scaled by RES_SCAL
    hi_limit:  float = float("nan")  # already scaled by RES_SCAL
    res_scal:  int   = 0
```

Access via:
```python
meta = data.tests[(1000, "Vdd_current")]
print(meta.units, meta.lo_limit, meta.hi_limit)
```

---

## Low-Level API: `RECFuncs`

### RecordSelect

```python
def RecordSelect(f) -> tuple[int, NamedTuple | None]
```

Reads **one** record from an open binary file `f`.

- Reads 4-byte header → dispatches on `(REC_TYP, REC_SUB)`
- Returns `(file_position_before_read, parsed_record)`
- Unknown record types return `NULREcord`
- Returns `(pos, None)` at end-of-file

```python
with open("file.stdf", "rb") as f:
    while True:
        pos, rec = RECFuncs.RecordSelect(f)
        if rec is None:
            break
        print(type(rec).__name__, rec)
```

### RecordContainer

Internal wrapper used by all parser functions. You rarely need this directly, but it is useful for writing custom parsers.

```python
class RecordContainer:
    def __init__(self, contents: bytes, length: int)
    def read(self, size: int) -> bytes      # raises RecordTruncated if overrun
    def length_check(self, size: int) -> bool
    def move(self, size: int)               # skip bytes
    def move_n(self)                        # skip a C*n field
```

### Parser functions

All parsers share the same external signature after decoration:

```python
PARSER(contents: bytes, length: int) -> NamedTuple
```

| Function | Returns | REC_TYP | REC_SUB |
|---|---|---|---|
| `ATR` | `ATRRecord` | 0 | 20 |
| `BPS` | `BPSRecord` | 20 | 10 |
| `DTR` | `DTRRecord` | 50 | 30 |
| `EPS` | `None` | 20 | 20 |
| `FAR` | `FARRecord` | 0 | 10 |
| `FTR` | `FTRRecord` | 15 | 20 |
| `GDR` | `None` (stub) | 50 | 10 |
| `HBR` | `HBRRecord` | 1 | 40 |
| `MIR` | `MIRRecord` | 1 | 10 |
| `MPR` | `MPRRecord` | 15 | 15 |
| `MRR` | `MRRRecord` | 1 | 20 |
| `NULLREC` | `NULREcord` | — | — |
| `PCR` | `PCRRecord` | 1 | 30 |
| `PGR` | `PGRRecord` | 1 | 62 |
| `PIR` | `PIRRecord` | 5 | 10 |
| `PLR` | `PLRRecord` | 1 | 63 |
| `PMR` | `PMRRecord` | 1 | 60 |
| `PRR` | `PRRRecord` | 5 | 20 |
| `PTR` | `PTRRecord` | 15 | 10 |
| `RDR` | `RDRRecord` | 1 | 70 |
| `SBR` | `SBRRecord` | 1 | 50 |
| `SDR` | `SDRRecord` | 1 | 80 |
| `TSR` | `TSRRecord` | 10 | 30 |
| `WCR` | `WCRRecord` | 2 | 30 |
| `WIR` | `WIRRecord` | 2 | 10 |
| `WRR` | `WRRRecord` | 2 | 20 |

### Dispatch table

```python
from stdf_parser.RECFuncs import _DISPATCH
# _DISPATCH[(REC_TYP, REC_SUB)] -> parser function
```

---

## Record Types (NamedTuples)

All types live in `stdf_parser.RecordTuples`. Fields with default values are optional in STDF (may be absent in truncated records — the parser returns the default in that case).

### File-level records

#### `FARRecord` — File Attributes Record `(0, 10)`

| Field | Type | Description |
|---|---|---|
| `CPU_TYPE` | int | CPU type (2 = little-endian x86) |
| `STDF_VER` | int | STDF version (4) |

#### `ATRRecord` — Audit Trail Record `(0, 20)`

| Field | Type | Default | Description |
|---|---|---|---|
| `MOD_TIM` | int | — | modification time (Unix timestamp) |
| `CMD_LINE` | str | `''` | command line that modified the file |

### Lot-level records

#### `MIRRecord` — Master Information Record `(1, 10)`

| Field | Type | Default | Description |
|---|---|---|---|
| `SETUP_T` | datetime | — | setup time |
| `START_T` | datetime | — | lot start time |
| `STAT_NUM` | int | — | tester station number |
| `MODE_COD` | str | — | test mode (`P`=production, `E`=engineering, …) |
| `RTST_COD` | str | — | lot retest code |
| `PROT_COD` | str | — | data protection code |
| `BURN_TIM` | int | — | burn-in time (minutes) |
| `CMOD_COD` | str | — | command mode code |
| `LOT_ID` | str | — | lot ID |
| `PART_TYP` | str | — | device type / part number |
| `NODE_NAM` | str | `''` | tester node name |
| `TSTR_TYP` | str | `''` | tester type |
| `JOB_NAM` | str | `''` | job / test program name |
| `JOB_REV` | str | `''` | job revision |
| `SBLOT_ID` | str | `''` | sublot ID |
| `OPER_NAM` | str | `''` | operator name |
| `EXEC_TYP` | str | `''` | executive software type |
| `EXEC_VER` | str | `''` | executive software version |
| `TEST_COD` | str | `''` | test phase code |
| `TST_TEMP` | str | `''` | test temperature |
| `USER_TXT` | str | `''` | user text |
| `AUX_FILE` | str | `''` | auxiliary data file |
| `PKG_TYP` | str | `''` | package type |
| `FAMILY_ID` | str | `''` | device family ID |
| `DATE_COD` | str | `''` | date code |
| `FACIL_ID` | str | `''` | facility ID |
| `FLOOR_ID` | str | `''` | test floor ID |
| `PROC_ID` | str | `''` | process ID |
| `OPER_FRQ` | str | `''` | operation frequency |
| `SPEC_NAM` | str | `''` | test specification name |
| `SPEC_VER` | str | `''` | test specification version |
| `FLOW_ID` | str | `''` | test flow ID |
| `SETUP_ID` | str | `''` | setup ID |
| `DSGN_REV` | str | `''` | design revision |
| `ENG_ID` | str | `''` | engineering lot ID |
| `ROM_COD` | str | `''` | ROM code ID |
| `SERL_NUM` | str | `''` | tester serial number |
| `SUPR_NAM` | str | `''` | supervisor name |

#### `MRRRecord` — Master Results Record `(1, 20)`

| Field | Type | Default | Description |
|---|---|---|---|
| `FINISH_T` | datetime | — | lot finish time |
| `DISP_COD` | str | `' '` | lot disposition code |
| `USR_DESC` | str | `''` | user description |
| `EXC_DESC` | str | `''` | executive description |

#### `PCRRecord` — Part Count Record `(1, 30)`

| Field | Type | Default | Description |
|---|---|---|---|
| `HEAD_NUM` | int | — | head number (255 = all heads) |
| `SITE_NUM` | int | — | site number (255 = all sites) |
| `PART_CNT` | int | — | total parts tested |
| `RTST_CNT` | int | `0` | retested parts |
| `ABRT_CNT` | int | `0` | aborted parts |
| `GOOD_CNT` | int | `0` | good (passing) parts |
| `FUNC_CNT` | int | `0` | functional parts |

#### `SDRRecord` — Site Description Record `(1, 80)`

| Field | Type | Default | Description |
|---|---|---|---|
| `HEAD_NUM` | int | — | head number |
| `SITE_GRP` | int | — | site group number |
| `SITE_CNT` | int | — | number of test sites |
| `SITE_NUM` | list[int] | — | site numbers (length = SITE_CNT) |
| `HAND_TYP` | str | `''` | handler/prober type |
| `HAND_ID` | str | `''` | handler/prober ID |
| `CARD_TYP` | str | `''` | probe card type |
| `CARD_ID` | str | `''` | probe card ID |
| `LOAD_TYP` | str | `''` | load board type |
| `LOAD_ID` | str | `''` | load board ID |
| `DIB_TYP` | str | `''` | DIB board type |
| `DIB_ID` | str | `''` | DIB board ID |
| `CABL_TYP` | str | `''` | interface cable type |
| `CABL_ID` | str | `''` | interface cable ID |
| `CONT_TYP` | str | `''` | contactor type |
| `CONT_ID` | str | `''` | contactor ID |
| `LASR_TYP` | str | `''` | laser type |
| `LASR_ID` | str | `''` | laser ID |
| `EXTR_TYP` | str | `''` | extra equipment type |
| `EXTR_ID` | str | `''` | extra equipment ID |

### Wafer-level records

#### `WCRRecord` — Wafer Configuration Record `(2, 30)`

| Field | Type | Default | Description |
|---|---|---|---|
| `WAFR_SIZ` | float | nan | wafer size (mm) |
| `DIE_HT` | float | nan | die height |
| `DIE_WID` | float | nan | die width |
| `WF_UNITS` | int | `0` | units (1=in, 2=cm, 3=mm, 4=mils) |
| `WF_FLAT` | str | `' '` | wafer flat orientation (`U`,`D`,`L`,`R`) |
| `CENTER_X` | int | `0` | X coordinate of center die |
| `CENTER_Y` | int | `0` | Y coordinate of center die |
| `POS_X` | str | `' '` | positive X direction (`L` or `R`) |
| `POS_Y` | str | `' '` | positive Y direction (`U` or `D`) |

#### `WIRRecord` — Wafer Information Record `(2, 10)`

| Field | Type | Default | Description |
|---|---|---|---|
| `HEAD_NUM` | int | — | head number |
| `SITE_GRP` | int | — | site group number |
| `START_T` | int | — | wafer start time (Unix timestamp) |
| `WAFER_ID` | str | `''` | wafer ID |

#### `WRRRecord` — Wafer Results Record `(2, 20)`

| Field | Type | Default | Description |
|---|---|---|---|
| `HEAD_NUM` | int | — | head number |
| `SITE_GRP` | int | — | site group number |
| `FINISH_T` | int | — | wafer finish time (Unix timestamp) |
| `PART_CNT` | int | — | parts tested on wafer |
| `RTST_CNT` | int | `0` | retested parts |
| `ABRT_CNT` | int | `0` | aborted parts |
| `GOOD_CNT` | int | `0` | good parts |
| `FUNC_CNT` | int | `0` | functional parts |
| `WAFER_ID` | str | `''` | wafer ID |
| `FABWF_ID` | str | `''` | fab wafer ID |
| `FRAME_ID` | str | `''` | wafer frame ID |
| `MASK_ID` | str | `''` | wafer mask ID |
| `USR_DESC` | str | `''` | user description |
| `EXC_DESC` | str | `''` | executive description |

### Part-level records

#### `PIRRecord` — Part Information Record `(5, 10)`

| Field | Type | Description |
|---|---|---|
| `HEAD_NUM` | int | head number |
| `SITE_NUM` | int | site number |

#### `PRRRecord` — Part Results Record `(5, 20)`

| Field | Type | Default | Description |
|---|---|---|---|
| `HEAD_NUM` | int | — | head number |
| `SITE_NUM` | int | — | site number |
| `PART_FLG` | bytes | — | part flags (bit 3 = part failed) |
| `NUM_TEST` | int | — | number of tests executed |
| `HARD_BIN` | int | — | hardware bin number |
| `SOFT_BIN` | int | — | software bin number |
| `X_COORD` | int | — | die X coordinate |
| `Y_COORD` | int | — | die Y coordinate |
| `TEST_T` | float | — | test time in **seconds** (raw value / 1000) |
| `PART_ID` | str | — | part / serial number |
| `PART_TXT` | str | `''` | part description |
| `PART_FIX` | str | `''` | part fixturing data |

### Test records

#### `PTRRecord` — Parametric Test Record `(15, 10)`

| Field | Type | Default | Description |
|---|---|---|---|
| `TEST_NUM` | int | — | test number |
| `HEAD_NUM` | int | — | head number |
| `SITE_NUM` | int | — | site number |
| `TEST_FLG` | bytes | — | test flags (bit 7: 0=pass, 1=fail) |
| `PARM_FLG` | bytes | — | parametric flags |
| `RESULT` | float | — | measured result (raw, not scaled) |
| `TEST_TXT` | str | `''` | test name / description |
| `ALARM_ID` | str | `''` | alarm ID |
| `OPT_FLAG` | bytes | `None` | optional data flag |
| `RES_SCAL` | int | `0` | result scale exponent (×10^n) |
| `LLM_SCAL` | int | `0` | low limit scale exponent |
| `HLM_SCAL` | int | `0` | high limit scale exponent |
| `LO_LIMIT` | float | nan | low test limit (nan if OPT_FLAG bit 6 set) |
| `HI_LIMIT` | float | nan | high test limit (nan if OPT_FLAG bit 7 set) |
| `UNITS` | str | `''` | result units |
| `C_RESFMT` | str | `''` | result printf format |
| `C_LLMFMT` | str | `''` | low limit printf format |
| `C_HLMFMT` | str | `''` | high limit printf format |
| `LO_SPEC` | float | nan | low specification limit |
| `HI_SPEC` | float | nan | high specification limit |

> **Scaling:** `actual_value = RESULT × 10^RES_SCAL`. The high-level `parse()` applies this automatically. When using the low-level API you must scale manually.

#### `MPRRecord` — Multiple-Result Parametric Record `(15, 15)`

| Field | Type | Default | Description |
|---|---|---|---|
| `TEST_NUM` | int | — | test number |
| `HEAD_NUM` | int | — | head number |
| `SITE_NUM` | int | — | site number |
| `TEST_FLG` | bytes | — | test flags |
| `PARM_FLG` | bytes | — | parametric flags |
| `RTN_ICNT` | int | — | number of return state entries |
| `RSLT_CNT` | int | — | number of result values |
| `RTN_STAT` | list[int] | `None` | per-pin return states (length RTN_ICNT) |
| `RTN_RSLT` | list[float] | `None` | per-pin results (length RSLT_CNT) |
| `TEST_TXT` | str | `''` | test name |
| `ALARM_ID` | str | `''` | alarm ID |
| `OPT_FLAG` | bytes | `None` | optional data flag |
| `RES_SCAL` | int | `0` | result scale exponent |
| `LLM_SCAL` | int | `0` | low limit scale exponent |
| `HLM_SCAL` | int | `0` | high limit scale exponent |
| `LO_LIMIT` | float | nan | low test limit |
| `HI_LIMIT` | float | nan | high test limit |
| `START_IN` | float | nan | starting input value |
| `INCR_IN` | float | nan` | input increment |
| `RTN_INDX` | list[int] | `None` | pin index array |
| `UNITS` | str | `''` | result units |
| `UNITS_IN` | str | `''` | input units |
| `C_RESFMT` | str | `''` | result printf format |
| `C_LLMFMT` | str | `''` | low limit printf format |
| `C_HLMFMT` | str | `''` | high limit printf format |
| `LO_SPEC` | float | nan | low specification limit |
| `HI_SPEC` | float | nan | high specification limit |

#### `FTRRecord` — Functional Test Record `(15, 20)`

| Field | Type | Default | Description |
|---|---|---|---|
| `TEST_NUM` | int | — | test number |
| `HEAD_NUM` | int | — | head number |
| `SITE_NUM` | int | — | site number |
| `TEST_FLG` | int | — | test flags |
| `OPT_FLG` | bytes | `b'\x00'` | optional flags |
| `CYCL_CNT` | int | `0` | cycle count |
| `REL_VADR` | int | `0` | relative vector address of first failure |
| `REPT_CNT` | int | `0` | repeat count of the failing vector |
| `NUM_FAIL` | int | `0` | number of pins with at least one failure |
| `XFAIL_AD` | int | `0` | X logical device failure address |
| `YFAIL_AD` | int | `0` | Y logical device failure address |
| `VECT_OFF` | int | `0` | vector offset |
| `RTN_ICNT` | int | `0` | count of return states |
| `PGM_ICNT` | int | `0` | count of programmed states |
| `RTN_INDX` | int | `0` | return state indexes |
| `RTN_STAT` | int | `0` | returned states |
| `PGM_INDX` | int | `0` | programmed state indexes |
| `PGM_STAT` | int | `0` | programmed states |
| `FAIL_PIN` | bytes | `b''` | failing pin bit field |
| `VECT_NAME` | str | `''` | vector name |
| `TIME_SET` | str | `''` | timing set name |
| `OP_CODE` | str | `''` | vector op code |
| `TEST_TXT` | str | `''` | test name |
| `ALARM_ID` | str | `''` | alarm ID |
| `PROG_TXT` | str | `''` | additional programmed information |
| `RSLT_TXT` | str | `''` | additional result information |
| `PATG_NUM` | int | `0` | pattern generator number |
| `SPIN_MAP` | str | `''` | bit map of enabled comparators |
| `RESULT` | int | `0` | **derived**: `1`=pass, `0`=fail (from `TEST_FLG` bit 7) |

### Summary records

#### `HBRRecord` — Hard Bin Record `(1, 40)`

| Field | Type | Default | Description |
|---|---|---|---|
| `HEAD_NUM` | int | — | head number (255 = all) |
| `SITE_NUM` | int | — | site number (255 = all) |
| `HBIN_NUM` | int | — | hardware bin number |
| `HBIN_CNT` | int | — | bin count |
| `HBIN_PF` | str | `' '` | pass/fail (`P` or `F`) |
| `HBIN_NAM` | str | `''` | bin name |

#### `SBRRecord` — Soft Bin Record `(1, 50)`

| Field | Type | Default | Description |
|---|---|---|---|
| `HEAD_NUM` | int | — | head number (255 = all) |
| `SITE_NUM` | int | — | site number (255 = all) |
| `SBIN_NUM` | int | — | software bin number |
| `SBIN_CNT` | int | — | bin count |
| `SBIN_PF` | str | `' '` | pass/fail (`P` or `F`) |
| `SBIN_NAM` | str | `''` | bin name |

#### `TSRRecord` — Test Synopsis Record `(10, 30)`

| Field | Type | Default | Description |
|---|---|---|---|
| `HEAD_NUM` | int | — | head number |
| `SITE_NUM` | int | — | site number |
| `TEST_TYP` | str | — | test type (`P`=parametric, `F`=functional, `M`=multi-result) |
| `TEST_NUM` | int | — | test number |
| `EXEC_CNT` | int | `0` | number of executions |
| `FAIL_CNT` | int | `0` | number of failures |
| `ALRM_CNT` | int | `0` | number of alarms |
| `TEST_NAM` | str | `''` | test name |
| `SEQ_NAME` | str | `''` | sequence name |
| `TEST_LBL` | str | `''` | test label |
| `OPT_FLAG` | bytes | `None` | optional data flags |
| `TEST_TIM` | float | nan | average test time (seconds) |
| `TEST_MIN` | float | nan | minimum result |
| `TEST_MAX` | float | nan | maximum result |
| `TST_SUMS` | float | nan | sum of results |
| `TST_SQRS` | float | nan | sum of squares of results |

### Miscellaneous records

#### `HeaderRecord`

```python
HeaderRecord(REC_LEN: int, REC_TYP: int, REC_SUB: int)
```
Returned by `get_headers()`. `REC_LEN` is the body length (excludes the 4-byte header).

#### `PIRRecord` — Part Information Record `(5, 10)`

| Field | Type | Description |
|---|---|---|
| `HEAD_NUM` | int | head number |
| `SITE_NUM` | int | site number |

#### `PMRRecord` — Pin Map Record `(1, 60)`

| Field | Type | Default | Description |
|---|---|---|---|
| `PMR_INDX` | int | — | pin map index |
| `CHAN_TYP` | int | `0` | channel type |
| `CHAN_NAM` | str | `''` | channel name |
| `PHY_NAM` | str | `''` | physical name |
| `LOG_NAM` | str | `''` | logical name |
| `HEAD_NUM` | int | `0` | head number |
| `SITE_NUM` | int | `0` | site number |

#### `PGRRecord` — Pin Group Record `(1, 62)`

| Field | Type | Default | Description |
|---|---|---|---|
| `GRP_INDX` | int | — | group index |
| `GRP_NAM` | str | `''` | group name |
| `INDX_CNT` | int | `0` | number of pins in group |
| `PMR_INDX` | list[int] | `None` | pin map indexes |

#### `PLRRecord` — Pin List Record `(1, 63)`

| Field | Type | Default | Description |
|---|---|---|---|
| `GRP_CNT` | int | — | number of pin groups |
| `GRP_INDX` | list | `None` | group indexes |
| `GRP_MODE` | list | `None` | operational modes |
| `GRP_RADX` | list | `None` | radix for display |
| `PGM_CHAR` | list | `None` | program state chars (hi) |
| `RTN_CHAR` | list | `None` | return state chars (hi) |
| `PGM_CHAL` | list | `None` | program state chars (lo) |
| `RTN_CHAL` | list | `None` | return state chars (lo) |

#### `RDRRecord` — Retest Data Record `(1, 70)`

| Field | Type | Default | Description |
|---|---|---|---|
| `NUM_BINS` | int | — | number of retest bins |
| `RTST_BIN` | list[int] | `None` | retest bin numbers |

#### `BPSRecord` — Begin Program Section `(20, 10)`

| Field | Type | Default | Description |
|---|---|---|---|
| `SEQ_NAME` | str | `''` | section name |

#### `DTRRecord` — Datalog Text Record `(50, 30)`

| Field | Type | Default | Description |
|---|---|---|---|
| `TEXT_DAT` | str | `''` | ASCII text data |

#### `NULREcord` — Unknown/Null Record

| Field | Type | Description |
|---|---|---|
| `CONTENTS` | int | raw content as integer |

---

## Writing STDF: `STDFWriter` & Recipes

### Writer class

```python
from stdf_parser.STDFWriter import Writer

class Writer:
    def __init__(self, filepath: str)
    def collect(self, record: RecipeBase)    # append a recipe's bytes to buffer
    def save(self)                           # flush buffer to file

    # Convenience write methods (each accepts a dict of field values):
    def write_FAR(self, data: dict)
    def write_MIR(self, data: dict)
    def write_PIR(self, data: dict)
    def write_PTR(self, data: dict)
    def write_PRR(self, data: dict)
    def write_MRR(self, data: dict)
    def write_HBR(self, data: dict)
    def write_SBR(self, data: dict)
    def write_TSR(self, data: dict)
    def write_PCR(self, data: dict)
```

For record types without a `write_*` method, use the Recipe classes directly:

```python
from stdf_parser.RECRecipes import WIRRecipe, WRRRecipe

w = Writer("out.stdf")
w.collect(WIRRecipe({"HEAD_NUM": 1, "SITE_GRP": 255, "START_T": 0, "WAFER_ID": "W01"}))
w.collect(WRRRecipe({"HEAD_NUM": 1, "SITE_GRP": 255, "FINISH_T": 100, "PART_CNT": 50}))
w.save()
```

### Using Recipe classes directly

All recipes inherit from `RecipeBase`:

```python
class RecipeBase:
    REC_TYP: int
    REC_SUB: int
    FIELDS: list  # [(field_name, encoder_fn, default_value), ...]

    def __init__(self, data: dict)   # data keys that are missing use default_value
    def to_bytes(self) -> bytes      # returns 4-byte header + encoded body
```

### Recipe field reference

The `FIELDS` list in each recipe defines which dict keys are accepted and their encoding. Missing keys silently use the default. Key names are identical to the NamedTuple field names above.

| Recipe class | Import name | write_* method |
|---|---|---|
| `ATRRecipe` | `RECRecipes.ATRRecipe` | — |
| `BPSRecipe` | `RECRecipes.BPSRecipe` | — |
| `DTRRecipe` | `RECRecipes.DTRRecipe` | — |
| `FARRecipe` | `RECRecipes.FARRecipe` | `write_FAR` |
| `FTRRecipe` | `RECRecipes.FTRRecipe` | — |
| `HBRRecipe` | `RECRecipes.HBRRecipe` | `write_HBR` |
| `MIRRecipe` | `RECRecipes.MIRRecipe` | `write_MIR` |
| `MPRRecipe` | `RECRecipes.MPRRecipe` | — |
| `MRRRecipe` | `RECRecipes.MRRRecipe` | `write_MRR` |
| `PCRRecipe` | `RECRecipes.PCRRecipe` | `write_PCR` |
| `PGRRecipe` | `RECRecipes.PGRRecipe` | — |
| `PIRRecipe` | `RECRecipes.PIRRecipe` | `write_PIR` |
| `PLRRecipe` | `RECRecipes.PLRRecipe` | — |
| `PMRRecipe` | `RECRecipes.PMRRecipe` | — |
| `PRRRecipe` | `RECRecipes.PRRRecipe` | `write_PRR` |
| `PTRRecipe` | `RECRecipes.PTRRecipe` | `write_PTR` |
| `RDRRecipe` | `RECRecipes.RDRRecipe` | — |
| `SBRRecipe` | `RECRecipes.SBRRecipe` | `write_SBR` |
| `SDRRecipe` | `RECRecipes.SDRRecipe` | — |
| `TSRRecipe` | `RECRecipes.TSRRecipe` | `write_TSR` |
| `WCRRecipe` | `RECRecipes.WCRRecipe` | — |
| `WIRRecipe` | `RECRecipes.WIRRecipe` | — |
| `WRRRecipe` | `RECRecipes.WRRRecipe` | — |

---

## Binary Codec: `ByteFuncs`

All functions accept a `data` argument that is either an open binary file or a `RecordContainer`. Read functions advance the internal read position. `RecordTruncated` is raised if a read would exceed the declared record length.

### Read functions

```python
from stdf_parser.ByteFuncs import *
```

| Function | STDF type | Python return |
|---|---|---|
| `get_u(val, data)` | U*val (1/2/4) | `int` |
| `get_u_arr(val, count, data)` | kxU*val | `list[int]` |
| `get_i(val, data)` | I*val (1/2/4) | `int` (signed) |
| `get_r(val, data)` | R*val (4/8) | `float` (nan on error) |
| `get_r_arr(val, count, data)` | kxR*val | `list[float]` |
| `get_c(val, data)` | C*val | `str` |
| `get_cn(data)` | C*n | `str` (`'no data'` on error) |
| `get_cn_arr(count, data)` | kxC*n | `list[str]` |
| `get_b(val, data)` | B*val | `bytes` |
| `get_bn(data)` | B*n | `bytes` (`0` on error) |
| `get_dn(data)` | D*n | `bytes` (`0` on error) |
| `get_all(data)` | — | `int` (all remaining bytes) |

### Write functions

| Function | STDF type | Accepts | Returns |
|---|---|---|---|
| `write_u(val, value)` | U*val (1/2/4) | `int` | `bytes` |
| `write_u_arr(val, values)` | kxU*val | `list[int]` | `bytes` |
| `write_i(val, value)` | I*val (1/2/4) | `int` | `bytes` |
| `write_r(val, value)` | R*val (4/8) | `float` | `bytes` |
| `write_r_arr(val, values)` | kxR*val | `list[float]` | `bytes` |
| `write_cn(value)` | C*n | `str` or `None` | `bytes` |
| `write_cn_arr(values)` | kxC*n | `list[str]` | `bytes` |
| `write_c(val, value)` | C*val | `str` | `bytes` (space-padded) |
| `write_b(val, value)` | B*val | `int` or `bytes` | `bytes` (zero-padded) |
| `write_bn(value)` | B*n | `bytes` | `bytes` |
| `write_dn(value, bit_count=None)` | D*n | `bytes` | `bytes` |

---

## Exceptions

```python
from stdf_parser.ByteFuncs import RecordTruncated
```

| Exception | When raised |
|---|---|
| `RecordTruncated` | A `RecordContainer.read()` call would exceed the declared record length. Parsers catch this and return partial records with NamedTuple defaults for remaining fields. |

---

## STDF Type → Python Type mapping

| STDF type | Bytes | Python type | Notes |
|---|---|---|---|
| U*1 | 1 | `int` | unsigned 0–255 |
| U*2 | 2 | `int` | unsigned 0–65535 |
| U*4 | 4 | `int` | unsigned 0–4294967295 |
| I*1 | 1 | `int` | signed −128–127 |
| I*2 | 2 | `int` | signed −32768–32767 |
| I*4 | 4 | `int` | signed |
| R*4 | 4 | `float` | IEEE 754 single; `nan` on error |
| R*8 | 8 | `float` | IEEE 754 double; `nan` on error |
| C*1 | 1 | `str` | single ASCII character |
| C*f | f | `str` | fixed-length ASCII string |
| C*n | 1+n | `str` | length-prefixed ASCII string |
| B*1 | 1 | `bytes` | single byte |
| B*f | f | `bytes` | fixed-length bytes |
| B*n | 1+n | `bytes` | length-prefixed bytes |
| D*n | 2+⌈n/8⌉ | `bytes` | bit-count-prefixed bit field |

All multi-byte integers and floats are **little-endian** (CPU_TYPE=2).

---

## Known Limitations & Notes

- **`GDR` (Generic Data Record)** — parser stub returns `None`. GDR records are silently skipped by `stdf_parse.parse()`.
- **`EPS` (End Program Section)** — parser returns `None`.
- **`PRR.X_COORD` / `PRR.Y_COORD`** — the parser reads these as `U*2` (unsigned), but the STDF spec defines them as `I*2` (signed). Negative coordinates (common in wafer maps centered at origin) will appear as large positive numbers.
- **`PTR`/`MPR` limits** — `LO_LIMIT` and `HI_LIMIT` are set to `np.nan` when `OPT_FLAG` bit 6 or bit 7 is set (limit not valid / no limit). Always check `math.isnan()` before using limits.
- **STDF scaling** — the raw `RESULT` in a `PTRRecord` is **not** scaled. Apply `RESULT × 10^RES_SCAL` for the engineering value. `stdf_parse.parse()` does this automatically.
- **`MIR`/`MRR` timestamps** — returned as `datetime` objects (UTC epoch + field value seconds). `WIR`/`WRR` timestamps are raw `int` Unix timestamps (not converted to `datetime`).
- **`Debugger` bugs** — `Timer.start()` calls `time.time()` instead of the imported `time()`, and `Debugger.start_timer()` calls `timer.Start()` (non-existent). The debug path is unreliable; avoid `debug_enabled=True` in production.
- **`get_all()` bug** — references `ret` before assignment. Not triggered in normal parsing.
- **File start detection** — `stdf_parse.parse()` searches the first 100 KB for the FAR magic bytes. If the FAR is beyond 100 KB (unusual but valid), parsing will fail.
- **Multi-site** — `parse()` correctly handles simultaneous insertion on multiple sites. The low-level `RecordSelect` loop leaves multi-site ordering to the caller.
- **`Writer.save()`** — buffers the entire file in memory before writing. For very large files, use `RecipeBase.to_bytes()` and write incrementally to a file object.
