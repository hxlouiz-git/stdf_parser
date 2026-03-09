
from datetime import datetime, timedelta
from functools import wraps
import numpy as np


from Debugger import Debugger

from MBgetFuncs import get_u , get_c ,get_cn, get_r, get_b, get_bn, get_i, get_dn, get_all, get_r_arr, get_u_arr, get_cn_arr
from RecordTuples import *




class RecordContainer():
    def __init__(self,contents,length):
        self.contents = contents
        self.length = length
        self.pos = 0

    def content_check(self, func):
        @wraps(func)
        def wrapper(self, size=None):
            if self.length_check():
                pass
            else:
                raise Exception("Attempting to read beyond record length")
            
            if size == 0:
                raise Exception("Attempting to read 0 bytes")

            return func(size)    
        return wrapper



    def read(self, size):

        if self.length_check(size):    
            data = self.contents[self.pos:self.pos+size]
            self.pos += size
            return data
        else:
            raise Exception("Attempting to read beyond record length")
    
    def length_check(self, size):
        return self.pos + size <= self.length
    
    def move(self, size):
        if self.length_check(size):    
            self.pos += size
        else:
            raise Exception("Attempting to move beyond record length")
        
    def move_n(self):
        if self.length_check(1):    
            size = self.read(1)
            self.move(size)
        else:
            raise Exception("Attempting to move beyond record length")

def debug_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Allow debugFlag to be passed as argument, otherwise use self.debugFlag
        debug_enabled = kwargs['debug_enabled']

        if debug_enabled:
            record=func.__name__
            print(f"Debug: Starting {record} with args: {args}, kwargs: {kwargs}")
            Debugger.write("RECfile",f"{record}\n")
            Debugger.start_timer(record)

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f"simulating {func.__name__}")
            result = None

        if debug_enabled:
            print(f"Debug: Finished {record} with result: {result}")
            Debugger.stop_timer(record)
            Debugger.count(record)

        return result
    return wrapper

def contents_wrapper(func):
    @wraps(func)
    def wrapper(contents, length):
        container = RecordContainer(contents, length)
        return func(container)
    return wrapper

def parse_record(func):
    return debug_wrapper(contents_wrapper(func))


