from stdf_parser.STDFWriter import Writer



file = Writer('test2.stdf')


file.write_FAR({
     "CPU_TYPE": 2,
        "STDF_VER": 4
})

file.write_MIR({
     "SETUP_T": 1212,
    "START_T": 54324,
        "STAT_NUM": 0,
        "MODE_COD": " ",
        "RTST_COD": " ",
        "PROT_COD": " ",
        "BURN_TIM": 0   ,
        "CMOD_COD": " ",
        "LOT_ID": "testlot",
        "PART_TYP": "adum1251",
        "NODE_NAM": None,
        "TSTR_TYP": "simtest",
        "JOB_NAM": "simprog",
        "JOB_REV": "v1",
        "SBLOT_ID": None,
        "OPER_NAM": "HDs",
        "EXEC_TYP": None,
        "EXEC_VER": None,
        "TEST_COD": None,
        "TST_TEMP": None,
        "USER_TXT": None,
        "AUX_FILE": None,
        "PKG_TYP": None,
        "FAMILY_ID": None,
        "DATE_COD": None,
        "FACIL_ID": None,
        "FLOOR_ID": None,
        "PROC_ID": None,
        "OPER_FRQ": None,
        "SPEC_NAM": None,
        "SPEC_VER": None,
        "FLOW_ID": None,
        "SETUP_ID": None,
        "DSGN_REV": None,
        "ENG_ID": None,
        "ROM_COD": None,
        "SERL_NUM": None,
        "SUPR_NAM": None
    
})

file.write_PIR({
    "HEAD_NUM": 1,
    "SITE_NUM": 0
})

file.write_PTR({
        "TEST_NUM": 10,
        "HEAD_NUM": 1,
        "SITE_NUM": 0,
        "TEST_FLG": 64,
        "PARM_FLG": 0,
        "RESULT": 67,
        "TEST_TXT": "X Coords",
        "ALARM_ID": None,
        "OPT_FLAG": 206,
        "RES_SCAL": 0,
        "LLM_SCAL": 0,
        "HLM_SCAL": 0,
        "LO_LIMIT": 0,
        "HI_LIMIT": 0,
        "UNITS": None,
        "C_RESFMT": None,
        "C_LLMFMT": None,
        "C_HLMFMT": None,
        "LO_SPEC": 0,
        "HI_SPEC": 0


})


file.write_PRR({

        "HEAD_NUM": 1,
        "SITE_NUM": 0,
        "PART_FLG": 0,
        "NUM_TEST": 1,
        "HARD_BIN": 0,
        "SOFT_BIN": 19,
        "X_COORD": 67,
        "Y_COORD": 41,
        "TEST_T": 0,
        "PART_ID": None,
        "PART_TXT": None,
        "PART_FIX": None
})

file.write_MRR({
        "FINISH_T": 5387,
        "DISP_COD": " ",
        "USR_DESC": None,
        "EXC_DESC": None    
})

file.save()
