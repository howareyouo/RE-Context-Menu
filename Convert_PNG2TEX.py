import os
import sys
import subprocess
import argparse
import tempfile
from DDS import *
from TEX import *

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
TEXCONV = os.path.join(TOOL_DIR, "bin", "texconv.exe")

# 目标游戏版本（右键 .png 时转换输出的 .tex.{version}）
GAME = "RE4R"
EXTENSION = ".143221013"
# 使用的压缩格式（DXGI 名称，texconv -f 可识别）
FORMAT = "BC7_UNORM"
# 备份后缀（追加在完整文件名后，扩展名保留）
BACKUP_TAG = "_bak"


def run_texconv(args):
    cmd = [TEXCONV, "-y"] + args
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("texconv failed:\n" + result.stdout + result.stderr)
    return result


def ConvertPNGtoTEX(filepath):
    if not os.path.exists(TEXCONV):
        raise RuntimeError(f"Could not find texconv.exe: {TEXCONV}")

    if os.path.splitext(filepath)[1].lower() != ".png":
        raise RuntimeError(f"Unsupported file type, expected a .png file: {filepath}")

    directory = os.path.dirname(filepath)
    file = os.path.basename(filepath)
    stem = file.split(".tex.")[0] if ".tex." in file else os.path.splitext(file)[0]
    out_path = os.path.join(directory, f"{stem}.tex{EXTENSION}")

    with tempfile.TemporaryDirectory() as tmp:
        # 1) PNG -> DDS (BC7 压缩, 生成完整 mipmap 链)
        print("texconv: PNG -> DDS (BC7_UNORM, full mipmap chain)")
        run_texconv(["-dx10", "-f", FORMAT, "-o", tmp, filepath])

        mid_dds = os.path.join(tmp, stem + ".dds")
        if not os.path.exists(mid_dds):
            raise RuntimeError("texconv did not produce expected DDS output, please check the input PNG")

        # 2) DDS -> TEX
        print(f"Reading DDS: {mid_dds}")
        with open(mid_dds, "rb") as f:
            dds = DDS()
            dds.ReadDDSHeader(f)
            dds.ReadDDSData(f)

        tex = TEX()
        tex.ConvertToTEX(dds, stem, GAME, EXTENSION.lstrip("."), verbose=False)

        # 先写临时文件再替换，避免跨盘移动；若原 .tex 已存在则备份为 {stem}.tex_bak{EXTENSION}
        tmp_out = os.path.join(directory, f".{stem}.tex{EXTENSION}.tmp")
        try:
            with open(tmp_out, "wb") as f:
                tex.WriteTEX(f)

            if os.path.exists(out_path):
                backup_path = os.path.join(directory, f"{stem}.tex{BACKUP_TAG}{EXTENSION}")
                if os.path.exists(backup_path):
                    os.remove(backup_path)  # 旧备份覆盖，仅保留最近一次的原文件
                os.replace(out_path, backup_path)  # 原 .tex -> _bak 备份
                os.replace(tmp_out, out_path)      # 新文件 -> 原路径
                print(f"Backup: {backup_path}")
            else:
                os.replace(tmp_out, out_path)      # 无原文件，直接写入
        finally:
            if os.path.exists(tmp_out):
                os.remove(tmp_out)  # 清理残留临时文件

    print(f"Done: {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PNG to RE Engine TEX converter")
    parser.add_argument("file", help="Path to the .png file to convert")
    args = parser.parse_args()

    try:
        ConvertPNGtoTEX(args.file)
    except Exception as e:
        print(f"✗ Error: {e}")
        os.system("pause")
        sys.exit(1)