def RecordSelect(f,containers):

    if containers.debugFlag:
        containers.DebuggerStartTimer("file read")


    NULL_REC=0
    fsub=f.read(4)
    REC_LEN,REC_TYP,REC_SUB=get_headers(fsub,4)
    fsub=f.read(REC_LEN)
    pos=f.tell()

    if containers.debugFlag:
        data = f"Pos: {pos} REC_LEN: {REC_LEN} REC_TYP: {REC_TYP} REC_SUB: {REC_SUB} "
        containers.DebuggerWrite("RECfile",f"{data}")
        containers.DebuggerStopTimer("file read")


    if REC_TYP==15:
        if REC_SUB==10:      # PTR()   
            PTR2(fsub,REC_LEN,containers)  # [TEST_TXT, TEST_NUM, UNITS, HI_LIMIT, LO_LIMIT, RES_SCAL]

        elif REC_SUB==15:    # MPR()
            MPR2(fsub,REC_LEN,containers)  # [TEST_NUM,RESULT,SITE_NUM,TEST_TXT,var,RTN_ICNT]
        
        elif REC_SUB==20:    # FTR()
            FTR2(fsub,REC_LEN,containers)    # [TEST_NUM,RESULT,SITE_NUM,TEST_TXT]

        else:
            NULL_REC=1
    elif REC_TYP==5:
        if REC_SUB==10:      # PIR()
            PIR2(fsub,REC_LEN,containers)

        elif REC_SUB==20:    # PRR()
            PRR2(fsub,REC_LEN,containers)   # return [PART_ID,SOFT_BIN,HARD_BIN,X_COORD,Y_COORD,SITE_NUM,TEST_T,NUM_TEST] 

        else:
            NULL_REC=1
    elif REC_TYP==0:
        if REC_SUB==10:      # FAR()
            FAR2(fsub,REC_LEN,containers)

        elif REC_SUB==20:    # ATR()
            ATR2(fsub,REC_LEN,containers)
            
        else:
            NULL_REC=1
    elif REC_TYP==1:
        if REC_SUB==10:    # MIR()
            MIR2(fsub,REC_LEN,containers) #see above legend

        elif REC_SUB==20:    # MRR()
            MRR2(fsub,REC_LEN,containers)  #LOTDet[3]=MRR(fsub,REC_LEN) #End time

        elif REC_SUB==30:    # PCR()
            PCR2(fsub,REC_LEN,containers)

        elif REC_SUB==40:    # HBR()
            HBR2(fsub,REC_LEN,containers)

        elif REC_SUB==50:    # SBR()
            SBR2(fsub,REC_LEN,containers)

        elif REC_SUB==60:    # PMR()
            PMR2(fsub,REC_LEN,containers) #[PMR_INDX,CHAN_TYP,CHAN_NAM,PHY_NAM,LOG_NAM,HEAD_NUM,SITE_NUM]
        
        elif REC_SUB==62:    # PGR()
            PGR2(fsub,REC_LEN,containers)

        elif REC_SUB==63:    # PLR()
            PLR2(fsub,REC_LEN,containers)

        elif REC_SUB==70:    # RDR()
            RDR2(fsub,REC_LEN,containers)

        elif REC_SUB==80:    # SDR()
            SDR2(fsub,REC_LEN,containers) #[HAND_TYP,HAND_ID,CARD_TYP,CARD_ID,DIB_ID]

        else:
            NULL_REC=1
    elif REC_TYP==2:
        if REC_SUB==10:      # WIR()
            WIR2(fsub,REC_LEN,containers) 

        elif REC_SUB==20:    # WRR()
            WRR2(fsub,REC_LEN,containers)

        elif REC_SUB==30:    # WCR()
            WCR2(fsub,REC_LEN,containers)

        else:
            NULL_REC=1        
    elif REC_TYP==10:
        if REC_SUB==30:      # TSR()
            TSR2(fsub,REC_LEN,containers) #0HEAD_NUM,1SITE_NUM,2TEST_TYP,3TEST_NUM,4EXEC_CNT,5FAIL_CNT,6TEST_NAM

        else:
            NULL_REC=1         
    elif REC_TYP==20:
        if REC_SUB==10:      # BPS() 
            BPS2(fsub,REC_LEN,containers)

        elif REC_SUB==20:    # EPS()
            EPS2(fsub,REC_LEN,containers)

        else:
            NULL_REC=1
    elif REC_TYP==50:
        if REC_SUB==10:      # GDR()
            GDR2(fsub,REC_LEN,containers)
            
        elif REC_SUB==30:    # DTR()
            DTR2(fsub,REC_LEN,containers)

        else:
            NULL_REC=1
    else:
        NULL_REC=2

    if NULL_REC==1:
        print("Unrecognized record sub type REC_TYP: " + str(REC_TYP) + " REC_SUB: " + str(REC_SUB) +" , will attempt to skip.")
        NULL_REC=0
        NULLREC(fsub,pos,REC_TYP,REC_SUB,containers)
    elif NULL_REC==2:
        print("Unrecognized record type REC_TYP: " + str(REC_TYP) + " REC_SUB: " + str(REC_SUB) +", will now terminate. Try ParamOnly mode or send STDF to developer for checking")
        NULLREC(fsub,pos,REC_TYP,REC_SUB,containers)
        f.seek(0,2) #go to end of file to terminate stdf reading

    return pos

@parse_record
def get_headers(data: RecordContainer):
    REC_LEN=get_u(2,data)
    REC_TYP=get_u(1,data)
    REC_SUB=get_u(1,data)

    return REC_LEN, REC_TYP, REC_SUB

@parse_record
def ATR(data: RecordContainer):

    MOD_TIM = get_u(4, data)
    CMD_LINE = get_cn(data)

    return ATRRecord(MOD_TIM, CMD_LINE)

@parse_record
def BPS(data: RecordContainer):

    SEQ_NAME = get_cn(data)

    return BPSRecord(SEQ_NAME)

@parse_record
def DTR(data: RecordContainer):

    TEXT_DAT = get_cn(data)

    return DTRRecord(TEXT_DAT)

@parse_record
def EPS(data: RecordContainer):
    
    return None

@parse_record
def FAR(data: RecordContainer):
    
    CPU_TYPE=get_u(1,data)
    STDF_VER=get_u(1,data)

    return FARRecord(CPU_TYPE, STDF_VER)

