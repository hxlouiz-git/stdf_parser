from stdf_parser.STDFWriter import Writer
import random
import os
import pandas as pd


class TestParam:
        def __init__(self, name,num, lower_limit=None, upper_limit=None, units=None):
                self.name = name
                self.num = num
                self.lower_limit = lower_limit
                self.upper_limit = upper_limit
                self.units = units
#Tname	Tnum	Unit	HL	LL

csv_path = './testlist_input.csv'
df = pd.read_csv(csv_path)
tnums = df['Tnum'].tolist()
tnams = df['Tname'].tolist()
t_ll = df['LL'].tolist()
t_ul = df['HL'].tolist()
s1 = df['S1'].tolist()
s2 = df['S2'].tolist()
s3 = df['S3'].tolist()
s4 = df['S4'].tolist()

insertions = 100
sites = [0,1,2,3]

tests = {}

pin_grad = [s1,s2,s3,s4]



#for smartswitch probe
# #"VCC - PINTVCC - INTVCC - RSLEW - JGATE - TEMPOUT - READY - INPUT - JSOURCE - OCP"
# pin_grad = [
#         [0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01],
#         [0.58,0.31,0.37,0.58,0.01,0.55,0.5,0.58,0.24,0.57],
#         [0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01],
#         [1,0.72,0.78,0.92,0.32,0.84,0.82,0.96,0.65,0.88]
# ]

for i in range(len(tnums)):
        tests[i] = TestParam(tnams[i], tnums[i], t_ll[i], t_ul[i], "V")




file = Writer('balsam.stdf')


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












for _ in range(insertions):

        for site in sites:

                file.write_PIR({
                "HEAD_NUM": 1,
                "SITE_NUM": site
                })
                grad = pin_grad[site]

                site_pass = True
                for i, test in enumerate(tests.values()):
                        test: TestParam
                        pass_flag = random.random() > (grad[i]*random.random())*.3

                        site_pass = site_pass and pass_flag

                        file.write_PTR({
                                "TEST_NUM": test.num,
                                "HEAD_NUM": 1,
                                "SITE_NUM": site,
                                "TEST_FLG": 0 if pass_flag else 192,
                                "PARM_FLG": 0,
                                "RESULT": random.uniform(test.lower_limit, test.upper_limit) if pass_flag else -2 + random.uniform(-1,1)*1e-3,
                                "TEST_TXT": test.name,
                                "ALARM_ID": None,
                                "OPT_FLAG": 206,
                                "RES_SCAL": 0,
                                "LLM_SCAL": 0,
                                "HLM_SCAL": 0,
                                "LO_LIMIT": test.lower_limit,
                                "HI_LIMIT": test.upper_limit,
                                "UNITS": test.units,
                                "C_RESFMT": None,
                                "C_LLMFMT": None,
                                "C_HLMFMT": None,
                                "LO_SPEC": 0,
                                "HI_SPEC": 0
                        })


                file.write_PRR({

                        "HEAD_NUM": 1,
                        "SITE_NUM": site,
                        "PART_FLG": 0,
                        "NUM_TEST": 1,
                        "HARD_BIN": 1 if site_pass else 2,
                        "SOFT_BIN": 1 if site_pass else 8,
                        "X_COORD": 0,
                        "Y_COORD": 0,
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
