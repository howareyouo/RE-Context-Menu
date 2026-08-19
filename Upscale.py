import os
import sys
import time
import shutil
import subprocess
import argparse
import tempfile
from pathlib import Path
from DDS import *
from TEX import *
from dxgiFormat import DXGI_FORMAT

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
TEXCONV = os.path.join(TOOL_DIR, "bin", "texconv.exe")

# Topaz Gigapixel AI executable candidate paths (tried in order)
TOPAZ_CANDIDATES = [
    r"F:\Program Files\Topaz Gigapixel AI\gigapixel.exe",
    r"C:\Program Files\Topaz Labs LLC\Topaz Gigapixel AI\Topaz Gigapixel AI.exe",
    r"C:\Program Files\Topaz Gigapixel AI\gigapixel.exe",
]

# Topaz output filename suffix (default _2x, configurable in Topaz preferences; auto-scanned if not found)
DEFAULT_SUFFIX = "_2x"
# Backup suffix for original file after upscale (appended to filename stem, before extension; extension unchanged)
BACKUP_TAG = "_bak"


def find_topaz():
    """Find Topaz executable: prefer env var, then candidate paths"""
    env = os.environ.get("TOPAZ_GIGAPIXEL")
    if env and os.path.exists(env):
        return env
    for p in TOPAZ_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def run_texconv(args):
    cmd = [TEXCONV, "-y"] + args
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("texconv failed:\n" + result.stdout + result.stderr)
    return result


def to_texconv_format(name):
    """DXGI_FORMAT_XXX -> XXX (texconv -f format name), TYPELESS falls back to UNORM"""
    fmt = name.replace("DXGI_FORMAT_", "")
    if fmt.endswith("_TYPELESS"):
        fmt = fmt.replace("_TYPELESS", "_UNORM")
    return fmt


def guess_version(filepath):
    """Extract version number from filename, e.g. abc.tex.143221013 -> 143221013"""
    ext = os.path.basename(filepath).split(".")[-1]
    if ext.lower() in ("tex", "dds"):
        return ""
    return ext


def run_topaz(topaz_exe, input_png, scale):
    """Call Topaz Gigapixel AI to upscale a single image (-i input, --scale factor, --overwrite output), wait for completion"""
    print(f"      Topaz: {topaz_exe} | scale x{scale}")
    subprocess.run([topaz_exe, "-i", input_png, "--scale", str(scale), "--overwrite"], check=True)


def find_output_png(tmp, suffix, input_mtime):
    """Find the output PNG after Topaz processing:
    --overwrite means Topaz overwrites the input; otherwise a new file with suffix is produced"""
    # 1) Match by suffix (e.g. input_2x.png)
    preferred = os.path.join(tmp, f"input{suffix}.png")
    if os.path.exists(preferred):
        return preferred
    # 2) Input file overwritten by Topaz (mtime changed)
    png_in = os.path.join(tmp, "input.png")
    if os.path.getmtime(png_in) > input_mtime:
        return png_in
    # 3) Fallback: scan for the newest png in the directory
    pngs = [os.path.join(tmp, n) for n in os.listdir(tmp)
            if n.lower().endswith(".png") and n.lower() != "input.png"]
    if pngs:
        return max(pngs, key=os.path.getmtime)
    raise RuntimeError("Could not find Topaz output image, please check Topaz output suffix setting")