@parse_record
def FTR(data: RecordContainer):

    TEST_NUM = get_u(4,data)
    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)
    TEST_FLG = get_u(1,data) #B1
    OPT_FLAG = get_b(1,data)
    CYCL_CNT = get_u(4,data)
    REL_VADR = get_u(4,data)
    REPT_CNT = get_u(4,data)
    NUM_FAIL = get_u(4,data)
    XFAIL_AD = get_i(4,data)
    YFAIL_AD = get_i(4,data)
    VECT_OFF = get_i(2,data)
    RTN_ICNT = get_u(2,data)
    PGM_ICNT = get_u(2,data)

    RTN_INDX = get_u(2*RTN_ICNT,data)
    RTN_STAT = get_u((RTN_ICNT // 2) + (RTN_ICNT % 2),data)

    PGM_INDX = get_u(2*PGM_ICNT,data)
    PGM_STAT = get_u((PGM_ICNT // 2) + (PGM_ICNT % 2),data)

    FAIL_PIN = get_dn(data)

    VECT_NAM = get_cn(data)
    TIME_SET = get_cn(data)
    OP_CODE = get_cn(data)

    TEST_TXT = get_cn(data)
    ALARM_ID = get_cn(data)
    PROG_TXT = get_cn(data)
    RSLT_TXT = get_cn(data)
    PATG_NUM = get_u(1,data)
    SPIN_MAP = get_dn(data)

    if TEST_FLG&128 == 0:
        RESULT=1
    else:
        RESULT=0

    return FTRRecord(TEST_NUM, HEAD_NUM, SITE_NUM, TEST_FLG,
                     OPT_FLAG, CYCL_CNT, REL_VADR, REPT_CNT,
                     NUM_FAIL, XFAIL_AD, YFAIL_AD, VECT_OFF,
                     RTN_ICNT, PGM_ICNT, RTN_INDX, RTN_STAT,
                     PGM_INDX, PGM_STAT, FAIL_PIN, VECT_NAM,
                     TIME_SET, OP_CODE, TEST_TXT, ALARM_ID,
                     PROG_TXT, RSLT_TXT, PATG_NUM, SPIN_MAP,
                     RESULT)

@parse_record
def GDR(data: RecordContainer):

    return None
 
@parse_record
def HBR(data: RecordContainer): 

    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)
    HBIN_NUM = get_u(2,data)
    HBIN_CNT = get_u(4,data)
    HBIN_PF = get_c(1,data)
    HBIN_NAM = get_cn(data)

    return HBRRecord(HEAD_NUM, SITE_NUM, HBIN_NUM, HBIN_CNT, HBIN_PF, HBIN_NAM)

@parse_record
def MIR(data: RecordContainer): 

    SETUP_T = get_u(4,data)
    SETUP_T = datetime(1970,1,1,0,0,0) + timedelta(seconds=SETUP_T)
    START_T = get_u(4,data)
    START_T = datetime(1970,1,1,0,0,0) + timedelta(seconds=START_T)
    STAT_NUM = get_u(1,data)
    MODE_COD = get_c(1,data)
    RTST_COD = get_c(1,data)
    PROT_COD = get_c(1,data)
    BURN_TIM = get_u(2,data)
    CMOD_COD = get_c(1,data)
    LOT_ID = get_cn(data)
    PART_TYP = get_cn(data)
    NODE_NAM = get_cn(data)
    TSTR_TYP = get_cn(data)
    JOB_NAM = get_cn(data)
    JOB_REV = get_cn(data)
    SBLOT_ID = get_cn(data)
    OPER_NAM = get_cn(data)
    EXEC_TYP = get_cn(data)
    EXEC_VER = get_cn(data)
    TEST_COD = get_cn(data)
    TST_TEMP = get_cn(data)
    USER_TXT = get_cn(data)
    AUX_FILE = get_cn(data)
    PKG_TYP = get_cn(data)
    FAMILY_ID = get_cn(data)
    DATE_COD = get_cn(data)
    FACIL_ID = get_cn(data)
    FLOOR_ID = get_cn(data)
    PROC_ID = get_cn(data)
    OPER_FRQ = get_cn(data)
    SPEC_NAM = get_cn(data)
    SPEC_VER = get_cn(data)
    FLOW_ID = get_cn(data)
    SETUP_ID = get_cn(data)
    DSGN_REV = get_cn(data)
    ENG_ID = get_cn(data)
    ROM_COD = get_cn(data)
    SERL_NUM = get_cn(data)
    SUPR_NAM = get_cn(data)
    

    return MIRRecord(SETUP_T, START_T, STAT_NUM, MODE_COD, 
                     RTST_COD, PROT_COD, BURN_TIM, CMOD_COD, 
                     LOT_ID, PART_TYP, NODE_NAM, TSTR_TYP, 
                     JOB_NAM, JOB_REV, SBLOT_ID, OPER_NAM, 
                     EXEC_TYP, EXEC_VER, TEST_COD, TST_TEMP, 
                     USER_TXT, AUX_FILE, PKG_TYP, FAMILY_ID, 
                     DATE_COD, FACIL_ID, FLOOR_ID, PROC_ID, 
                     OPER_FRQ, SPEC_NAM, SPEC_VER, FLOW_ID, 
                     SETUP_ID, DSGN_REV, ENG_ID, ROM_COD, 
                     SERL_NUM, SUPR_NAM)

@parse_record
def MPR(data: RecordContainer): 

        TEST_NUM = get_u(4,data)
        HEAD_NUM = get_u(1,data)
        SITE_NUM = get_u(1,data)
        TEST_FLG = get_b(1,data)
        PARM_FLG = get_b(1,data)
        RTN_ICNT = get_u(2,data)
        RSLT_CNT = get_u(2,data)
        RTN_STAT = get_u((RTN_ICNT // 2) + (RTN_ICNT % 2),data)
        RTN_RSLT = get_r_arr(4,RSLT_CNT,data)
        TEST_TXT = get_cn(data)
        ALARM_ID = get_cn(data)

        OPT_FLAG = get_b(1,data) #B1
        RES_SCAL = get_i(1,data)
        LLM_SCAL = get_i(1,data)
        HLM_SCAL = get_i(1,data)

        LO_LIMIT = get_r(4,data)
        if OPT_FLAG&64 == 64:
            LO_LIMIT = np.nan
        HI_LIMIT = get_r(4,data)
        if OPT_FLAG&128 == 128:
            HI_LIMIT = np.nan

        START_IN = get_r(4,data)
        INCR_IN = get_r(4,data)

        RTN_INDX = get_u_arr(2, RTN_ICNT, data)

        UNITS = get_cn(data)
        
        UNITS_IN = get_cn(data)
        C_RESFMT = get_cn(data)
        C_LLMFMT = get_cn(data)
        C_HLMFMT = get_cn(data)
        LO_SPEC = get_r(4,data)
        HI_SPEC = get_r(4,data)

        return MPRRecord(   TEST_NUM, HEAD_NUM, SITE_NUM, TEST_FLG,
                            PARM_FLG, RTN_ICNT, RSLT_CNT, RTN_STAT, 
                            RTN_RSLT, TEST_TXT, ALARM_ID, OPT_FLAG, 
                            RES_SCAL, LLM_SCAL, HLM_SCAL, LO_LIMIT, 
                            HI_LIMIT, START_IN, INCR_IN, RTN_INDX,
                            UNITS, UNITS_IN, C_RESFMT, C_LLMFMT,
                            C_HLMFMT, LO_SPEC, HI_SPEC)


# def MPR2(fsub,length,containers):

#     if containers.debugFlag:
#         record="MPR"
#         containers.DebuggerWrite("RECfile",f"{record}\n")
#         containers.DebuggerStartTimer(record)

#     duplicateTestNumFlag = False
#     TEST_NUM,var=get_u(4,fsub,0,length)
#     #HEAD_NUM,var=MBgetU(1,fsub,var,len)
#     var = var + 1
#     SITE_NUM,var=get_u(1,fsub,var,length)
#     #TEST_FLG,var=MBgetB(1,fsub,var,len)
#     #PARM_FLG,var=MBgetB(1,fsub,var,len)
#     var = var + 2
#     RTN_ICNT,var=get_u(2,fsub,var,length)
#     RSLT_CNT,var=get_u(2,fsub,var,length)
#     jump=(RTN_ICNT // 2) + (RTN_ICNT % 2)  #RTN_STAT
#     var=var+jump
#     RESULTave=0
#     RESULTppin=[]
#     for _ in range(RSLT_CNT):
#         Res,var=get_r(4,fsub,var,length)
#         RESULTave+=Res
#         RESULTppin.append(Res)
#     RESULTave=RESULTave/RSLT_CNT
#     TEST_TXT,var=get_cn(fsub,var,length)
#     TEST_TXT=TEST_TXT.replace(",", " ")
#     tnum = f"{TEST_NUM} {TEST_TXT}"
#     tnumPerPin = []


#     siteIndex = containers.siteList[SITE_NUM]

#     try:
#         parameter = containers.testListLocal[tnum]

#         for pin in parameter.pins:
#             tnumPerPin.append(f"{tnum} - {containers.pinList[pin]}")

#         containers.touchdownInfo[siteIndex][parameter.index+containers.colPadding] = RESULTave

#         if not parameter.duplicateTN:
#             for i, pin in enumerate(tnumPerPin):
#                 parameterPerPin = containers.testListLocal[pin]
#                 containers.touchdownInfo[siteIndex][parameterPerPin.index+containers.colPadding] = RESULTppin[i]

#     except KeyError as e:
#         #print(f"MPR Local:{e}")

#         try:
#             ALARM_ID,var=get_cn(fsub,var,length)
#             OPT_FLAG,var=get_u(1,fsub,var,length) #B1
#             RES_SCAL,var=get_i(1,fsub,var,length)
#             #LLM_SCAL,var=MBgetU(1,fsub,var,len)
#             #HLM_SCAL,var=MBgetU(1,fsub,var,len)
#             var = var + 2
#             LO_LIMIT,var=get_r(4,fsub,var,length)
#             if OPT_FLAG&64 == 64:
#                 LO_LIMIT = np.nan

#             HI_LIMIT,var=get_r(4,fsub,var,length)
#             if OPT_FLAG&128 == 128:
#                 HI_LIMIT = np.nan
                
#             var += 8
#             RTN_INDX=[]
#             for _ in range(RSLT_CNT):
#                 Res,var=get_u(2,fsub,var,length)
#                 RTN_INDX.append(Res)
#             # try:
#                 #jump=8+2*rslt #RTN_ICNT

#             UNITS,var=get_cn(fsub,var,length)
#         except:
#             LO_LIMIT = np.nan
#             HI_LIMIT = np.nan
#             UNITS = ''
#             RES_SCAL = 0
#             RSLT_CNT = 0
#             RTN_INDX=[]
#             duplicateTestNumFlag = True
#             print(f"MPR duplicate: {tnum}")

#         tnIndexPerPin = []
#         try:
#             parameter = containers.testListGlobal[tnum]
#             if len(RTN_INDX) > 0:
#                 parameter.pins = RTN_INDX

#             for pin in parameter.pins:
#                 tnumPin = f"{tnum} - {containers.pinList[pin]}"
#                 tnumPerPin.append(tnumPin)
#                 parameterPerPin = containers.testListLocal[tnumPin]
#                 tnIndexPerPin.append(parameterPerPin.index)

#         except KeyError as e2:

#             tnIndex = containers.AddTestGlobal(True,tnum,unit = containers.prefixes[RES_SCAL+12]+UNITS, power = RES_SCAL , testNumber = TEST_NUM,pins=RTN_INDX,testType="M",testName = TEST_TXT)
#             parameter = containers.testListGlobal[tnum]
#             if len(RTN_INDX) > 0:
#                 parameter.pins = RTN_INDX

#             if not duplicateTestNumFlag:
#                 for  pin in RTN_INDX:
#                     tnumPin = f"{tnum} - {containers.pinList[pin]}"
#                     tnumPerPin.append(tnumPin)
#                     index = containers.AddTestGlobal(True,tnumPin,unit = containers.prefixes[RES_SCAL+12]+UNITS, power = RES_SCAL , testNumber = TEST_NUM,testType="M",testName = f"{TEST_TXT} {containers.pinList[pin]}" )
#                     tnIndexPerPin.append(index)
        
#         power = parameter.power
#         tnIndex = parameter.index
#         UNITS=containers.prefixes[power+12]+UNITS
#         LO_LIMIT *= 10**power
#         HI_LIMIT *= 10**power

#         kwargs={
#             #'index'     :tnIndex,
#             'groupName'  :containers.groupName,
#             #'testName'  :TEST_TXT,
#             'testNumber':TEST_NUM,
#             'unit'      :UNITS,
#             'HL'        :HI_LIMIT,
#             'LL'        :LO_LIMIT,
#             'power'     :power,
#             'pins'      :RTN_INDX,
#             'testType'  :'M',
#             'duplicateTN' : duplicateTestNumFlag
#         }
#         for item in containers.touchdownInfo:
#             item.extend([np.nan]*(RSLT_CNT+1))

#         tnIndex = containers.AddTestLocal(testItem = tnum,testName = TEST_TXT, **kwargs)
#         containers.touchdownInfo[siteIndex][tnIndex+containers.colPadding] = RESULTave

#         if not duplicateTestNumFlag:
#             for i, (pin,pinIndex) in enumerate(zip(tnumPerPin,parameter.pins)):
#                 tnIndex=containers.AddTestLocal(testItem = pin, testName = f"{TEST_TXT} {containers.pinList[pinIndex]}" , **kwargs)
#                 containers.touchdownInfo[siteIndex][tnIndex+containers.colPadding] = RESULTppin[i]

#     if containers.debugFlag:
#         containers.DebuggerStopTimer(record)

#         parameter = containers.testListLocal[tnum]

#         data=\
#         f"TEST_NUM: {TEST_NUM} \
#         RESULT: {RESULTave} \
#         SITE_NUM: {SITE_NUM} \
#         TEST_TXT: {TEST_TXT} \
#         LO_LIMIT: {parameter.LL} \
#         HI_LIMIT: {parameter.HL} \
#         UNITS: {parameter.unit} \
#         RES_SCAL: {parameter.power} \
#         RSLT_CNT: {RSLT_CNT}\n"  

#         containers.DebuggerWrite(record,data)
#         containers.DebuggerCount(record)

@parse_record
def MRR(data: RecordContainer): 

    FINISH_T,var=get_u(4,data)
    FINISH_T=datetime(1970,1,1,0,0,0) + timedelta(seconds=FINISH_T)
    DISP_COD,var=get_c(1,data)
    USR_DESC,var=get_cn(data)
    EXC_DESC,var=get_cn(data)

    return MRRRecord(FINISH_T, DISP_COD, USR_DESC, EXC_DESC)

@parse_record
def NULLREC(data: RecordContainer): 

    CONTENTS = get_all(data)

    return NULREcord(CONTENTS)

@parse_record
def PCR(data: RecordContainer): 

    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)
    PART_CNT = get_u(4,data)
    RTST_CNT = get_u(4,data)
    ABRT_CNT = get_u(4,data)
    GOOD_CNT = get_u(4,data)
    FUNC_CNT = get_u(4,data)

    return PCRRecord(HEAD_NUM, SITE_NUM, PART_CNT, RTST_CNT, ABRT_CNT, GOOD_CNT, FUNC_CNT)
    
@parse_record
def PGR(data: RecordContainer): 

    GRP_INDX = get_u(2,data)
    GRP_NAM = get_cn(data)
    INDX_CNT = get_u(2,data)
    PMR_INDX = get_u_arr(2, INDX_CNT, data)

    return PGRRecord(GRP_INDX, GRP_NAM, INDX_CNT, PMR_INDX)

@parse_record
def PIR(data: RecordContainer): 

    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)
    
    return PIRRecord(HEAD_NUM, SITE_NUM)

@parse_record
def PLR(data: RecordContainer): 
    
    GRP_CNT = get_u(2,data)
    GRP_INDX = get_u_arr(2, GRP_CNT, data)
    GRP_MODE = get_u_arr(1, GRP_CNT, data)
    GRP_RADX = get_u_arr(1, GRP_CNT, data)
    PGM_CHAR = get_cn_arr(1, GRP_CNT, data)
    RTN_CHAR = get_cn_arr(1, GRP_CNT, data)
    PGM_CHAL = get_cn_arr(1, GRP_CNT, data)
    RTN_CHAL = get_cn_arr(1, GRP_CNT, data)

    return PLRRecord(GRP_CNT, GRP_INDX, GRP_MODE, GRP_RADX, PGM_CHAR, RTN_CHAR, PGM_CHAL, RTN_CHAL)

@parse_record
def PMR(data: RecordContainer): 

    PMR_INDX = get_u(2,data)
    CHAN_TYP = get_u(2,data)
    CHAN_NAM = get_cn(data)
    PHY_NAM = get_cn(data)
    LOG_NAM = get_cn(data)
    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)

    return PMRRecord(PMR_INDX, CHAN_TYP, CHAN_NAM, PHY_NAM, LOG_NAM, HEAD_NUM, SITE_NUM)

@parse_record
def PRR(data: RecordContainer):
    
    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)
    PART_FLG = get_b(1,data)
    NUM_TEST = get_u(2,data)
    HARD_BIN = get_u(2,data)
    SOFT_BIN = get_u(2,data)
    X_COORD = get_u(2,data)
    Y_COORD = get_u(2,data)
    TEST_T = get_u(4,data)
    TEST_T=TEST_T/1000
    PART_ID = get_cn(data)
    PART_TXT = get_cn(data)
    PART_FIX = get_bn(data) #B*n

    return PRRRecord(HEAD_NUM, SITE_NUM, PART_FLG, NUM_TEST, 
                     HARD_BIN, SOFT_BIN, X_COORD, Y_COORD, 
                     TEST_T, PART_ID, PART_TXT, PART_FIX)

@parse_record
def PTR(data: RecordContainer):

    TEST_NUM = get_u(4,data)
    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)
    TEST_FLG = get_b(1,data)
    PARM_FLG = get_b(1,data)
    RESULT = get_r(4,data)
    TEST_TXT = get_cn(data)
    ALARM_ID = get_cn(data)

    OPT_FLAG = get_b(1,data) #B1

    RES_SCAL = get_i(1,data)
    LLM_SCAL = get_u(1,data)
    HLM_SCAL = get_u(1,data)

    LO_LIMIT = get_r(4,data)
    if OPT_FLAG&64 == 64:
        LO_LIMIT = np.nan
    HI_LIMIT = get_r(4,data)
    if OPT_FLAG&128 == 128:
        HI_LIMIT = np.nan
    UNITS = get_cn(data)
    
    C_RESFMT = get_cn(data)
    C_LLMFMT = get_cn(data)
    C_HLMFMT = get_cn(data)
    LO_SPEC = get_r(4,data)
    HI_SPEC = get_r(4,data)

    return PTRRecord(TEST_NUM, HEAD_NUM, SITE_NUM, TEST_FLG, 
                     PARM_FLG, RESULT, TEST_TXT, ALARM_ID, 
                     OPT_FLAG, RES_SCAL, LLM_SCAL, HLM_SCAL, 
                     LO_LIMIT, HI_LIMIT, UNITS, C_RESFMT,
                     C_LLMFMT, C_HLMFMT, LO_SPEC, HI_SPEC)

