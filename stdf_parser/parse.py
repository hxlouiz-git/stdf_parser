"""
High-level STDF parser.

Public API
----------
parse(path) -> StdfData
    Parse an STDF file and return a structured StdfData object.

StdfData attributes
-------------------
    lot_info    : dict            — MIR fields (LOT_ID, PART_TYP, NODE_NAM, …)
    finish_info : dict            — MRR fields (FINISH_T, DISP_COD, …)
    wafers      : list[dict]      — one dict per WIR/WRR pair (wafer-level metadata)
    units       : list[dict]      — one dict per PIR/PRR pair (one unit plunge)
                                    keys: HEAD_NUM, SITE_NUM, PART_ID, SOFT_BIN,
                                          HARD_BIN, X_COORD, Y_COORD, TEST_T,
                                          NUM_TEST, WAFER_ID, + one key per test
    tests       : dict[key->TestMeta] — parametric info (limits, units, scale)
                                    keyed by (TEST_NUM, TEST_TXT)
    tsr         : list[TSRRecord] — TSR summary records
    sbin        : dict[int->SBRRecord] — soft-bin summaries keyed by SBIN_NUM
    hbin        : dict[int->HBRRecord] — hard-bin summaries keyed by HBIN_NUM

PIR/PRR handling
----------------
Multi-site STDFs send one PIR per active site before any PTR records, and one
PRR per site at the end.  We key the in-progress unit buffers by
(HEAD_NUM, SITE_NUM) so simultaneous plunges on different sites are tracked
independently and never clobber each other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .RECFuncs import (
    get_headers,
    PTR, MPR, FTR,
    PIR, PRR,
    MIR, MRR,
    WIR, WRR,
    TSR,
    SBR, HBR,
    SDR,
    RecordTruncated,
)

# (REC_TYP, REC_SUB) → parser function
_DISPATCH: dict[tuple[int, int], Any] = {
    (0,  10): None,          # FAR  — byte-order record; handled separately
    (1,  10): MIR,
    (1,  20): MRR,
    (1,  40): HBR,
    (1,  50): SBR,
    (1,  80): SDR,
    (2,  10): WIR,
    (2,  20): WRR,
    (5,  10): PIR,
    (5,  20): PRR,
    (10, 30): TSR,
    (15, 10): PTR,
    (15, 15): MPR,
    (15, 20): FTR,
}


@dataclass
class TestMeta:
    """Parametric metadata harvested from the first PTR/MPR for each test."""
    test_num: int
    test_txt: str
    units: str = ""
    lo_limit: float = float("nan")
    hi_limit: float = float("nan")
    res_scal: int = 0


@dataclass
class StdfData:
    lot_info: dict    = field(default_factory=dict)
    finish_info: dict = field(default_factory=dict)
    wafers: list      = field(default_factory=list)
    units: list       = field(default_factory=list)
    tests: dict       = field(default_factory=dict)   # (TEST_NUM, TEST_TXT) → TestMeta
    tsr: list         = field(default_factory=list)
    sbin: dict        = field(default_factory=dict)   # SBIN_NUM → SBRRecord
    hbin: dict        = field(default_factory=dict)   # HBIN_NUM → HBRRecord


def _record_key(rec) -> tuple[int, str]:
    return (rec.TEST_NUM, rec.TEST_TXT or "")


def _ptr_result(rec, meta: TestMeta | None) -> float:
    """Extract scalar result from PTR, applying RES_SCAL.

    Truncated PTRs (all records after the first for a given test) omit
    RES_SCAL.  Fall back to the scale stored in TestMeta so the result is
    always multiplied by the correct power of ten.
    """
    try:
        result = float(rec.RESULT) if rec.RESULT is not None else float("nan")
        if rec.RES_SCAL is not None:
            scal = int(rec.RES_SCAL)
        elif meta is not None:
            scal = meta.res_scal
        else:
            scal = 0
        return result * (10 ** scal)
    except (TypeError, ValueError):
        return float("nan")


def _ftr_result(rec) -> int:
    """0 = fail, 1 = pass for FTR."""
    return int(rec.RESULT)


def _register_test_meta(tests: dict, rec) -> TestMeta:
    """Store or update parametric metadata for a test record.

    The first full PTR/MPR for each test carries limits, units, and scale.
    All subsequent records for the same test are typically truncated — those
    optional fields come back as None.  We therefore:
      - Create the TestMeta on first encounter regardless of whether fields
        are present (truncated-first edge case).
      - On every subsequent encounter, overwrite only the fields that are
        non-None, so a full record arriving mid-lot can correct the metadata.
    Returns the (possibly newly created) TestMeta.
    """
    key = _record_key(rec)
    existing = tests.get(key)

    try:
        scal  = int(rec.RES_SCAL) if rec.RES_SCAL is not None else None
        lo    = float(rec.LO_LIMIT) if rec.LO_LIMIT is not None else None
        hi    = float(rec.HI_LIMIT) if rec.HI_LIMIT is not None else None
        units = rec.UNITS if getattr(rec, "UNITS", None) is not None else None
    except (TypeError, ValueError, AttributeError):
        scal, lo, hi, units = None, None, None, None

    if existing is None:
        resolved_scal = scal if scal is not None else 0
        tests[key] = TestMeta(
            test_num=rec.TEST_NUM,
            test_txt=rec.TEST_TXT or "",
            units=units or "",
            lo_limit=(lo * (10 ** resolved_scal)) if lo is not None else float("nan"),
            hi_limit=(hi * (10 ** resolved_scal)) if hi is not None else float("nan"),
            res_scal=resolved_scal,
        )
    else:
        if scal is not None:
            existing.res_scal = scal
        if units is not None:
            existing.units = units
        resolved_scal = existing.res_scal
        if lo is not None:
            existing.lo_limit = lo * (10 ** resolved_scal)
        if hi is not None:
            existing.hi_limit = hi * (10 ** resolved_scal)

    return tests[key]


def _mir_to_dict(mir) -> dict:
    if mir is None:
        return {}
    return {f: getattr(mir, f, None) for f in mir._fields}


def _wir_to_dict(wir) -> dict:
    return {f: getattr(wir, f, None) for f in wir._fields}


def _wrr_to_dict(wrr) -> dict:
    return {f: getattr(wrr, f, None) for f in wrr._fields}


def parse(path: str) -> StdfData:
    """
    Parse an STDF file at *path* and return a StdfData instance.

    All unit data (PTR/MPR/FTR) is buffered per (HEAD_NUM, SITE_NUM) between
    each PIR and its matching PRR.  On PRR the buffer is finalised into a unit
    dict and appended to StdfData.units.
    """
    data = StdfData()

    # in-flight unit buffers: (HEAD_NUM, SITE_NUM) → dict
    _active: dict[tuple[int, int], dict] = {}

    # open wafer contexts: HEAD_NUM → WIR dict
    _open_wafer: dict[int, dict] = {}
    _current_wafer: dict[int, str] = {}

    with open(path, "rb") as f:
        file_bytes = f.read()

    total = len(file_bytes)
    pos = 0

    # Skip to FAR record: find b'\x00\x0a' (FAR) or fall back to b'\x05\x0a' (PIR)
    far_pos = file_bytes.find(b'\x00\x0a')
    pir_pos = file_bytes.find(b'\x05\x0a')
    if far_pos != -1:
        pos = max(0, far_pos - 2)
    elif pir_pos != -1:
        pos = max(0, pir_pos - 2)

    while pos + 4 <= total:
        hdr_bytes = file_bytes[pos: pos + 4]
        try:
            header = get_headers(hdr_bytes, 4)
        except Exception:
            break

        rec_len    = header.REC_LEN
        rec_typ    = header.REC_TYP
        rec_sub    = header.REC_SUB
        body_start = pos + 4
        body_end   = body_start + rec_len

        if body_end > total:
            break

        body = file_bytes[body_start: body_end]
        pos  = body_end

        parser = _DISPATCH.get((rec_typ, rec_sub))
        if parser is None:
            continue

        try:
            rec = parser(body, rec_len)
        except (RecordTruncated, Exception):
            continue

        if (rec_typ, rec_sub) == (1, 10):    # MIR
            data.lot_info = _mir_to_dict(rec)

        elif (rec_typ, rec_sub) == (1, 20):  # MRR
            data.finish_info = {f: getattr(rec, f, None) for f in rec._fields}

        elif (rec_typ, rec_sub) == (1, 40):  # HBR
            data.hbin[rec.HBIN_NUM] = rec

        elif (rec_typ, rec_sub) == (1, 50):  # SBR
            data.sbin[rec.SBIN_NUM] = rec

        elif (rec_typ, rec_sub) == (2, 10):  # WIR — wafer start
            _open_wafer[rec.HEAD_NUM] = _wir_to_dict(rec)
            _current_wafer[rec.HEAD_NUM] = rec.WAFER_ID or ""

        elif (rec_typ, rec_sub) == (2, 20):  # WRR — wafer end
            wir = _open_wafer.pop(rec.HEAD_NUM, {})
            wafer = {**wir, **_wrr_to_dict(rec)}
            data.wafers.append(wafer)
            _current_wafer.pop(rec.HEAD_NUM, None)

        elif (rec_typ, rec_sub) == (5, 10):  # PIR — unit plunge starts
            key = (rec.HEAD_NUM, rec.SITE_NUM)
            _active[key] = {
                "HEAD_NUM":  rec.HEAD_NUM,
                "SITE_NUM":  rec.SITE_NUM,
                "WAFER_ID":  _current_wafer.get(rec.HEAD_NUM, ""),
            }

        elif (rec_typ, rec_sub) == (5, 20):  # PRR — unit plunge ends
            key = (rec.HEAD_NUM, rec.SITE_NUM)
            unit = _active.pop(key, {
                "HEAD_NUM": rec.HEAD_NUM,
                "SITE_NUM": rec.SITE_NUM,
                "WAFER_ID": _current_wafer.get(rec.HEAD_NUM, ""),
            })
            unit.update({
                "PART_ID":  rec.PART_ID  or "",
                "SOFT_BIN": rec.SOFT_BIN,
                "HARD_BIN": rec.HARD_BIN,
                "X_COORD":  rec.X_COORD,
                "Y_COORD":  rec.Y_COORD,
                "TEST_T":   rec.TEST_T,
                "NUM_TEST": rec.NUM_TEST,
            })
            data.units.append(unit)

        elif (rec_typ, rec_sub) == (10, 30):  # TSR
            data.tsr.append(rec)

        elif (rec_typ, rec_sub) == (15, 10):  # PTR
            key = (rec.HEAD_NUM, rec.SITE_NUM)
            if key not in _active:
                continue
            meta = _register_test_meta(data.tests, rec)
            col = _record_key(rec)
            _active[key][col] = _ptr_result(rec, meta)

        elif (rec_typ, rec_sub) == (15, 15):  # MPR
            key = (rec.HEAD_NUM, rec.SITE_NUM)
            if key not in _active:
                continue
            meta = _register_test_meta(data.tests, rec)
            col = _record_key(rec)
            try:
                scal = meta.res_scal
                _active[key][col] = [v * (10 ** scal) for v in rec.RTN_RSLT] if rec.RTN_RSLT else []
            except (TypeError, AttributeError):
                _active[key][col] = rec.RTN_RSLT

        elif (rec_typ, rec_sub) == (15, 20):  # FTR
            key = (rec.HEAD_NUM, rec.SITE_NUM)
            if key not in _active:
                continue
            _register_test_meta(data.tests, rec)
            col = _record_key(rec)
            _active[key][col] = _ftr_result(rec)

    return data
