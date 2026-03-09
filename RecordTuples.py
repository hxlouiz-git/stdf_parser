from typing import NamedTuple
from datetime import datetime

class ATRRecord(NamedTuple):

    MOD_TIM: int  # Modification time
    CMD_LINE: str  # Command line


class BPSRecord(NamedTuple):

    SEQ_NAME: str  # Sequence name


class DTRRecord(NamedTuple):

    TEXT_DAT: str  # Text data

class FARRecord(NamedTuple):

    CPU_TYPE: int  # File ID
    STDF_VER: int  # STDF version

class FTRRecord(NamedTuple):

    TEST_NUM:int
    HEAD_NUM:int
    SITE_NUM:int
    TEST_FLG:int
    OPT_FLG:bytes
    CYCL_CNT:int
    REL_VADR:int
    REPT_CNT:int
    NUM_FAIL:int
    XFAIL_AD:int
    YFAIL_AD:int
    VECT_OFF:int
    RTN_ICNT:int
    PGM_ICNT:int
    RTN_INDX:int
    RTN_STAT:int
    PGM_INDX:int
    PGM_STAT:int
    FAIL_PIN:bytes
    VECT_NAME:str
    TIME_SET:str
    OP_CODE:str
    TEST_TXT:str
    ALARM_ID:str
    PROG_TXT:str
    RSLT_TXT:str
    RESULT:int

class HBRRecord(NamedTuple):

    HEAD_NUM: int  # Head number
    SITE_NUM: int  # Site count
    HBIN_NUM: int  # Number of bins
    HBIN_CNT: int
    HBIN_PF: str
    HBIN_PCT: str


class MIRRecord(NamedTuple):
    SETUP_T: datetime  # Setup time
    START_T: datetime  # Start time
    STAT_NUM: str  # Number of status codes
    MODE_COD: str
    RTST_COD: str
    PROT_COD: str
    BURN_TIM: int
    CMOD_COD: str
    LOT_ID: str
    PART_TYP: str
    NODE_NAM: str
    TSTR_TYP: str
    JOB_NAM: str
    JOB_REV: str
    SBLOT_ID: str
    OPER_NAM: str
    EXEC_TYP: str
    EXEC_VER: str
    TEST_COD: str
    TST_TEMP: str
    USER_TXT: str
    AUX_FILE: str
    PKG_TYP: str
    FAMILY_ID: str
    DATE_COD: str
    FACIL_ID: str
    FLOOR_ID: str
    PROC_ID: str
    OPER_FRQ: str
    SPEC_NAM: str
    SPEC_VER: str
    FLOW_ID: str
    SETUP_ID: str
    DSGN_REV: str
    ENG_ID: str
    ROM_COD: str
    SERL_NUM: str
    SUPR_NAM: str


class MPRRecord(NamedTuple):

    TEST_NUM: int
    HEAD_NUM: int
    SITE_NUM: int
    TEST_FLG: int
    PARM_FLG: bytes
    RTN_ICNT: int
    RSLT_CNT: int
    RTN_STAT: list
    RTN_RSLT: list
    TEST_TXT: str
    ALARM_ID: str
    OPT_FLAG: bytes
    RES_SCAL: int
    LLM_SCAL: int
    HLM_SCAL: int
    LO_LIMIT: float
    HI_LIMIT: float
    START_IN: float
    INCR_IN: float
    RTN_INDX: list
    UNITS: str
    UNITS_IN: str
    C_RESFMT: str
    C_LLMFMT: str
    C_HLMFMT: str
    LO_SPEC: float
    HI_SPEC: float

class MRRRecord(NamedTuple):

    FINISH_T: datetime
    DISP_COD: str
    USR_DESC: str
    EXC_DESC: str

class NULREcord(NamedTuple):

    CONTENTS: int  # Number of null records

class PCRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    PART_CNT: int
    RTST_CNT: int
    ABRT_CNT: int
    GOOD_CNT: int
    FUNC_CNT: int

class PGRRecord(NamedTuple):

    GRP_INDX: int
    GRP_NAM: str
    INDX_CNT: int
    PMR_INDX: list

class PIRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int

class PLRRecord(NamedTuple):

    GRP_CNT: int
    GRP_INDX: list
    GRP_MODE: list
    GRP_RADX: list
    PGM_CHAR: list
    RTN_CHAR: list
    PGM_CHAL: list
    RTN_CHAL: list

class PMRRecord(NamedTuple):

    PMR_INDX: int
    CHAN_TYP: int
    CHAN_NAM: str
    PHY_NAM: str
    LOG_NAM: str
    HEAD_NUM: int
    SITE_NUM: int

class PRRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    PART_FLG: bytes
    NUM_TEST: int
    HARD_BIN: int
    SOFT_BIN: int
    X_COORD: int
    Y_COORD: int
    TEST_T: float
    PART_ID: str
    PART_TXT: str
    PART_FIX: str

class PTRRecord(NamedTuple):

    TEST_NUM: int
    HEAD_NUM: int
    SITE_NUM: int
    TEST_FLG: bytes
    PARM_FLG: bytes
    RESULT: float
    TEST_TXT: str
    ALARM_ID: str
    OPT_FLAG: bytes
    RES_SCAL: int
    LLM_SCAL: int
    HLM_SCAL: int
    LO_LIMIT: float
    HI_LIMIT: float
    UNITS: str
    C_RESFMT: str
    C_LLMFMT: str
    C_HLMFMT: str
    LO_SPEC: float
    HI_SPEC: float

class RDRRecord(NamedTuple):

    NUM_BINS: int
    RTST_BIN = list

class SBRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    SBIN_NUM: int
    SBIN_CNT: int
    SBIN_PF: str
    SBIN_NAM: str

class SDRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    SITE_CNT: int
    SITE_NUM: list
    HAND_TYP = str
    HAND_ID = str
    CARD_TYP = str
    CARD_ID = str
    LOAD_TYP = str
    LOAD_ID = str
    DIB_TYP = str
    DIB_ID = str
    CABL_TYP = str
    CABL_ID = str
    LASR_TYP = str
    LASR_ID = str
    EXTR_TYP = str
    EXTR_ID = str

class TSRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_NUM: int
    TEST_TYP: str
    TEST_NUM: int
    EXEC_CNT: int
    FAIL_CNT: int
    ALRM_CNT: int
    TEST_NAM: str
    SEQ_NAME: str
    TEST_LBL: str
    OPT_FLAG: bytes
    TEST_TIM: float
    TEST_MIN: float
    TEST_MAX: float
    TST_SUMS: float
    TST_SQRS: float

class WCRRecord(NamedTuple):

    WAFR_SIZ: float
    DIE_HT: float
    DIE_WID: float
    WF_UNITS: int
    WF_FLAT: str
    CENTER_X: int
    CENTER_Y: int
    POS_X: str
    POS_Y: str


class WIRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_GRP: int
    START_T: int
    WAFER_ID: str

class WRRRecord(NamedTuple):

    HEAD_NUM: int
    SITE_GRP: int
    FINISH_T: int
    PART_CNT: int
    RTST_CNT: int
    ABRT_CNT: int
    GOOD_CNT: int
    FUNC_CNT: int
    WAFER_ID: str
    FABWF_ID: str
    FRAME_ID: str
    MASK_ID: str
    USR_DESC: str
    EXC_DESC: str
    