# def PTR2(fsub,length,containers):
    

#     if containers.debugFlag:
#         record="PTR"
#         containers.DebuggerWrite("RECfile",f"{record}\n")
#         containers.DebuggerStartTimer(record)

#     TEST_NUM,var=get_u(4,fsub,0,length)
#     #HEAD_NUM,var=MBgetU(1,fsub,var,len)
#     var = var +1 
#     SITE_NUM,var=get_u(1,fsub,var,length)
#     #TEST_FLG,var=MBgetB(1,fsub,var,len)
#     #PARM_FLG,var=MBgetB(1,fsub,var,len)
#     var = var +2
#     RESULT,var=get_r(4,fsub,var,length)
#     # if math.isinf(RESULT):
#     #     RESULT = np.nan
#     TEST_TXT,var=get_cn(fsub,var,length)
#     TEST_TXT=TEST_TXT.replace(",", " ")
#     tnum = f"{TEST_NUM} {TEST_TXT}"
#     siteIndex = containers.siteList[SITE_NUM]

#     try:
#         tnIndex = containers.testListLocal[tnum].index
#         containers.touchdownInfo[siteIndex][tnIndex+containers.colPadding] = RESULT
#     except KeyError as e:
#         #print (f"PTR Local:{e}")
#         try:
#             ALARM_ID,var=get_cn(fsub,var,length)
#             OPT_FLAG,var=get_u(1,fsub,var,length) #B1
#             RES_SCAL,var=get_i(1,fsub,var,length)
#             #LLM_SCAL,var=MBgetU(1,fsub,var,len)
#             #HLM_SCAL,var=MBgetU(1,fsub,var,len)
#             var = var +2
#             LO_LIMIT,var=get_r(4,fsub,var,length)
#             if OPT_FLAG&64 == 64:
#                 LO_LIMIT = np.nan
#             HI_LIMIT,var=get_r(4,fsub,var,length)
#             if OPT_FLAG&128 == 128:
#                 HI_LIMIT = np.nan
#             UNITS,var=get_cn(fsub,var,length)
#         except:
#             LO_LIMIT = np.nan
#             HI_LIMIT = np.nan
#             UNITS = ''
#             RES_SCAL = 0
#             print(f"PTR duplicate: {tnum}")


