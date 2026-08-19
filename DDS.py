import struct

from Helpers import *
from dxgiFormat import *
import re

class DDS:
    def __init__(self):
        self.Magic = b''
        
        self.Size = 0
        self.Flags = 0
        self.Height = 0
        self.Width = 0
        self.PitchOrLinearSize = 0
        self.Depth = 0
        self.MipmapCount = 0
        self.Reserved = b''
        
        #Pixel Format
        self.SizePF = 0
        self.FlagsPF = 0
        self.FourCC = b''
        self.RGBBitCount = 0
        self.RBitMask = 0
        self.GBitMask = 0
        self.BBitMask = 0
        self.ABitMask = 0
        
        # DXGI Format
        self.dxgiFormat = 0
        self.resourceDimension = 0
        self.miscFlag = 0
        self.arraySize = 0
        self.miscFlags2 = 0
       
       
        self.Caps = 0
        self.Caps2 = 0
        self.Caps3 = 0
        self.Caps4 = 0
        self.Reserved2 = 0
        
        self.dataDDS = b''
    
    def ReadDDSHeader(self, f):
        self.Magic = f.read(4)
        if self.Magic != b"DDS ":
            raise Exception("File is not a dds file")
            
        self.Size = read_uint(f)
        self.Flags = read_uint(f)
        self.Height = read_uint(f)
        self.Width = read_uint(f)
        self.PitchOrLinearSize = read_uint(f)
        self.Depth = read_uint(f)
        self.MipmapCount = read_uint(f)
        self.Reserved = f.read(11 * 4)
        self.ReadDDSPixelFormat(f)
        
        
            
        self.Caps = read_uint(f)
        self.Caps2 = read_uint(f)
        self.Caps3 = read_uint(f)
        self.Caps4 = read_uint(f)
        self.Reserved2 = read_uint(f)
        
        if self.FourCC == b"DX10":
            self.ReadDXGIFormat(f)
        
        
        
        
        
    def ReadDDSPixelFormat(self, f):
        self.SizePF = read_uint(f)
        self.FlagsPF = read_uint(f)
        self.FourCC = f.read(4)
        self.RGBBitCount = read_uint(f)
        self.RBitMask = read_uint(f)
        self.GBitMask = read_uint(f)
        self.BBitMask = read_uint(f)
        self.ABitMask = read_uint(f)
        
        
    def ReadDXGIFormat(self, f):
        self.dxgiFormat = read_uint(f)
        self.resourceDimension = read_uint(f)
        self.miscFlag = read_uint(f)
        self.arraySize = read_uint(f)
        self.miscFlags2 = read_uint(f)
       
    def ReadDDSData(self, f):
        self.dataDDS = f.read()
        
        
    def ConvertToDDS(self, TEX):
        self.Magic = b'DDS '
        
        self.Size = 124
        
        self.Height = TEX.Height
        self.Width = TEX.Width
        
        key = DXGI_FORMAT(TEX.DXGIFormat).name
        
        if re.search(r"BC[1-7]", key):
            self.PitchOrLinearSize = TEX.MipmapLinearSize[0] # Linear Size (size of one mipmap level), used only for compressed BCn formats
            # dds stores only first mipmap level's linear size in header
            
            self.Flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000
            
        else:
            self.PitchOrLinearSize = TEX.MipmapPitch[0] # Pitch (how many bytes in a row of pixels/blocks), not used for compressed BCn formats, used only for uncompressed formats (row of pixels)
            self.Flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x8
            
        self.Depth = TEX.Depth
        
        self.Caps = 0x1000
        
        if self.Depth > 1:
            self.Flags |= 0x800000
            
        
        self.MipmapCount = TEX.MipmapCount
        
        if self.MipmapCount > 1:
            self.Flags |= 0x20000
            self.Caps |= 0x400000
            
        if self.MipmapCount > 1 or self.Depth > 1:
            self.Caps |= 0x8
            
            
        self.Reserved = b'\x00' * 11 * 4
        
        #Pixel Format
        self.SizePF = 32
        self.FlagsPF = 0x4
        self.FourCC = b"DX10"
        
        
        
          

        self.Caps2 = 0
        self.Caps3 = 0
        self.Caps4 = 0
        self.Reserved2 = 0
        
        # DXGI Format
        self.dxgiFormat = TEX.DXGIFormat
        
        if TEX.Depth == 1:
            self.resourceDimension = 3
            
        self.arraySize = 1
        
        self.dataDDS = TEX.dataTEX
        
    
    def WriteDDSHeader(self, f):
        f.write(self.Magic)
        
        write_uint(f, self.Size)
        write_uint(f, self.Flags)
        write_uint(f, self.Height)
        write_uint(f, self.Width)
        write_uint(f, self.PitchOrLinearSize)
        write_uint(f, self.Depth)
        write_uint(f, self.MipmapCount)
        f.write(self.Reserved)
        self.WriteDDSPixelFormat(f)
        
        
            
        write_uint(f, self.Caps)
        write_uint(f, self.Caps2)
        write_uint(f, self.Caps3)
        write_uint(f, self.Caps4)
        write_uint(f, self.Reserved2)
        
        self.WriteDXGIFormat(f)
    
    
    
    def WriteDDSPixelFormat(self, f):
        write_uint(f, self.SizePF)
        write_uint(f, self.FlagsPF)
        f.write(self.FourCC)
        write_uint(f, self.RGBBitCount)
        write_uint(f, self.RBitMask)
        write_uint(f, self.GBitMask)
        write_uint(f, self.BBitMask)
        write_uint(f, self.ABitMask)
        
        
    def WriteDXGIFormat(self, f):
        write_uint(f, self.dxgiFormat)
        write_uint(f, self.resourceDimension)
        write_uint(f, self.miscFlag)
        write_uint(f, self.arraySize)
        write_uint(f, self.miscFlags2)
        
    def WriteDDSData(self, f):
        f.write(self.dataDDS)

