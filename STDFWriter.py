
from RECRecipes import *

class Writer:
    def __init__(self, filepath):
        self.file = open(filepath, 'wb').close()
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

    def write_FTR(self, data:dict):
        record = FTRRecipe(data)
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

    

    