#         try:
#             parameter = containers.testListGlobal[tnum]

#         except KeyError as e2:
#             #print (f"PTR GLobal:{e2}")
            
#             tnIndex = containers.AddTestGlobal(True,tnum,unit = containers.prefixes[RES_SCAL+12]+UNITS, power = RES_SCAL , testNumber = TEST_NUM,testType = "P")
#             parameter = containers.testListGlobal[tnum]
        
#         power = parameter.power
#         tnIndex = parameter.index
#         UNITS=containers.prefixes[power+12]+UNITS
#         LO_LIMIT *= 10**power
#         HI_LIMIT *= 10**power

#         kwargs={
#             #'index'     :tnIndex,
#             'groupName'  :containers.groupName,
#             'testName'  :TEST_TXT,
#             'testNumber':TEST_NUM,
#             'testItem'  :tnum,
#             'unit'      :UNITS,
#             'HL'        :HI_LIMIT,
#             'LL'        :LO_LIMIT,
#             'power'     :power,
#             'testType'  :'P'
#         }

#         for item in containers.touchdownInfo:
#             item.append(np.nan)
#         tnIndex = containers.AddTestLocal(**kwargs)
#         containers.touchdownInfo[siteIndex][tnIndex+containers.colPadding] = RESULT



#     if containers.debugFlag:
#         containers.DebuggerStopTimer(record)
#         parameter = containers.testListLocal[tnum]
#         data=f"\
#         TEST_NUM: {TEST_NUM} \
#         RESULT: {RESULT} \
#         SITE_NUM: {SITE_NUM} \
#         TEST_TXT: {TEST_TXT} \
#         LO_LIMIT: {parameter.LL} \
#         HI_LIMIT: {parameter.HL} \
#         UNITS: {parameter.unit} \
#         RES_SCAL: {parameter.power}\n"  

