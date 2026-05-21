from typing import NamedTuple
from datetime import datetime
from enum import Enum
from functools import partial
from stdf_parser.ByteFuncs import *


class RecipeBase:
    """Generic base for all STDF write recipes.

    Subclasses declare three class attributes:
        REC_TYP  – STDF record type byte
        REC_SUB  – STDF record sub-type byte
        FIELDS   – ordered list of (field_name, encoder_fn, default_value)
                   encoder_fn must accept a single value and return bytes.

    Example encoders (using functools.partial):
        partial(write_u, 1)  ->  U*1
        partial(write_u, 2)  ->  U*2
        partial(write_u, 4)  ->  U*4
        partial(write_i, 1)  ->  I*1
        partial(write_r, 4)  ->  R*4
        partial(write_r, 8)  ->  R*8
        write_cn             ->  C*n
        partial(write_c, 12) ->  C*12
        write_bn             ->  B*n
        partial(write_b, 6)  ->  B*6
    """

    REC_TYP = 0
    REC_SUB = 0
    FIELDS: list = []  # [(field_name, encoder_fn, default_value), ...]

    def __init__(self, data: dict):
        self._encoded = [
            encoder(data.get(name, default))
            for name, encoder, default in self.FIELDS
        ]

    def to_bytes(self) -> bytes:
        body = b''.join(self._encoded)
        REC_LEN = write_u(2, len(body))
        REC_TYP = write_u(1, self.REC_TYP)
        REC_SUB = write_u(1, self.REC_SUB)
        return REC_LEN + REC_TYP + REC_SUB + body



class ATRRecipe(RecipeBase):
    REC_TYP = 0
    REC_SUB = 20
    FIELDS = [
        ("MOD_TIM", partial(write_u, 4), 0),
        ("CMD_LINE", write_cn,           None),
    ]

class BPSRecipe(RecipeBase):
    REC_TYP = 20
    REC_SUB = 10
    FIELDS = [
        ("SEQ_NAME", write_cn, None),
    ]

class DTRRecipe(RecipeBase):
    REC_TYP = 50
    REC_SUB = 30
    FIELDS = [
        ("TEXT_DAT", write_cn, None),
    ]

class FARRecipe(RecipeBase):
    REC_TYP = 0
    REC_SUB = 10
    FIELDS = [
        ("CPU_TYPE", partial(write_u,1), 0),
        ("STDF_VER", partial(write_u,1), 4),
    ]

class FTRRecipe(RecipeBase):
    REC_TYP = 15
    REC_SUB = 20
    FIELDS = [
        ("TEST_NUM", partial(write_u,4), 0),
        ("HEAD_NUM", partial(write_u,1), 0),
        ("SITE_NUM", partial(write_u,1), 0),
        ("TEST_FLG", partial(write_b,1), 0),
        ("OPT_FLG", partial(write_b,1), 0),
        ("CYCL_CNT", partial(write_u,4), 0),
        ("REL_VADR", partial(write_u,4), 0),
        ("REPT_CNT", partial(write_u,4), 0),
        ("NUM_FAIL", partial(write_u,4), 0),
        ("XFAIL_AD", partial(write_i,4), 0),
        ("YFAIL_AD", partial(write_i,4), 0),
        ("VECT_OFF", partial(write_i,4), 0),
        ("RTN_ICNT", partial(write_u,2), 0),
        ("PGM_ICNT", partial(write_u,2), 0),
        ("RTN_INDX", partial(write_u,2), 0),
        ("RTN_STAT", partial(write_u,1), 0),
        ("PGM_INDX", partial(write_u,2), 0),
        ("PGM_STAT", partial(write_u,1), 0),
        ("FAIL_PIN", write_dn, None),
        ("VECT_NAME", write_cn, None),
        ("TIME_SET", write_cn, None),
        ("OP_CODE", write_cn, None),
        ("TEST_TXT", write_cn, None),
        ("ALARM_ID", write_cn, None),
        ("PROG_TXT", write_cn, None),
        ("RSLT_TXT", write_cn, None),
        ("PATG_NUM", partial(write_u,1), 255),
        ("SPIN_MAP", write_cn, None)
    ]

class HBRRecipe(RecipeBase):
    REC_TYP = 1
    REC_SUB = 40
    FIELDS = [
        ("HEAD_NUM", partial(write_u, 1), 0),
        ("SITE_NUM", partial(write_u, 1), 0),
        ("HBIN_NUM", partial(write_u, 2), 0),
        ("HBIN_CNT", partial(write_u, 4), 0),
        ("HBIN_PF", partial(write_c, 1), " "),
        ("HBIN_PCT", write_cn, None),
    ]

