
from stdf_parser.RECRecipes import *

class Writer:
    def __init__(self, filepath):
        self.file = open(filepath, 'wb')
        self.data = None


    def collect(self, record):
        if self.data is None:
            self.data = record.to_bytes()
        else:
            self.data += record.to_bytes()        

    def save(self):
        self.file.write(self.data)
        self.file.close()

    def write_MIR(self, data:dict):
        record = MIRRecipe(data)
        self.collect(record)

    def write_PTR(self, data:dict):
        record = PTRRecipe(data)
        self.collect(record)

    def write_FAR(self, data:dict):
        record = FARRecipe(data)
        self.collect(record)

    def write_PIR(self, data:dict):
        record = PIRRecipe(data)
        self.collect(record)

    def write_PRR(self, data:dict):
        record = PRRRecipe(data)
        self.collect(record)

    def write_MRR(self, data:dict):
        record = MRRRecipe(data)
        self.collect(record)

    def write_HBR(self, data:dict):
        record = HBRRecipe(data)
        self.collect(record)

    def write_SBR(self, data:dict):
        record = SBRRecipe(data)
        self.collect(record)

    def write_TSR(self, data:dict):
        record = TSRRecipe(data)
        self.collect(record)

    def write_PCR(self, data:dict):
        record = PCRRecipe(data)
        self.collect(record)


if __name__ == "__main__":
    test = Writer("test.stdf")


    test.write_PIR({})

    data = {
        "TEST_NUM":10 ,
        "HEAD_NUM": 1,
        "SITE_NUM": 0,
        "TEST_FLG": 0x40,
        "PARM_FLG": 0,
        "RESULT": 67.0,
        "TEST_TXT": "X Coordinate",
        "ALARM_ID": None,
        "OPT_FLAG": 0xCE,
        "RES_SCAL": 0,
        "LLM_SCAL": 0,
        "HLM_SCAL": 0,
        "LO_LIMIT": 0,
        "HI_LIMIT": 0,
        "UNITS": None,
        }
    
    test.write_PTR(data)

    test.write_PRR({
        "HARD_BIN":1,
        "SOFT_BIN": 1,
        "PART_FLG": 0x08,
        "NUM_TEST": 1,
        "HARD_BIN": 8,
        "SOFT_BIN": 13,
        "X_COORD": 67.0,
        "Y_COORD": 41,
     #  "PART_ID": 0x31
        })



    
    test.save()