#         containers.DebuggerWrite(record,data)
#         containers.DebuggerCount(record)
                                      
@parse_record
def RDR(data: RecordContainer):
    
    NUM_BINS = get_u(2,data)
    RTST_BIN = get_u_arr(2, NUM_BINS, data)

    return RDRRecord(NUM_BINS, RTST_BIN)

@parse_record
def SBR(data: RecordContainer):

    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)
    SBIN_NUM = get_u(2,data)
    SBIN_CNT = get_u(4,data)
    SBIN_PF = get_c(1,data)
    SBIN_NAM = get_cn(data)

    return SBRRecord(HEAD_NUM, SITE_NUM, SBIN_NUM, SBIN_CNT, SBIN_PF, SBIN_NAM)

@parse_record
def SDR(data: RecordContainer):

    HEAD_NUM = get_u(1,data)
    SITE_GRP = get_u(1,data)
    SITE_CNT = get_u(1,data)
    SITE_NUM = get_u_arr(1,SITE_CNT,data)
    HAND_TYP = get_cn(data)
    HAND_ID = get_cn(data)
    CARD_TYP = get_cn(data)
    CARD_ID = get_cn(data)
    LOAD_TYP = get_cn(data)
    LOAD_ID = get_cn(data)
    DIB_TYP = get_cn(data)
    DIB_ID = get_cn(data)
    CABL_TYP = get_cn(data)
    CABL_ID = get_cn(data)
    CONT_TYP = get_cn(data)
    CONT_ID = get_cn(data)
    LASR_TYP = get_cn(data)
    LASR_ID = get_cn(data)
    EXTR_TYP = get_cn(data)
    EXTR_ID = get_cn(data)

    return SDRRecord(HEAD_NUM, SITE_GRP, SITE_CNT, SITE_NUM,
                     HAND_TYP, HAND_ID, CARD_TYP, CARD_ID,
                     LOAD_TYP, LOAD_ID, DIB_TYP, DIB_ID,
                     CABL_TYP, CABL_ID, CONT_TYP, CONT_ID,
                     LASR_TYP, LASR_ID, EXTR_TYP, EXTR_ID)

