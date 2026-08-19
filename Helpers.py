import struct
import re
import math

def read_ubyte(f):
    return struct.unpack("<B", f.read(1))[0]

def read_ushort(f):
    return struct.unpack("<H", f.read(2))[0]

def read_uint(f):
    return struct.unpack("<I", f.read(4))[0]

def read_uint64(f):
    return struct.unpack("<Q", f.read(8))[0]

def read_float(f):
    return struct.unpack("<f", f.read(4))[0]

def read_bytes(f, format):
    match = re.search(r'\d+', format)
    return struct.unpack(format, f.read(int(match.group())))


def write_ubyte(f, data):
    f.write(struct.pack("<B", data))
    
def write_uint(f, data):
    f.write(struct.pack("<I", data))
    
def write_ushort(f, data):
    f.write(struct.pack("<H", data))

def write_uint64(f, data):
    f.write(struct.pack("<Q", data))
    
def write_float(f, data):
    f.write(struct.pack("<f", data))




def align_to_4(f, offset):
    alignment_bytes = (4 - (offset % 4)) % 4
    f.seek(alignment_bytes, 1)
    
def align_to_16(f, offset):
    alignment_bytes = (16 - (offset % 16)) % 16
    f.seek(alignment_bytes, 1)
    
def write_alignment_4(f, offset):
    alignment_bytes = (4 - (offset % 4)) % 4
    if alignment_bytes:
        f.write(b'\x00' * alignment_bytes)
        
def write_alignment_16(f, offset):
    alignment_bytes = (16 - (offset % 16)) % 16
    if alignment_bytes:
        f.write(b'\x00' * alignment_bytes)
        
    
