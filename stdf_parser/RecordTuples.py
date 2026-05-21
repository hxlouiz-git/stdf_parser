from typing import NamedTuple
from datetime import datetime


class HeaderRecord(NamedTuple):

    REC_LEN: int
    REC_TYP: int
    REC_SUB: int


class ATRRecord(NamedTuple):

    MOD_TIM: int
    CMD_LINE: str = ''


class BPSRecord(NamedTuple):

    SEQ_NAME: str = ''


class DTRRecord(NamedTuple):

    TEXT_DAT: str = ''


class FARRecord(NamedTuple):

    CPU_TYPE: int
    STDF_VER: int


class FTRRecord(NamedTuple):

    # Mandatory fields
    TEST_NUM:  int
    HEAD_NUM:  int
    SITE_NUM:  int
    TEST_FLG:  int
    # Optional fields — defaults used when record is truncated
    OPT_FLG:   bytes = b'\x00'
    CYCL_CNT:  int   = 0
    REL_VADR:  int   = 0
    REPT_CNT:  int   = 0
    NUM_FAIL:  int   = 0
    XFAIL_AD:  int   = 0
    YFAIL_AD:  int   = 0
    VECT_OFF:  int   = 0
    RTN_ICNT:  int   = 0
    PGM_ICNT:  int   = 0
    RTN_INDX:  int   = 0
    RTN_STAT:  int   = 0
    PGM_INDX:  int   = 0
    PGM_STAT:  int   = 0
    FAIL_PIN:  bytes = b''
    VECT_NAME: str   = ''
    TIME_SET:  str   = ''
    OP_CODE:   str   = ''
    TEST_TXT:  str   = ''
    ALARM_ID:  str   = ''
    PROG_TXT:  str   = ''
    RSLT_TXT:  str   = ''
    PATG_NUM:  int   = 0
    SPIN_MAP:  str   = ''
    RESULT:    int   = 0


class HBRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    HBIN_NUM: int
    HBIN_CNT: int
    HBIN_PF:  str = ' '
    HBIN_NAM: str = ''


class MIRRecord(NamedTuple):

    # Mandatory fields
    SETUP_T:   datetime
    START_T:   datetime
    STAT_NUM:  int
    MODE_COD:  str
    RTST_COD:  str
    PROT_COD:  str
    BURN_TIM:  int
    CMOD_COD:  str
    LOT_ID:    str
    PART_TYP:  str
    # Optional fields — defaults used when record is truncated
    NODE_NAM:  str = ''
    TSTR_TYP:  str = ''
    JOB_NAM:   str = ''
    JOB_REV:   str = ''
    SBLOT_ID:  str = ''
    OPER_NAM:  str = ''
    EXEC_TYP:  str = ''
    EXEC_VER:  str = ''
    TEST_COD:  str = ''
    TST_TEMP:  str = ''
    USER_TXT:  str = ''
    AUX_FILE:  str = ''
    PKG_TYP:   str = ''
    FAMILY_ID: str = ''
    DATE_COD:  str = ''
    FACIL_ID:  str = ''
    FLOOR_ID:  str = ''
    PROC_ID:   str = ''
    OPER_FRQ:  str = ''
    SPEC_NAM:  str = ''
    SPEC_VER:  str = ''
    FLOW_ID:   str = ''
    SETUP_ID:  str = ''
    DSGN_REV:  str = ''
    ENG_ID:    str = ''
    ROM_COD:   str = ''
    SERL_NUM:  str = ''
    SUPR_NAM:  str = ''


class MPRRecord(NamedTuple):

    # Mandatory fields
    TEST_NUM:  int
    HEAD_NUM:  int
    SITE_NUM:  int
    TEST_FLG:  bytes
    PARM_FLG:  bytes
    RTN_ICNT:  int
    RSLT_CNT:  int
    # Optional fields — defaults used when record is truncated
    RTN_STAT:  list  = None
    RTN_RSLT:  list  = None
    TEST_TXT:  str   = ''
    ALARM_ID:  str   = ''
    OPT_FLAG:  bytes = None
    RES_SCAL:  int   = 0
    LLM_SCAL:  int   = 0
    HLM_SCAL:  int   = 0
    LO_LIMIT:  float = float('nan')
    HI_LIMIT:  float = float('nan')
    START_IN:  float = float('nan')
    INCR_IN:   float = float('nan')
    RTN_INDX:  list  = None
    UNITS:     str   = ''
    UNITS_IN:  str   = ''
    C_RESFMT:  str   = ''
    C_LLMFMT:  str   = ''
    C_HLMFMT:  str   = ''
    LO_SPEC:   float = float('nan')
    HI_SPEC:   float = float('nan')


class MRRRecord(NamedTuple):

    FINISH_T: datetime
    DISP_COD: str = ' '
    USR_DESC: str = ''
    EXC_DESC: str = ''


class NULREcord(NamedTuple):

    CONTENTS: int


class PCRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    PART_CNT: int
    RTST_CNT: int = 0
    ABRT_CNT: int = 0
    GOOD_CNT: int = 0
    FUNC_CNT: int = 0


class PGRRecord(NamedTuple):

    GRP_INDX: int
    GRP_NAM:  str  = ''
    INDX_CNT: int  = 0
    PMR_INDX: list = None


class PIRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int


class PLRRecord(NamedTuple):

    GRP_CNT:  int
    GRP_INDX: list = None
    GRP_MODE: list = None
    GRP_RADX: list = None
    PGM_CHAR: list = None
    RTN_CHAR: list = None
    PGM_CHAL: list = None
    RTN_CHAL: list = None


class PMRRecord(NamedTuple):

    PMR_INDX: int
    CHAN_TYP: int = 0
    CHAN_NAM: str = ''
    PHY_NAM:  str = ''
    LOG_NAM:  str = ''
    HEAD_NUM: int = 0
    SITE_NUM: int = 0


class PRRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    PART_FLG: bytes
    NUM_TEST: int
    HARD_BIN: int
    SOFT_BIN: int
    X_COORD:  int
    Y_COORD:  int
    TEST_T:   float
    PART_ID:  str
    PART_TXT: str = ''
    PART_FIX: str = ''


class PTRRecord(NamedTuple):

    # Mandatory fields
    TEST_NUM:  int
    HEAD_NUM:  int
    SITE_NUM:  int
    TEST_FLG:  bytes
    PARM_FLG:  bytes
    RESULT:    float
    # Optional fields — defaults used when record is truncated
    TEST_TXT:  str   = ''
    ALARM_ID:  str   = ''
    OPT_FLAG:  bytes = None
    RES_SCAL:  int   = 0
    LLM_SCAL:  int   = 0
    HLM_SCAL:  int   = 0
    LO_LIMIT:  float = float('nan')
    HI_LIMIT:  float = float('nan')
    UNITS:     str   = ''
    C_RESFMT:  str   = ''
    C_LLMFMT:  str   = ''
    C_HLMFMT:  str   = ''
    LO_SPEC:   float = float('nan')
    HI_SPEC:   float = float('nan')


class RDRRecord(NamedTuple):

    NUM_BINS: int
    RTST_BIN: list = None


class SBRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    SBIN_NUM: int
    SBIN_CNT: int
    SBIN_PF:  str = ' '
    SBIN_NAM: str = ''


class SDRRecord(NamedTuple):

    # Mandatory fields
    HEAD_NUM:  int
    SITE_GRP:  int
    SITE_CNT:  int
    SITE_NUM:  list
    # Optional fields — defaults used when record is truncated
    HAND_TYP:  str = ''
    HAND_ID:   str = ''
    CARD_TYP:  str = ''
    CARD_ID:   str = ''
    LOAD_TYP:  str = ''
    LOAD_ID:   str = ''
    DIB_TYP:   str = ''
    DIB_ID:    str = ''
    CABL_TYP:  str = ''
    CABL_ID:   str = ''
    CONT_TYP:  str = ''
    CONT_ID:   str = ''
    LASR_TYP:  str = ''
    LASR_ID:   str = ''
    EXTR_TYP:  str = ''
    EXTR_ID:   str = ''


class TSRRecord(NamedTuple):

    # Mandatory fields
    HEAD_NUM: int
    SITE_NUM: int
    TEST_TYP: str
    TEST_NUM: int
    # Optional fields — defaults used when record is truncated
    EXEC_CNT: int   = 0
    FAIL_CNT: int   = 0
    ALRM_CNT: int   = 0
    TEST_NAM: str   = ''
    SEQ_NAME: str   = ''
    TEST_LBL: str   = ''
    OPT_FLAG: bytes = None
    TEST_TIM: float = float('nan')
    TEST_MIN: float = float('nan')
    TEST_MAX: float = float('nan')
    TST_SUMS: float = float('nan')
    TST_SQRS: float = float('nan')


class WCRRecord(NamedTuple):

    WAFR_SIZ: float = float('nan')
    DIE_HT:   float = float('nan')
    DIE_WID:  float = float('nan')
    WF_UNITS: int   = 0
    WF_FLAT:  str   = ' '
    CENTER_X: int   = 0
    CENTER_Y: int   = 0
    POS_X:    str   = ' '
    POS_Y:    str   = ' '


class WIRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_GRP: int
    START_T:  int
    WAFER_ID: str = ''


class WRRRecord(NamedTuple):

    # Mandatory fields
    HEAD_NUM: int
    SITE_GRP: int
    FINISH_T: int
    PART_CNT: int
    # Optional fields — defaults used when record is truncated
    RTST_CNT: int = 0
    ABRT_CNT: int = 0
    GOOD_CNT: int = 0
    FUNC_CNT: int = 0
    WAFER_ID: str = ''
    FABWF_ID: str = ''
    FRAME_ID: str = ''
    MASK_ID:  str = ''
    USR_DESC: str = ''
    EXC_DESC: str = ''
