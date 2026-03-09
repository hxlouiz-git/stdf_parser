
from time import time
import os
class Debugger():

    record_timers={}
    record_outputs={}
    record_count={}
    file_path = None
        
    def reset():
        Debugger.record_timers.clear()
        Debugger.record_outputs.clear()
        Debugger.record_count.clear()
        Debugger.file_path = None

    def open_file(record):
        if not os.path.exists(Debugger.file_path):
            os.makedirs(Debugger.file_path)

        Debugger.record_outputs[record] = open(f"{Debugger.file_path}/{record}.txt",'w')

    def count(record):
        try: 
            Debugger.record_count[record]+=1
        except:
            Debugger.record_count[record] = 0
            Debugger.record_count[record] += 1

    def write_file(record,data):
        Debugger.record_outputs[record].write(data)

    def create_timer(name):
        Debugger.record_timers[name]=Timer()

    def start_timer(name):
        try: 
            Debugger.record_timers[name].Start()
        except:
            Debugger.create_timer(name)


    def stop_timer(name):
        Debugger.record_timers[name].Stop()

    def print_timers():
        for key, timer in Debugger.record_timers.items():
            try:
                print(f"{key} time: {timer.totalTime} Count: {Debugger.record_count[key]}")
            except KeyError:
                print(f"{key} time: {timer.totalTime}")

    def write(name,data):
        try:
            Debugger.WriteFile(name,data)
        except:
            Debugger.OpenFile(name)
            Debugger.WriteFile(name,data)
        

class Timer():
    def __init__(self):
        self.startFlag = False
        self.totalTime = 0
        self.startTime = None
        self.start()

    def start(self):
        self.startTime = time.time()

    def stop(self):
        self.totalTime += time.time() - self.startTime


# class DebugItems():
#     def __init__(self):
#         self.record_timers={}
#         self.record_outputs={}
#         self.record_count={}
#         self.file_path = None
        
#     def reset(self):
#         self.record_timers.clear()
#         self.record_outputs.clear()
#         self.record_count.clear()

#     def open_file(self,record):
#         if not os.path.exists(self.file_path):
#             os.makedirs(self.file_path)

#         self.record_outputs[record] = open(f"{self.file_path}/{record}.txt",'w')

#     def record_count(self,record):
#         try: 
#             self.record_count[record]+=1
#         except:
#             self.record_count[record] = 0
#             self.record_count[record] += 1

#     def write_file(self,record,data):
#         self.record_outputs[record].write(data)

#     def create_timer(self,name):
#         self.record_timers[name]=Timer()

#     def start_timer(self,name):
#         try: 
#             self.record_timers[name].Start()
#         except:
#             self.create_timer(name)


#     def stop_timer(self,name):
#         self.record_timers[name].Stop()

#     def print_timers(self):
#         for key, timer in self.record_timers.items():
#             try:
#                 print(f"{key} time: {timer.totalTime} Count: {self.record_count[key]}")
#             except KeyError:
#                 print(f"{key} time: {timer.totalTime}")

# class Timer():
#     def __init__(self):
#         self.startFlag = False
#         self.totalTime = 0
#         self.startTime = None
#         self.start()

#     def start(self):
#         self.startTime = time.time()

#     def stop(self):
#         self.totalTime += time.time() - self.startTime
