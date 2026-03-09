
from functools import wraps
from RECFuncs import ATR, PIR, Debugger



Debugger.file_path = "."

debug_mode = False


ATR(contents=None,lenght=None,debug_enabled=debug_mode)


PIR(fsub=None,length=None,debug_enabled=debug_mode)