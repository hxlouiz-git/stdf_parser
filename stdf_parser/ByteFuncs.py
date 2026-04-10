
import struct
import numpy as np



#region Byte extraction functions

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
        content = data#.read(val)
        fmt = '<f' if val == 4 else '<d'
        ret = struct.unpack(fmt, content)[0]
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
        length = data.read(1)[0]
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
        length = data.read(1)[0]
        ret = get_b(length, data)

    #   print("MBgetC=",ret)
        return ret
    except:
        return 0

# endregion

#region Byte writing functions

def write_r(val, value):
    """Write a floating point number as val bytes (R*4 = float, R*8 = double)."""
    if val == 4:
        return struct.pack('<f', float(value))
    elif val == 8:
        return struct.pack('<d', float(value))
    return b'\x00' * val

def write_r_arr(val, values):
    """Write an array of floating point numbers (kxR*4 or kxR*8)."""
    ret = b''
    for v in values:
        ret += write_r(val, v)
    return ret

def write_u(val, value):
    """Write an unsigned integer as val bytes (U*1, U*2, U*4)."""
    return int(value).to_bytes(val, byteorder='little', signed=False)

def write_u_arr(val, values):
    """Write an array of unsigned integers (kxU*1, kxU*2, kxU*4)."""
    ret = b''
    for v in values:
        ret += write_u(val, v)
    return ret

def write_i(val, value):
    """Write a signed integer as val bytes (I*1, I*2, I*4)."""
    return int(value).to_bytes(val, byteorder='little', signed=True)

def write_cn(value):
    """Write a variable-length character string (C*n).
    First byte = unsigned count of bytes to follow."""
    if value is None or value == 'no data':
        return b'\x00'
    encoded = value.encode('ascii')
    return bytes([len(encoded)]) + encoded

def write_cn_arr(values):
    """Write an array of variable-length character strings (kxC*n)."""
    ret = b''
    for v in values:
        ret += write_cn(v)
    return ret

def write_c(val, value):
    """Write a fixed-length character string (C*f / C*12).
    Left-justified and space-padded to exactly val bytes."""
    encoded = value.encode('ascii')[:val]
    return encoded + b' ' * (val - len(encoded))

def write_b(val, value):
    """Write fixed-length bit-encoded data (B*6).
    Truncated or zero-padded to exactly val bytes."""
    if isinstance(value, int):
        # If value is an int, convert it to bytes of length val
        data = value.to_bytes(val, byteorder='little', signed=False)[:val]
    else:
        data = bytes(value)[:val]
    return data + b'\x00' * (val - len(data))

def write_bn(value):
    """Write a variable-length bit-encoded field (B*n).
    First byte = unsigned count of bytes to follow."""
    if value is None or value == 'no data':
        return b'\x00'
    data = bytes(value)
    return bytes([len(data)]) + data

def write_dn(value, bit_count=None):
    """Write a variable-length bit-encoded field (D*n).
    First two bytes = unsigned count of bits to follow.
    Unused high-order bits in the last byte must be zero.
    If bit_count is not provided, it defaults to len(value) * 8."""
    data = bytes(value)
    if bit_count is None:
        bit_count = len(data) * 8
    return write_u(2, bit_count) + data

#endregion


if __name__ == "__main__":
    test = write_b(1,0x40)
    print(test)


    print(f"data: {[f'0x{b:02X}' for b in test]}")