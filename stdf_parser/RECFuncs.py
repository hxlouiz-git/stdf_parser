
from datetime import datetime, timedelta
from functools import wraps
import numpy as np


from stdf_parser.Debugger import Debugger

from stdf_parser.ByteFuncs import get_u , get_c ,get_cn, get_r, get_b, get_bn, get_i, get_dn, get_all, get_r_arr, get_u_arr, get_cn_arr, RecordTruncated
from stdf_parser.RecordTuples import *
import traceback



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
            raise RecordTruncated()
    
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
        debug_enabled = kwargs['debug_enabled'] if 'debug_enabled' in kwargs else getattr(args[0], 'debugFlag', False)

        if debug_enabled:
            record=func.__name__
            print(f"Debug: Starting {record} with args: {args}, kwargs: {kwargs}")
            Debugger.write("RECfile",f"{record}\n")
            Debugger.start_timer(record)

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
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

_DISPATCH = {
    (0,  10): lambda b, n: FAR(b, n),
    (0,  20): lambda b, n: ATR(b, n),
    (1,  10): lambda b, n: MIR(b, n),
    (1,  20): lambda b, n: MRR(b, n),
    (1,  30): lambda b, n: PCR(b, n),
    (1,  40): lambda b, n: HBR(b, n),
    (1,  50): lambda b, n: SBR(b, n),
    (1,  60): lambda b, n: PMR(b, n),
    (1,  62): lambda b, n: PGR(b, n),
    (1,  63): lambda b, n: PLR(b, n),
    (1,  70): lambda b, n: RDR(b, n),
    (1,  80): lambda b, n: SDR(b, n),
    (2,  10): lambda b, n: WIR(b, n),
    (2,  20): lambda b, n: WRR(b, n),
    (2,  30): lambda b, n: WCR(b, n),
    (5,  10): lambda b, n: PIR(b, n),
    (5,  20): lambda b, n: PRR(b, n),
    (10, 30): lambda b, n: TSR(b, n),
    (15, 10): lambda b, n: PTR(b, n),
    (15, 15): lambda b, n: MPR(b, n),
    (15, 20): lambda b, n: FTR(b, n),
    (20, 10): lambda b, n: BPS(b, n),
    (20, 20): lambda b, n: EPS(b, n),
    (50, 10): lambda b, n: GDR(b, n),
    (50, 30): lambda b, n: DTR(b, n),
}

def RecordSelect(f):
    header_bytes = f.read(4)
    header = get_headers(header_bytes, 4)
    REC_LEN, REC_TYP, REC_SUB = header.REC_LEN, header.REC_TYP, header.REC_SUB
    body = f.read(REC_LEN)
    pos = f.tell()

    parser = _DISPATCH.get((REC_TYP, REC_SUB))

    if parser is not None:
        record = parser(body, REC_LEN)
    else:
        known_type = any(t == REC_TYP for t, _ in _DISPATCH)
        if known_type:
            print(f"Unrecognized record sub type REC_TYP: {REC_TYP} REC_SUB: {REC_SUB}, will attempt to skip.")
        else:
            print(f"Unrecognized record type REC_TYP: {REC_TYP} REC_SUB: {REC_SUB}, will now terminate. Try ParamOnly mode or send STDF to developer for checking")
            f.seek(0, 2)
        record = NULLREC(body, REC_LEN)

    return pos, record




@parse_record
def get_headers(data: RecordContainer):
    REC_LEN=get_u(2,data)
    REC_TYP=get_u(1,data)
    REC_SUB=get_u(1,data)

    return HeaderRecord(REC_LEN, REC_TYP, REC_SUB)

@parse_record
def ATR(data: RecordContainer):

    fields = {}
    try:
        fields['MOD_TIM'] = get_u(4, data)
        fields['CMD_LINE'] = get_cn(data)
    except RecordTruncated:
        pass

    return ATRRecord(**fields)

@parse_record
def BPS(data: RecordContainer):

    fields = {}
    try:
        fields['SEQ_NAME'] = get_cn(data)
    except RecordTruncated:
        pass

    return BPSRecord(**fields)

@parse_record
def DTR(data: RecordContainer):

    fields = {}
    try:
        fields['TEXT_DAT'] = get_cn(data)
    except RecordTruncated:
        pass

    return DTRRecord(**fields)

@parse_record
def EPS(data: RecordContainer):
    
    return None