class MIRRecipe(RecipeBase):
    REC_TYP = 1
    REC_SUB = 10
    FIELDS = [
        ("SETUP_T", partial(write_u,4), 0),
        ("START_T", partial(write_u,4), 0),
        ("STAT_NUM", partial(write_u,1), 0),
        ("MODE_COD", partial(write_c,1), " "),
        ("RTST_COD", partial(write_c,1), " "),
        ("PROT_COD", partial(write_c,1), " "),
        ("BURN_TIM", partial(write_u,2), 0),
        ("CMOD_COD", partial(write_c,1), " "),
        ("LOT_ID", write_cn, None),
        ("PART_TYP", write_cn, None),
        ("NODE_NAM", write_cn, None),
        ("TSTR_TYP", write_cn, None),
        ("JOB_NAM", write_cn, None),
        ("JOB_REV", write_cn, None),
        ("SBLOT_ID", write_cn, None),
        ("OPER_NAM", write_cn, None),
        ("EXEC_TYP", write_cn, None),
        ("EXEC_VER", write_cn, None),
        ("TEST_COD", write_cn, None),
        ("TST_TEMP", write_cn, None),
        ("USER_TXT", write_cn, None),
        ("AUX_FILE", write_cn, None),
        ("PKG_TYP", write_cn, None),
        ("FAMILY_ID", write_cn, None),
        ("DATE_COD", write_cn, None),
        ("FACIL_ID", write_cn, None),
        ("FLOOR_ID", write_cn, None),
        ("PROC_ID", write_cn, None),
        ("OPER_FRQ", write_cn, None),
        ("SPEC_NAM", write_cn, None),
        ("SPEC_VER", write_cn, None),
        ("FLOW_ID", write_cn, None),
        ("SETUP_ID", write_cn, None),
        ("DSGN_REV", write_cn, None),
        ("ENG_ID", write_cn, None),
        ("ROM_COD", write_cn, None),
        ("SERL_NUM", write_cn, None),
        ("SUPR_NAM", write_cn, None),
    ]

class MPRRecipe(RecipeBase):
    REC_TYP = 15
    REC_SUB = 15
    FIELDS = [
        ("TEST_NUM", partial(write_u, 4), 0),
        ("HEAD_NUM", partial(write_u, 1), 0),
        ("SITE_NUM", partial(write_u, 1), 0),
        ("TEST_FLG", partial(write_b, 1), 0),
        ("PARM_FLG", partial(write_b, 1), 0),
        ("RTN_ICNT", partial(write_u, 2), 0),
        ("RSLT_CNT", partial(write_u, 2), 0),
        ("RTN_STAT", partial(write_u, 1), 0),
        ("RTN_RSLT", partial(write_u, 4), 0),
        ("TEST_TXT", write_cn, None),
        ("ALARM_ID", write_cn, None),
        ("OPT_FLAG", partial(write_b, 1), 0),
        ("RES_SCAL", partial(write_u, 1), 0),
        ("LLM_SCAL", partial(write_u, 1), 0),
        ("HLM_SCAL", partial(write_u, 1), 0),
        ("LO_LIMIT", partial(write_r, 4), 0),
        ("HI_LIMIT", partial(write_r, 4), 0),
        ("START_IN", partial(write_r, 4), 0),
        ("INCR_IN", partial(write_r, 4), 0),
        ("RTN_INDX", partial(write_u, 2), 0),
        ("UNITS", write_cn, None),
        ("UNITS_IN", write_cn, None),
        ("C_RESFMT", write_cn, None),
        ("C_LLMFMT", write_cn, None),
        ("C_HLMFMT", write_cn, None),
        ("LO_SPEC", partial(write_r, 4), 0),
        ("HI_SPEC", partial(write_r, 4), 0)
    ]

class MRRRecipe(RecipeBase):
    REC_TYP = 1
    REC_SUB = 20
    FIELDS = [
        ("FINISH_T", partial(write_u,4), 0),
        ("DISP_COD", partial(write_c,1), " "),
        ("USR_DESC", write_cn, None),
        ("EXC_DESC", write_cn, None)
    ]

class PCRRecipe(RecipeBase):
    REC_TYP = 1
    REC_SUB = 30
    FIELDS = [
        ("HEAD_NUM", partial(write_u, 1), 0),
        ("SITE_NUM", partial(write_u, 1), 0),
        ("PART_CNT", partial(write_u, 4), 0),
        ("RTST_CNT", partial(write_u, 4), 4294967295),
        ("ABRT_CNT", partial(write_u, 4), 4294967295),
        ("GOOD_CNT", partial(write_u, 4), 4294967295),
        ("FUNC_CNT", partial(write_u, 4), 4294967295)
    ]

