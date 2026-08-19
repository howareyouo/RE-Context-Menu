import os
import sys
import shutil
import subprocess
import argparse
import tempfile
from DDS import *
from TEX import *

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
TEXCONV = os.path.join(TOOL_DIR, "bin", "texconv.exe")


def run_texconv(args):
    cmd = [TEXCONV, "-y"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("texconv failed:\n" + result.stdout + result.stderr)
    return result


def ConvertPNG(filepath):
    file = os.path.basename(filepath)
    directory = os.path.dirname(filepath)
    stem = file.split(".tex.")[0] if ".tex." in file else os.path.splitext(file)[0]

    if not os.path.exists(TEXCONV):
        raise RuntimeError(f"Could not find texconv.exe: {TEXCONV}")

    with tempfile.TemporaryDirectory() as tmp:
        print(f"Reading TEX: {filepath}")
        with open(filepath, "rb") as f:
            tex = TEX()
            tex.ReadTEX(f)

        if tex.Depth > 1 or tex.ImageCount > 1:
            raise RuntimeError("暂不支持体积/数组纹理（Depth>1 或 ImageCount>1）的转换")

        # TEX -> DDS
        mid_dds = os.path.join(tmp, "input.dds")
        with open(mid_dds, "wb") as f:
            dds = DDS()
            dds.ConvertToDDS(tex)
            dds.WriteDDSHeader(f)
            dds.WriteDDSData(f)

        # DDS -> PNG (base layer only)
        print("texconv: DDS -> PNG")
        run_texconv(["-ft", "png", "-m", "1", "-o", tmp, mid_dds])

        out_path = os.path.join(directory, f"{stem}.png")
        shutil.copy(os.path.join(tmp, "input.png"), out_path)  # Copy instead of move for cross-disk compatibility
        print(f"Done: {out_path}")
        return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RE Engine TEX to PNG converter")
    parser.add_argument("file", help="Path to the .tex file to convert")
    args = parser.parse_args()

    try:
        ConvertPNG(args.file)
    except Exception as e:
        print(f"✗ Error: {e}")
        os.system("pause")
        sys.exit(1)
