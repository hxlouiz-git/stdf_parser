# import array
# from multiprocessing import Array
# from reprlib import aRepr
import struct
# import time
import numpy as np
# from datetime import datetime, timedelta
# import matplotlib.pyplot as plt
# import tkinter as tk
# from tkinter import *
# from tkinter import filedialog
# from tkinter import ttk
# import os
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# from matplotlib.ticker import PercentFormatter

# from textwrap import wrap


# def MBgetR(val,fsub,pos,length):
#     try:
#         stop=val+pos
#         c = 0
#         content = fsub[pos:stop]
#         for i in range(val):
#             c |= content[i] << (8 * i)
#         ret = struct.unpack('f', struct.pack('I', c))[0]

#         return ret, stop
#     except:
#         return np.nan, val+pos
    

def get_r_arr(val,count,data):
    ret = []
    for _ in range(count):
        ret.append(get_r(val,data))
    
    return ret

def get_u_arr(val,count,data):
    ret = []
    for _ in range(count):
        ret.append(get_u(val,data))
    
    return ret

def get_cn_arr(count,data):
    ret = []
    for _ in range(count):
        ret.append(get_cn(data))
    
    return ret


def get_r(val,data):
    try:
        c = 0
        content =  data.read(val)
        for i in range(val):
            c |= content[i] << (8 * i)
        ret = struct.unpack('f', struct.pack('I', c))[0]

        return ret
    except:
        return np.nan

def get_u(val,data):

    ret =0
    try:
        content = data.read(val)
        for i in range(val):
            ret |= content[i] << (8 * i)

        return ret
    except:
        return np.nan


def get_all(data):

    val = data.length
    content = data.read(val)

    for i in range(val):
        ret |= content[i] << (8 * i)

    return ret

def get_i(val,data):

    content = data.read(val)
    ret = int.from_bytes(content,'little', signed=True)

    return ret

def get_cn(data):
    try:
        length = data.read(1)
        ret = data.read(length).decode('ascii')

    #   print("MBgetC=",ret)
        return ret
    except:
        return 'no data'
    
def get_dn(data):
    try:
        bit_length = get_u(2, data)
        byte_length = (bit_length // 8) + (bit_length % 8)
  
        ret = get_b(byte_length, data)

        return ret
    except:
        return 0


def get_c(val,data):

    ret = data.read(val).decode('ascii')

    return ret


def get_b(val,data):

    ret = data.read(val)

    return ret

def get_bn(data):

    try:
        length = data.read(1)
        ret = get_b(length, data)

    #   print("MBgetC=",ret)
        return ret
    except:
        return 0

