import struct

from Helpers import *
from enum import *
import re
from dxgiFormat import *



    



class TEX:
    def __init__(self):
        self.Magic = b''
        self.Version = 0
        self.Width = 0
        self.Height = 0
        self.Depth = 0
        self.MipmapCount = 0
        self.ImageCount = 0
        self.DXGIFormat = 0
        self.SwizzleControl = b"\xFF" * 4
        self.CubemapMarker = 0
        self.Unk = b''
        
        self.UnkSwizzle = b''
        
        self.MipmapOffsets = [] # offset to each mipmap level
        self.MipmapPitch = [] # how many bytes per a row of blocks (if compressed BCn), how many bytes per a row of pixels (if not compressed)
        self.MipmapLinearSize = [] # Size of one mipmap level in bytes
        
        self.dataTEX = b''
        
        
    def ReadTEX(self, f):
        self.Magic = f.read(4)
        if self.Magic != b"TEX\x00":
            raise Exception("File is not a RE Engine tex file")
        
        self.Version = read_uint(f)
        self.Width = read_ushort(f)
        self.Height = read_ushort(f)
        self.Depth = read_ushort(f)
        
        if self.Version > 11 and self.Version != 190820018:
            self.ImageCount = read_ubyte(f)
            self.MipmapHeaderSize = read_ubyte(f)
            self.MipmapCount = self.MipmapHeaderSize // 16 # Each mipmap header is 16 bytes
            
        else:
            self.MipmapCount = read_ubyte(f)
            self.ImageCount = read_ubyte(f)
            
            
        self.DXGIFormat = read_uint(f)
        self.SwizzleControl = f.read(4)
        self.CubemapMarker = read_uint(f)
        self.Unk = f.read(4)
        
        
        if self.Version > 27 and self.Version != 190820018:
            self.SwizzleHeightDepth = read_ubyte(f)
            self.SwizzleWidth = read_ubyte(f)
            self.UnkSwizzle = f.read(6)
        

        for i in range(self.MipmapCount):
            self.MipmapOffsets.append(read_uint64(f))
            self.MipmapPitch.append(read_uint(f))
            self.MipmapLinearSize.append(read_uint(f))
        
        
        self.dataTEX = f.read()
        
   
        
    
    def ConvertToTEX(self, DDS, Filename, Game, Version, verbose=True):
        self.Magic = b'TEX\x00'
        self.Version = int(Version)
        self.Width = DDS.Width
        self.Height = DDS.Height
        self.Depth = DDS.Depth
        
        if self.Version > 11 and self.Version != 190820018:
            self.ImageCount = DDS.arraySize
            self.MipmapHeaderSize = DDS.MipmapCount * 16
            self.MipmapCount = DDS.MipmapCount
            
        else:
            self.MipmapCount = DDS.MipmapCount
            self.ImageCount = DDS.arraySize
            
            
        self.DXGIFormat = DDS.dxgiFormat
        self.SwizzleControl = b"\xFF" * 4
        self.CubemapMarker = 0
        self.Unk = b"\x00" * 4
        
        extra = 0
        if self.Version > 27 and self.Version != 190820018:
            self.SwizzleHeightDepth = 0
            self.SwizzleWidth = 0
            self.UnkSwizzle = b"\x00" * 6
            
            extra = 8
        
        key = DXGI_FORMAT(self.DXGIFormat).name
        
        byte_size = DXGIFormatByteSize[key].value
        
        width = self.Width
        height = self.Height
        if verbose:
            print(width, height)
        
        base = 0x20 + extra + 16 * self.MipmapCount
        mipmap_sizes = 0
        for i in range(self.MipmapCount):
            self.MipmapOffsets.append(base + mipmap_sizes)
            
            num_blocks_wide = math.ceil(width / 4) # How many blocks in a row, round up to nearest integer to avoid not having enough blocks
            num_blocks_tall = math.ceil(height / 4) # How many blocks in a column, round up to nearest integer to avoid not having enough blocks
            
            if verbose:
                print(num_blocks_wide, num_blocks_tall)
            
            if re.search(r"BC[1-7]", key):
                self.MipmapPitch.append(num_blocks_wide * (4 * 4)) # How many bytes in a row of blocks (for compressed BCn formats only)
                
                if verbose:
                    print(self.MipmapPitch[i])
                
                self.MipmapLinearSize.append(num_blocks_wide * num_blocks_tall * byte_size) # Size of one mipmap level in bytes
                
            else:
                self.MipmapPitch.append(width * byte_size) # How many bytes in a row of pixels (for uncompressed formats only)
                self.MipmapLinearSize.append(height * self.MipmapPitch[i]) # Size of one mipmap level in bytes, equals height * pitch
            
            
            
            mipmap_sizes += self.MipmapLinearSize[i]
            
            if verbose:
                print(f"Mip {i:2d}: {width:4d} x {height:4d}  →  {num_blocks_wide}x{num_blocks_tall} blocks  →  {self.MipmapLinearSize} bytes")
            
            width = max(1, width//2)
            height = max(1, height//2)
 
        
        self.dataTEX = DDS.dataDDS
    
    def WriteTEX(self, f):
        f.write(b"TEX\x00")
        
        write_uint(f, self.Version)
        write_ushort(f, self.Width)
        write_ushort(f, self.Height)
        write_ushort(f, self.Depth)
        
        
        if self.Version > 11 and self.Version != 190820018:
            write_ubyte(f, self.ImageCount)
            write_ubyte(f, self.MipmapHeaderSize)
            
        else:
            write_ubyte(f, self.MipmapCount)
            write_ubyte(f, self.ImageCount)
            
            
        write_uint(f, self.DXGIFormat)
        f.write(self.SwizzleControl)
        write_uint(f, self.CubemapMarker)
        f.write(b"\x00" * 4) # self.Unk
        

        if self.Version > 27 and self.Version != 190820018:
            write_ubyte(f, self.SwizzleHeightDepth)
            write_ubyte(f, self.SwizzleWidth)
            f.write(b"\x00" * 6) # self.UnkSwizzle
            
            
        for i in range(self.MipmapCount):
            write_uint64(f, self.MipmapOffsets[i])
            write_uint(f, self.MipmapPitch[i])
            write_uint(f, self.MipmapLinearSize[i])
            
        f.write(self.dataTEX)
        
        
        
        
    
        
        
        
    