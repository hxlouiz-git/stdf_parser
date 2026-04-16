from stdf_parser.ByteFuncs import get_u, get_i
from stdf_parser.RECFuncs import get_headers, PTR
from stdf_parser.RecordTuples import HeaderRecord, PTRRecord

import os

filename = "S65731.2_ADuM4185_IC3_v30905p01a_STS-232_20250728_74228.stdf"

with open(filename, "rb") as f:
    fsize = os.path.getsize(filename)
    initial_chunk = f.read(100000)
    pos = initial_chunk.find(b'\x00\x0a')
    f.seek(pos - 2, 0)
    pos = f.tell()

    while pos < fsize:

        fsub = f.read(4)
        
        var: HeaderRecord = get_headers(fsub,4)       
        recLEN = var.REC_LEN
        recTYP = var.REC_TYP
        recSUB = var.REC_SUB

        #print(f"REC_LEN: {recLEN}, REC_TYP: {recTYP}, REC_SUB: {recSUB}")
        fsub = f.read(recLEN)


        if recTYP==15:
            if recSUB==10:      # PTR()   
                var:PTRRecord = PTR(fsub,recLEN)

                print(var)