@parse_record
def TSR(data: RecordContainer):

    HEAD_NUM = get_u(1,data)
    SITE_NUM = get_u(1,data)
    TEST_TYP = get_c(1,data)
    TEST_NUM = get_u(4,data)
    EXEC_CNT = get_u(4,data)
    FAIL_CNT = get_u(4,data)
    ALRM_CNT = get_u(4,data)
    TEST_NAM = get_cn(data)
    SEQ_NAME = get_cn(data)
    TEST_LBL = get_cn(data)
    OPT_FLAG = get_b(1,data)
    TEST_TIM = get_r(4,data)
    TEST_MIN = get_r(4,data)
    TEST_MAX = get_r(4,data)
    TST_SUMS = get_r(4,data)
    TST_SQRS = get_r(4,data)

    return TSRRecord(HEAD_NUM, SITE_NUM, TEST_TYP, TEST_NUM,
                     EXEC_CNT, FAIL_CNT, ALRM_CNT, TEST_NAM, 
                     SEQ_NAME, TEST_LBL, OPT_FLAG, TEST_TIM, 
                     TEST_MIN, TEST_MAX, TST_SUMS, TST_SQRS)

@parse_record
def WCR(data: RecordContainer):
    
    WAFR_SIZ = get_r(4,data)
    DIE_HT = get_r(4,data)
    DIE_WID = get_r(4,data)
    WF_UNITS = get_u(1,data)
    WF_FLAT = get_c(1,data)
    CENTER_X = get_i(2,data)
    CENTER_Y = get_i(2,data)
    POS_X = get_c(1,data)
    POS_Y = get_c(1,data)

    return WCRRecord(DIE_HT, DIE_WID, WF_UNITS, WF_FLAT, CENTER_X, CENTER_Y, POS_X, POS_Y)