@parse_record
def FAR(data: RecordContainer):

    fields = {}
    try:
        fields['CPU_TYPE'] = get_u(1, data)
        fields['STDF_VER'] = get_u(1, data)
    except RecordTruncated:
        pass

    return FARRecord(**fields)

@parse_record
def FTR(data: RecordContainer):

    fields = {}
    try:
        fields['TEST_NUM'] = get_u(4,data)
        fields['HEAD_NUM'] = get_u(1,data)
        fields['SITE_NUM'] = get_u(1,data)
        fields['TEST_FLG'] = get_u(1,data)
        fields['OPT_FLG']  = get_b(1,data)
        fields['CYCL_CNT'] = get_u(4,data)
        fields['REL_VADR'] = get_u(4,data)
        fields['REPT_CNT'] = get_u(4,data)
        fields['NUM_FAIL'] = get_u(4,data)
        fields['XFAIL_AD'] = get_i(4,data)
        fields['YFAIL_AD'] = get_i(4,data)
        fields['VECT_OFF'] = get_i(2,data)
        fields['RTN_ICNT'] = get_u(2,data)
        fields['PGM_ICNT'] = get_u(2,data)
        fields['RTN_INDX'] = get_u(2*fields['RTN_ICNT'],data)
        fields['RTN_STAT'] = get_u((fields['RTN_ICNT'] // 2) + (fields['RTN_ICNT'] % 2),data)
        fields['PGM_INDX'] = get_u(2*fields['PGM_ICNT'],data)
        fields['PGM_STAT'] = get_u((fields['PGM_ICNT'] // 2) + (fields['PGM_ICNT'] % 2),data)
        fields['FAIL_PIN'] = get_dn(data)
        fields['VECT_NAME'] = get_cn(data)
        fields['TIME_SET'] = get_cn(data)
        fields['OP_CODE']  = get_cn(data)
        fields['TEST_TXT'] = get_cn(data)
        fields['ALARM_ID'] = get_cn(data)
        fields['PROG_TXT'] = get_cn(data)
        fields['RSLT_TXT'] = get_cn(data)
        fields['PATG_NUM'] = get_u(1,data)
        fields['SPIN_MAP'] = get_dn(data)
    except RecordTruncated:
        pass

    if 'TEST_FLG' in fields:
        fields['RESULT'] = 1 if fields['TEST_FLG'] & 128 == 0 else 0

    return FTRRecord(**fields)

@parse_record
def GDR(data: RecordContainer):

    return None
 
@parse_record
def HBR(data: RecordContainer):

    fields = {}
    try:
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_NUM'] = get_u(1, data)
        fields['HBIN_NUM'] = get_u(2, data)
        fields['HBIN_CNT'] = get_u(4, data)
        fields['HBIN_PF']  = get_c(1, data)
        fields['HBIN_NAM'] = get_cn(data)
    except RecordTruncated:
        pass

    return HBRRecord(**fields)

@parse_record
def MIR(data: RecordContainer):

    fields = {}
    try:
        fields['SETUP_T']   = datetime(1970,1,1,0,0,0) + timedelta(seconds=get_u(4,data))
        fields['START_T']   = datetime(1970,1,1,0,0,0) + timedelta(seconds=get_u(4,data))
        fields['STAT_NUM']  = get_u(1, data)
        fields['MODE_COD']  = get_c(1, data)
        fields['RTST_COD']  = get_c(1, data)
        fields['PROT_COD']  = get_c(1, data)
        fields['BURN_TIM']  = get_u(2, data)
        fields['CMOD_COD']  = get_c(1, data)
        fields['LOT_ID']    = get_cn(data)
        fields['PART_TYP']  = get_cn(data)
        fields['NODE_NAM']  = get_cn(data)
        fields['TSTR_TYP']  = get_cn(data)
        fields['JOB_NAM']   = get_cn(data)
        fields['JOB_REV']   = get_cn(data)
        fields['SBLOT_ID']  = get_cn(data)
        fields['OPER_NAM']  = get_cn(data)
        fields['EXEC_TYP']  = get_cn(data)
        fields['EXEC_VER']  = get_cn(data)
        fields['TEST_COD']  = get_cn(data)
        fields['TST_TEMP']  = get_cn(data)
        fields['USER_TXT']  = get_cn(data)
        fields['AUX_FILE']  = get_cn(data)
        fields['PKG_TYP']   = get_cn(data)
        fields['FAMILY_ID'] = get_cn(data)
        fields['DATE_COD']  = get_cn(data)
        fields['FACIL_ID']  = get_cn(data)
        fields['FLOOR_ID']  = get_cn(data)
        fields['PROC_ID']   = get_cn(data)
        fields['OPER_FRQ']  = get_cn(data)
        fields['SPEC_NAM']  = get_cn(data)
        fields['SPEC_VER']  = get_cn(data)
        fields['FLOW_ID']   = get_cn(data)
        fields['SETUP_ID']  = get_cn(data)
        fields['DSGN_REV']  = get_cn(data)
        fields['ENG_ID']    = get_cn(data)
        fields['ROM_COD']   = get_cn(data)
        fields['SERL_NUM']  = get_cn(data)
        fields['SUPR_NAM']  = get_cn(data)
    except RecordTruncated:
        pass

    return MIRRecord(**fields)

@parse_record
def MPR(data: RecordContainer):

    fields = {}
    try:
        fields['TEST_NUM'] = get_u(4, data)
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_NUM'] = get_u(1, data)
        fields['TEST_FLG'] = get_b(1, data)
        fields['PARM_FLG'] = get_b(1, data)
        fields['RTN_ICNT'] = get_u(2, data)
        fields['RSLT_CNT'] = get_u(2, data)
        fields['RTN_STAT'] = get_u((fields['RTN_ICNT'] // 2) + (fields['RTN_ICNT'] % 2), data)
        fields['RTN_RSLT'] = get_r_arr(4, fields['RSLT_CNT'], data)
        fields['TEST_TXT'] = get_cn(data)
        fields['ALARM_ID'] = get_cn(data)
        fields['OPT_FLAG'] = get_b(1, data)
        fields['RES_SCAL'] = get_i(1, data)
        fields['LLM_SCAL'] = get_i(1, data)
        fields['HLM_SCAL'] = get_i(1, data)
        fields['LO_LIMIT'] = get_r(4, data)
        if fields['OPT_FLAG'][0] & 64 == 64:
            fields['LO_LIMIT'] = np.nan
        fields['HI_LIMIT'] = get_r(4, data)
        if fields['OPT_FLAG'][0] & 128 == 128:
            fields['HI_LIMIT'] = np.nan
        fields['START_IN'] = get_r(4, data)
        fields['INCR_IN']  = get_r(4, data)
        fields['RTN_INDX'] = get_u_arr(2, fields['RTN_ICNT'], data)
        fields['UNITS']    = get_cn(data)
        fields['UNITS_IN'] = get_cn(data)
        fields['C_RESFMT'] = get_cn(data)
        fields['C_LLMFMT'] = get_cn(data)
        fields['C_HLMFMT'] = get_cn(data)
        fields['LO_SPEC']  = get_r(4, data)
        fields['HI_SPEC']  = get_r(4, data)
    except RecordTruncated:
        pass

    return MPRRecord(**fields)


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

    fields = {}
    try:
        fields['FINISH_T'] = datetime(1970,1,1,0,0,0) + timedelta(seconds=get_u(4,data))
        fields['DISP_COD'] = get_c(1, data)
        fields['USR_DESC'] = get_cn(data)
        fields['EXC_DESC'] = get_cn(data)
    except RecordTruncated:
        pass

    return MRRRecord(**fields)

@parse_record
def NULLREC(data: RecordContainer): 

    CONTENTS = get_all(data)

    return NULREcord(CONTENTS)

@parse_record
def PCR(data: RecordContainer):

    fields = {}
    try:
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_NUM'] = get_u(1, data)
        fields['PART_CNT'] = get_u(4, data)
        fields['RTST_CNT'] = get_u(4, data)
        fields['ABRT_CNT'] = get_u(4, data)
        fields['GOOD_CNT'] = get_u(4, data)
        fields['FUNC_CNT'] = get_u(4, data)
    except RecordTruncated:
        pass

    return PCRRecord(**fields)
    
@parse_record
def PGR(data: RecordContainer):

    fields = {}
    try:
        fields['GRP_INDX'] = get_u(2, data)
        fields['GRP_NAM']  = get_cn(data)
        fields['INDX_CNT'] = get_u(2, data)
        fields['PMR_INDX'] = get_u_arr(2, fields['INDX_CNT'], data)
    except RecordTruncated:
        pass

    return PGRRecord(**fields)

@parse_record
def PIR(data: RecordContainer):

    fields = {}
    try:
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_NUM'] = get_u(1, data)
    except RecordTruncated:
        pass

    return PIRRecord(**fields)

@parse_record
def PLR(data: RecordContainer):

    fields = {}
    try:
        fields['GRP_CNT']  = get_u(2, data)
        fields['GRP_INDX'] = get_u_arr(2, fields['GRP_CNT'], data)
        fields['GRP_MODE'] = get_u_arr(1, fields['GRP_CNT'], data)
        fields['GRP_RADX'] = get_u_arr(1, fields['GRP_CNT'], data)
        fields['PGM_CHAR'] = get_cn_arr(1, fields['GRP_CNT'], data)
        fields['RTN_CHAR'] = get_cn_arr(1, fields['GRP_CNT'], data)
        fields['PGM_CHAL'] = get_cn_arr(1, fields['GRP_CNT'], data)
        fields['RTN_CHAL'] = get_cn_arr(1, fields['GRP_CNT'], data)
    except RecordTruncated:
        pass

    return PLRRecord(**fields)

@parse_record
def PMR(data: RecordContainer):

    fields = {}
    try:
        fields['PMR_INDX'] = get_u(2, data)
        fields['CHAN_TYP'] = get_u(2, data)
        fields['CHAN_NAM'] = get_cn(data)
        fields['PHY_NAM']  = get_cn(data)
        fields['LOG_NAM']  = get_cn(data)
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_NUM'] = get_u(1, data)
    except RecordTruncated:
        pass

    return PMRRecord(**fields)

@parse_record
def PRR(data: RecordContainer):

    fields = {}

    try:
    
        fields['HEAD_NUM'] = get_u(1,data)
        fields['SITE_NUM'] = get_u(1,data)
        fields['PART_FLG'] = get_b(1,data)
        fields['NUM_TEST'] = get_u(2,data)
        fields['HARD_BIN'] = get_u(2,data)
        fields['SOFT_BIN'] = get_u(2,data)
        fields['X_COORD'] = get_u(2,data)
        fields['Y_COORD'] = get_u(2,data)
        fields['TEST_T'] = get_u(4,data)
        fields['TEST_T'] = fields['TEST_T']/1000
        fields['PART_ID'] = get_cn(data)
        fields['PART_TXT'] = get_cn(data)
        fields['PART_FIX'] = get_bn(data) #B*n

    except RecordTruncated:
        pass

    return PRRRecord(**fields)

@parse_record
def PTR(data: RecordContainer):

    fields = {}
    try:
        fields['TEST_NUM'] = get_u(4,data)
        fields['HEAD_NUM'] = get_u(1,data)
        fields['SITE_NUM'] = get_u(1,data)
        fields['TEST_FLG'] = get_b(1,data)
        fields['PARM_FLG'] = get_b(1,data)
        fields['RESULT']   = get_r(4,data)
        fields['TEST_TXT'] = get_cn(data)
        fields['ALARM_ID'] = get_cn(data)
        fields['OPT_FLAG'] = get_b(1,data)
        fields['RES_SCAL'] = get_i(1,data)
        fields['LLM_SCAL'] = get_u(1,data)
        fields['HLM_SCAL'] = get_u(1,data)
        fields['LO_LIMIT'] = get_r(4,data)
        if fields['OPT_FLAG'][0]&64 == 64:
            fields['LO_LIMIT'] = np.nan
        fields['HI_LIMIT'] = get_r(4,data)
        if fields['OPT_FLAG'][0]&128 == 128:
            fields['HI_LIMIT'] = np.nan
        fields['UNITS']    = get_cn(data)
        fields['C_RESFMT'] = get_cn(data)
        fields['C_LLMFMT'] = get_cn(data)
        fields['C_HLMFMT'] = get_cn(data)
        fields['LO_SPEC']  = get_r(4,data)
        fields['HI_SPEC']  = get_r(4,data)
    except RecordTruncated:
        pass

    return PTRRecord(**fields)

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

    fields = {}
    try:
        fields['NUM_BINS'] = get_u(2, data)
        fields['RTST_BIN'] = get_u_arr(2, fields['NUM_BINS'], data)
    except RecordTruncated:
        pass

    return RDRRecord(**fields)

@parse_record
def SBR(data: RecordContainer):

    fields = {}
    try:
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_NUM'] = get_u(1, data)
        fields['SBIN_NUM'] = get_u(2, data)
        fields['SBIN_CNT'] = get_u(4, data)
        fields['SBIN_PF']  = get_c(1, data)
        fields['SBIN_NAM'] = get_cn(data)
    except RecordTruncated:
        pass

    return SBRRecord(**fields)

@parse_record
def SDR(data: RecordContainer):

    fields = {}
    try:
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_GRP'] = get_u(1, data)
        fields['SITE_CNT'] = get_u(1, data)
        fields['SITE_NUM'] = get_u_arr(1, fields['SITE_CNT'], data)
        fields['HAND_TYP'] = get_cn(data)
        fields['HAND_ID']  = get_cn(data)
        fields['CARD_TYP'] = get_cn(data)
        fields['CARD_ID']  = get_cn(data)
        fields['LOAD_TYP'] = get_cn(data)
        fields['LOAD_ID']  = get_cn(data)
        fields['DIB_TYP']  = get_cn(data)
        fields['DIB_ID']   = get_cn(data)
        fields['CABL_TYP'] = get_cn(data)
        fields['CABL_ID']  = get_cn(data)
        fields['CONT_TYP'] = get_cn(data)
        fields['CONT_ID']  = get_cn(data)
        fields['LASR_TYP'] = get_cn(data)
        fields['LASR_ID']  = get_cn(data)
        fields['EXTR_TYP'] = get_cn(data)
        fields['EXTR_ID']  = get_cn(data)
    except RecordTruncated:
        pass

    return SDRRecord(**fields)

@parse_record
def TSR(data: RecordContainer):

    fields = {}
    try:
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_NUM'] = get_u(1, data)
        fields['TEST_TYP'] = get_c(1, data)
        fields['TEST_NUM'] = get_u(4, data)
        fields['EXEC_CNT'] = get_u(4, data)
        fields['FAIL_CNT'] = get_u(4, data)
        fields['ALRM_CNT'] = get_u(4, data)
        fields['TEST_NAM'] = get_cn(data)
        fields['SEQ_NAME'] = get_cn(data)
        fields['TEST_LBL'] = get_cn(data)
        fields['OPT_FLAG'] = get_b(1, data)
        fields['TEST_TIM'] = get_r(4, data)
        fields['TEST_MIN'] = get_r(4, data)
        fields['TEST_MAX'] = get_r(4, data)
        fields['TST_SUMS'] = get_r(4, data)
        fields['TST_SQRS'] = get_r(4, data)
    except RecordTruncated:
        pass

    return TSRRecord(**fields)

@parse_record
def WCR(data: RecordContainer):

    fields = {}
    try:
        fields['WAFR_SIZ'] = get_r(4, data)
        fields['DIE_HT']   = get_r(4, data)
        fields['DIE_WID']  = get_r(4, data)
        fields['WF_UNITS'] = get_u(1, data)
        fields['WF_FLAT']  = get_c(1, data)
        fields['CENTER_X'] = get_i(2, data)
        fields['CENTER_Y'] = get_i(2, data)
        fields['POS_X']    = get_c(1, data)
        fields['POS_Y']    = get_c(1, data)
    except RecordTruncated:
        pass

    return WCRRecord(**fields)

@parse_record
def WIR(data: RecordContainer):

    fields = {}
    try:
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_GRP'] = get_u(1, data)
        fields['START_T']  = get_u(4, data)
        fields['WAFER_ID'] = get_cn(data)
    except RecordTruncated:
        pass

    return WIRRecord(**fields)

@parse_record
def WRR(data: RecordContainer):

    fields = {}
    try:
        fields['HEAD_NUM'] = get_u(1, data)
        fields['SITE_GRP'] = get_u(1, data)
        fields['FINISH_T'] = get_u(4, data)
        fields['PART_CNT'] = get_u(4, data)
        fields['RTST_CNT'] = get_u(4, data)
        fields['ABRT_CNT'] = get_u(4, data)
        fields['GOOD_CNT'] = get_u(4, data)
        fields['FUNC_CNT'] = get_u(4, data)
        fields['WAFER_ID'] = get_cn(data)
        fields['FABWF_ID'] = get_cn(data)
        fields['FRAME_ID'] = get_cn(data)
        fields['MASK_ID']  = get_cn(data)
        fields['USR_DESC'] = get_cn(data)
        fields['EXC_DESC'] = get_cn(data)
    except RecordTruncated:
        pass

    return WRRRecord(**fields)