class PGRRecipe(RecipeBase):
    REC_TYP = 1
    REC_SUB = 62
    FIELDS = [
        ("GRP_INDX", partial(write_u, 2), 0),
        ("GRP_NAM", write_cn, None),
        ("INDX_CNT", partial(write_u, 2), 0),
        ("PMR_INDX", partial(write_u, 2), 0)
    ]

class PIRRecipe(RecipeBase):
    REC_TYP = 5
    REC_SUB = 10
    FIELDS = [
        ("HEAD_NUM", partial(write_u, 1), 1),
        ("SITE_NUM", partial(write_u, 1), 0)
    ]

class PLRRecipe(RecipeBase):
    REC_TYP = 5
    REC_SUB = 20
    FIELDS = [
        ("GRP_CNT", partial(write_u, 2), 0),
        ("GRP_INDX", partial(write_u, 2), 0),
        ("GRP_MODE", partial(write_u, 2), 0),
        ("GRP_RADX", partial(write_u, 1), 0),
        ("PGM_CHAR", write_cn, None),
        ("RTN_CHAR", write_cn, None),
        ("PGM_CHAL", write_cn, None),
        ("RTN_CHAL", write_cn, None)
    ]

class PMRRecipe(RecipeBase):
    REC_TYP = 1
    REC_SUB = 60
    FIELDS = [
        ("PMR_INDX", partial(write_u, 2), 0),
        ("CHAN_TYP", partial(write_u, 2), 0),
        ("CHAN_NAM", write_cn, None),
        ("PHY_NAM", write_cn, None),
        ("LOG_NAM", write_cn, None),
        ("HEAD_NUM", partial(write_u, 1), 1),
        ("SITE_NUM", partial(write_u, 1), 1)
    ]

class PRRRecipe(RecipeBase):
    REC_TYP = 5
    REC_SUB = 20
    FIELDS = [
        ("HEAD_NUM", partial(write_u, 1), 1),
        ("SITE_NUM", partial(write_u, 1), 0),
        ("PART_FLG", partial(write_b, 1), 0),
        ("NUM_TEST", partial(write_u, 2), 0),
        ("HARD_BIN", partial(write_u, 2), 0),
        ("SOFT_BIN", partial(write_u, 2), 65535),
        ("X_COORD", partial(write_i, 2), -32768),
        ("Y_COORD", partial(write_i, 2), -32768),
        ("TEST_T", partial(write_u, 4), 0),
        ("PART_ID", write_cn, None),
        ("PART_TXT", write_cn, None),
        ("PART_FIX", write_bn, None)
    ]

class PTRRecipe(RecipeBase):
    REC_TYP = 15
    REC_SUB = 10
    FIELDS = [
        ("TEST_NUM", partial(write_u, 4), 0),
        ("HEAD_NUM", partial(write_u, 1), 0),
        ("SITE_NUM", partial(write_u, 1), 0),
        ("TEST_FLG", partial(write_b, 1), 0),
        ("PARM_FLG", partial(write_b, 1), 0),
        ("RESULT", partial(write_r, 4), 0),
        ("TEST_TXT", write_cn, None),
        ("ALARM_ID", write_cn, None),
        ("OPT_FLAG", partial(write_b, 1), 0),
        ("RES_SCAL", partial(write_i, 1), 0),
        ("LLM_SCAL", partial(write_i, 1), 0),
        ("HLM_SCAL", partial(write_i, 1), 0),
        ("LO_LIMIT", partial(write_r, 4), 0),
        ("HI_LIMIT", partial(write_r, 4), 0),
        ("UNITS", write_cn, None),
        ("C_RESFMT", write_cn, None),
        ("C_LLMFMT", write_cn, None),
        ("C_HLMFMT", write_cn, None),
        ("LO_SPEC", partial(write_r, 4), 0),
        ("HI_SPEC", partial(write_r, 4), 0)
    ]

class RDRRecipe(RecipeBase):
    REC_TYP = 1
    REC_SUB = 70
    FIELDS = [
        ("NUM_BINS", partial(write_u, 2), 0),
        ("RTST_BIN", partial(write_u,2), 0)
    ]