@parse_record
def WIR(data: RecordContainer):

    HEAD_NUM = get_u(1,data)
    SITE_GRP = get_u(1,data)
    START_T = get_u(4,data)
    WAFER_ID = get_cn(data)

    return WIRRecord(HEAD_NUM, SITE_GRP, START_T, WAFER_ID)

@parse_record
def WRR(data: RecordContainer):
    
    HEAD_NUM = get_u(1,data)
    SITE_GRP = get_u(1,data)
    FINISH_T = get_u(4,data)
    PART_CNT = get_u(4,data)
    RTST_CNT = get_u(4,data)
    ABRT_CNT = get_u(4,data)
    GOOD_CNT = get_u(4,data)
    FUNC_CNT = get_u(4,data)
    WAFER_ID = get_cn(data)
    FABWF_ID = get_cn(data)
    FRAME_ID = get_cn(data)
    MASK_ID = get_cn(data)
    USR_DESC = get_cn(data)
    EXC_DESC = get_cn(data)

    return WRRRecord(HEAD_NUM, SITE_GRP, FINISH_T, PART_CNT,
                     RTST_CNT, ABRT_CNT, GOOD_CNT, FUNC_CNT,
                     WAFER_ID, FABWF_ID, FRAME_ID, MASK_ID,
                     USR_DESC, EXC_DESC)