def Upscale(filepath, version, scale, topaz_exe, suffix):
    file = os.path.basename(filepath)
    directory = os.path.dirname(filepath)
    stem = file.split(".tex.")[0] if ".tex." in file else os.path.splitext(file)[0]

    if not os.path.exists(TEXCONV):
        raise RuntimeError(f"Could not find texconv.exe, please confirm it is in the tool directory: {TEXCONV}")

    with tempfile.TemporaryDirectory() as tmp:
        # 1) TEX -> DDS
        print(f"[1/5] Reading TEX: {filepath}")
        with open(filepath, "rb") as f:
            tex = TEX()
            tex.ReadTEX(f)

        if tex.Depth > 1 or tex.ImageCount > 1:
            raise RuntimeError("Unsupported volume/array textures (Depth>1 or ImageCount>1)")

        original_format = DXGI_FORMAT(tex.DXGIFormat).name
        print(f"      Format: {original_format} | Size: {tex.Width}x{tex.Height} | Mipmap: {tex.MipmapCount}")

        mid_dds = os.path.join(tmp, "input.dds")
        with open(mid_dds, "wb") as f:
            dds = DDS()
            dds.ConvertToDDS(tex)
            dds.WriteDDSHeader(f)
            dds.WriteDDSData(f)

        # 2) DDS -> PNG (base layer only)
        print("[2/5] texconv: DDS -> PNG")
        run_texconv(["-ft", "png", "-m", "1", "-o", tmp, mid_dds])

        # 3) Topaz upscale
        print("[3/5] Topaz Gigapixel AI upscaling...")
        if not topaz_exe:
            topaz_exe = find_topaz()
        if not topaz_exe or not os.path.exists(topaz_exe):
            raise RuntimeError("Could not find Topaz Gigapixel AI, please specify full path with --topaz-exe or set TOPAZ_GIGAPIXEL env var")
        png_in = os.path.join(tmp, "input.png")
        input_mtime = os.path.getmtime(png_in)
        run_topaz(topaz_exe, png_in, scale)
        upscaled_png = find_output_png(tmp, suffix, input_mtime)
        print(f"      Topaz output: {upscaled_png}")

        # 4) PNG -> DDS (re-compress with original format, rebuild mipmaps)
        fmt = to_texconv_format(original_format)
        print(f"[4/5] texconv: PNG -> DDS (format {fmt})")
        upscaled_copy = os.path.join(tmp, "upscaled.png")
        shutil.copy(upscaled_png, upscaled_copy)
        run_texconv(["-dx10", "-f", fmt, "-m", str(max(tex.MipmapCount, 1)), "-o", tmp, upscaled_copy])
        new_dds = os.path.join(tmp, "upscaled.dds")

        # 5) DDS -> TEX
        print("[5/5] Converting back to TEX")
        with open(new_dds, "rb") as f:
            dds2 = DDS()
            dds2.ReadDDSHeader(f)
            dds2.ReadDDSData(f)

        out = TEX()
        out.ConvertToTEX(dds2, stem, "", version, verbose=False)  # Hide conversion debug info

        # Write new file to same directory temp file first (avoid cross-disk move), then swap with original:
        # Original file backed up as {stem}_bak.tex.{version} (extension unchanged), new file replaces original path
        original_path = os.path.abspath(filepath)
        backup_path = os.path.join(directory, f"{stem}{BACKUP_TAG}.tex.{version}")
        tmp_out = os.path.join(directory, f".{stem}.tex.{version}.tmp")

        try:
            with open(tmp_out, "wb") as f:
                out.WriteTEX(f)

            if os.path.exists(backup_path):
                os.remove(backup_path)  # Old backup overwritten, only keep the most recent original version
            os.replace(original_path, backup_path)  # Original file -> _bak backup
            os.replace(tmp_out, original_path)      # Upscaled new file -> original path
        finally:
            if os.path.exists(tmp_out):
                os.remove(tmp_out)  # Clean up any residual temp file

        print(f"Backup: {backup_path}")
        print(f"Done: {original_path}")
        return original_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RE Engine TEX AI Upscale (via Topaz Gigapixel AI)")
    parser.add_argument("file", help="Path to the .tex file to upscale")
    parser.add_argument("-version", default="", help="Game version number (without dot), auto-detected from filename if omitted")
    parser.add_argument("--scale", type=float, default=1.5, help="Upscale factor (default 1.5)")
    parser.add_argument("--topaz-exe", default=None, help="Full path to Topaz gigapixel.exe")
    parser.add_argument("--suffix", default=DEFAULT_SUFFIX, help="Topaz output filename suffix (default _2x)")
    args = parser.parse_args()

    start = time.time()
    version = args.version or guess_version(args.file)

    try:
        Upscale(args.file, version, args.scale, args.topaz_exe, args.suffix)
    except Exception as e:
        print(f"✗ Error: {e}")
        os.system("pause")
        sys.exit(1)

    print(f"Total time: {time.time() - start:.1f} seconds")