class SBRRecipe(RecipeBase):
    REC_TYP = 1
    REC_SUB = 50
    FIELDS = [
        ("HEAD_NUM", partial(write_u, 1), 0),
        ("SITE_NUM", partial(write_u, 1), 0),
        ("SBIN_NUM", partial(write_u, 2), 0),
        ("SBIN_CNT", partial(write_u, 4), 0),
        ("SBIN_PF", partial(write_c, 1), " "),
        ("SBIN_NAM", write_cn, None)
    ]

class SDRRecipe(RecipeBase):

    REC_TYP = 1
    REC_SUB = 80
    FIELDS = [
            ("HEAD_NUM", partial(write_u, 1), 0),
            ("SITE_NUM", partial(write_u, 1), 0),
            ("SITE_CNT", partial(write_u, 1), 0),
            ("SITE_NUM", partial(write_u, 1), 0),
            ("HAND_TYP", write_cn, None),
            ("HAND_ID", write_cn, None),
            ("CARD_TYP", write_cn, None),
            ("CARD_ID", write_cn, None),
            ("LOAD_TYP", write_cn, None),
            ("LOAD_ID", write_cn, None),
            ("DIB_TYP", write_cn, None),
            ("DIB_ID", write_cn, None),
            ("CABL_TYP", write_cn, None),
            ("CABL_ID", write_cn, None),
            ("LASR_TYP", write_cn, None),
            ("LASR_ID", write_cn, None),
            ("EXTR_TYP", write_cn, None),
            ("EXTR_ID", write_cn, None)
    ]

class TSRRecipe(RecipeBase):
    REC_TYP = 10
    REC_SUB = 30
    FIELDS = [
        ("HEAD_NUM", partial(write_u, 1), 0),
        ("SITE_NUM", partial(write_u, 1), 0),
        ("TEST_TYP", partial(write_c, 1), " "),
        ("TEST_NUM", partial(write_u, 4), 0),
        ("EXEC_CNT", partial(write_u, 4), 4294967295),
        ("FAIL_CNT", partial(write_u, 4), 4294967295),
        ("ALRM_CNT", partial(write_u, 4), 4294967295),
        ("TEST_NAM", write_cn, None),
        ("SEQ_NAME", write_cn, None),
        ("TEST_LBL", write_cn, None),
        ("OPT_FLAG", partial(write_b, 1), 0),
        ("TEST_TIM", partial(write_r, 4), 0),
        ("TEST_MIN", partial(write_r, 4), 0),
        ("TEST_MAX", partial(write_r, 4), 0),
        ("TST_SUMS", partial(write_r, 4), 0),
        ("TST_SQRS", partial(write_r, 4), 0)
    ]

class WCRRecipe(RecipeBase):
    REC_TYP = 2
    REC_SUB = 30
    FIELDS = [
        ("WAFR_SIZ", partial(write_r, 4), 0),
        ("DIE_HT", partial(write_r, 4), 0),
        ("DIE_WID", partial(write_r, 4), 0),
        ("WF_UNITS", partial(write_u, 1), 0),
        ("WF_FLAT", partial(write_c, 1), " "),
        ("CENTER_X", partial(write_i, 2), -32768),
        ("CENTER_Y", partial(write_i, 2), -32768),
        ("POS_X", partial(write_c,1), " "),
        ("POS_Y", partial(write_c,1), " ")
    ]

class WIRRecipe(RecipeBase):
    REC_TYP = 2
    REC_SUB = 10
    FIELDS = [
        ("HEAD_NUM", partial(write_u, 1), 0),
        ("SITE_GRP", partial(write_u, 1), 255),
        ("START_T", partial(write_u, 4), 0),
        ("WAFER_ID", write_cn, None)
    ]

class WRRRecipe(RecipeBase):
    REC_TYP = 2
    REC_SUB = 20
    FIELDS = [
        ("HEAD_NUM", partial(write_u, 1), 0),
        ("SITE_GRP", partial(write_u, 1), 255),
        ("FINISH_T", partial(write_u, 4), 0),
        ("PART_CNT", partial(write_u, 4), 0),
        ("RTST_CNT", partial(write_u, 4), 4294967295),
        ("ABRT_CNT", partial(write_u, 4), 4294967295),
        ("GOOD_CNT", partial(write_u, 4), 4294967295),
        ("FUNC_CNT", partial(write_u, 4), 4294967295),
        ("WAFER_ID", write_cn, None),
        ("FABWF_ID", write_cn, None),
        ("FRAME_ID", write_cn, None),
        ("MASK_ID", write_cn, None),
        ("USR_DESC", write_cn, None),
        ("EXC_DESC", write_cn, None)
    ]
    