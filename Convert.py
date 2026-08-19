import os
import sys
import time
import argparse
from pathlib import Path
from DDS import *
from TEX import *

Versions = ["11", "34", "143221013"]

def Convert(Filepath, Game, Version, DDS, TEX):
    File = os.path.basename(Filepath)
    Filename = os.path.splitext(File)[0]
    DirectoryPath = os.path.dirname(Filepath)
    Extension = File.split(".")[-1] # e.g.: "11" (the Version) or dds
    Path = os.path.join(DirectoryPath, Filename)
    
    if Extension.lower() == 'dds':
        PathOutputTEX = os.path.join(DirectoryPath, Filename + ".tex." + Version)
        with open(Filepath, 'rb') as f:
            dds = DDS()
            dds.ReadDDSHeader(f) # Read DDS
            dds.ReadDDSData(f)
        
        with open(PathOutputTEX, 'wb') as f:
            ############################################################

            tex = TEX() # Construct TEX
            tex.ConvertToTEX(dds, Filename, Game, Version) # Convert to TEX
            
            tex.WriteTEX(f) # Write .tex.{version}
    
    elif Extension.lower() in Versions:
        PathOutputDDS = os.path.join(DirectoryPath, Filename + f".{Extension}." + "dds")
        with open(Filepath, 'rb') as f:
            tex = TEX()
            tex.ReadTEX(f) # Read TEX
            
        with open(PathOutputDDS, 'wb') as f:
            dds = DDS() # Construct DDS
            dds.ConvertToDDS(tex) # Convert to DDS
            
            dds.WriteDDSHeader(f) # Write DDS Header
            dds.WriteDDSData(f) # Write DDS Data
            
    else:
        raise ValueError(f"Unsupported file type: {Extension}")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('file', help="Path of file to convert")
    parser.add_argument('-game',  default="", help="Game name, not used for now. default is empty string when converting to .dds")
    parser.add_argument('-version', default="", help="Game version without a dot, used for converting to .tex, default is empty string when converting to .dds")

    args = parser.parse_args()

    print(f"Game: {args.game}")
    print(f"Version: {args.version}")
    print(f"File received: {args.file}\n")
    
   
    start = time.time()
    
    try:
        Convert(args.file, args.game, args.version, DDS, TEX)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        os.system("pause")
        sys.exit(1)
    
    end = time.time()
    
    print(f"\nCode finished in {end - start} seconds\n")
        

        