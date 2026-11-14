# -*- coding: utf-8 -*-
"""
全格式 → Markdown 转换工具（核心脚本）
======================================
把常见办公/文档/图片格式转换为 Markdown，按需加载、按需调用，无常驻后台、低负荷。

支持格式：
  - PDF、电子书(EPUB/MOBI/FB2/CBZ/XPS/SVG)   → PyMuPDF4LLM
  - Word(.docx)、PPT(.pptx)、HTML(.html/.htm) → pandoc
  - Excel(.xlsx/.xls)、CSV                     → pandas
  - 图片(PNG/JPG/TIFF/GIF/BMP/WEBP)            → tesseract OCR

用法：
  python converter.py <文件1> [文件2 ...] [选项]

选项：
  --no-clean        跳过 pandoc 格式清洗
  --outdir 目录      指定输出目录（默认与源文件同目录）
  --embed-images     PDF 转换时提取内嵌图片
  --no-ocr          关闭 OCR（图片将跳过识别、扫描 PDF 不识别文字）
  --lang 语言        OCR 语言，默认 "chi_sim+eng"

依赖发现顺序（支持任意安装位置，换电脑无需改代码）：
  1. 环境变量：PANDOC / TESSERACT
  2. 本目录：pandoc/pandoc.exe、Tesseract-OCR/tesseract.exe
  3. 系统 PATH：pandoc、tesseract
  4. Windows 常见安装位置（自动探测）

低负荷说明：
  - 一次性命令行进程，转完即退，无任何后台常驻。
  - 按需 import：转哪个格式才加载对应库。
  - OCR 仅在处理图片/扫描 PDF 且未加 --no-ocr 时调用 tesseract。
"""
import sys
import os
import glob
import shutil
import subprocess
import argparse

# ---------------------------------------------------------------
# 路径常量（自动探测，一般无需修改）
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(BASE_DIR, "lib")                      # 本地 Python 库目录（setup_deps.py 安装到这里）
if os.path.isdir(LIB):
    sys.path.insert(0, LIB)


def _search_pandoc():
    """按优先级寻找 pandoc.exe。"""
    cands = [os.environ.get("PANDOC"),
             os.path.join(BASE_DIR, "pandoc", "pandoc.exe"),
             os.path.join(BASE_DIR, "pandoc.exe"),
             shutil.which("pandoc")]
    cands += sorted(glob.glob(os.path.join(
        os.path.expanduser("~"), "AppData", "Local", "Pandoc", "*", "pandoc.exe")),
        reverse=True)
    cands += sorted(glob.glob(os.path.join(
        os.environ.get("ProgramFiles", r"C:\Program Files"), "Pandoc", "pandoc.exe")))
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


def _search_tesseract():
    """按优先级寻找 tesseract.exe。"""
    cands = [os.environ.get("TESSERACT"),
             os.path.join(BASE_DIR, "Tesseract-OCR", "tesseract.exe"),
             shutil.which("tesseract")]
    cands += sorted(glob.glob(os.path.join(
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        "Tesseract-OCR", "tesseract.exe")))
    cands += sorted(glob.glob(os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR", "tesseract.exe")))
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


PANDOC = _search_pandoc()
TESSERACT = _search_tesseract()
# tessdata 目录：优先用 tesseract 同目录下的 tessdata
_tess_dir = os.path.dirname(TESSERACT) if TESSERACT else None
TESSDATA = os.path.join(_tess_dir, "tessdata") if _tess_dir else None
if TESSDATA and not os.path.isdir(TESSDATA):
    TESSDATA = None

# 格式分派表
PDF_LIKE = {".pdf"}
BOOK_LIKE = {".epub", ".mobi", ".fb2", ".cbz", ".xps", ".svg"}
PANDOC_LIKE = {".docx", ".pptx", ".html", ".htm"}
EXCEL_LIKE = {".xlsx", ".xls", ".csv"}
IMAGE_LIKE = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".gif", ".bmp", ".webp"}


def has_tesseract() -> bool:
    return bool(TESSERACT)


def has_pandoc() -> bool:
    return bool(PANDOC)


def pandoc_clean(raw_md: str, final_md: str) -> None:
    """用 pandoc 规范化 markdown（GFM 风格、表格对齐）。"""
    cmd = [PANDOC, "-f", "markdown", "-t", "gfm", "--wrap=none",
           "-o", final_md, raw_md]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def finish_md(raw_md: str, final_md: str, clean: bool) -> str:
    """清洗（可选）并落盘为 final_md，返回最终路径。"""
    if clean and has_pandoc():
        pandoc_clean(raw_md, final_md)
        os.remove(raw_md)
    else:
        os.replace(raw_md, final_md)
    return final_md


# ---------------- PDF / 电子书 ----------------
def convert_pdf_book(path, outdir, clean, embed_images, ocr, lang):
    import pymupdf4llm
    base = os.path.splitext(os.path.basename(path))[0]
    raw_md = os.path.join(outdir, base + "_raw.md")
    final_md = os.path.join(outdir, base + ".md")
    # 仅在 tesseract 存在且允许 OCR 时启用 OCR
    use_ocr = ocr and has_tesseract()
    md = pymupdf4llm.to_markdown(
        path,
        write_images=embed_images,
        image_path=outdir if embed_images else None,
        use_ocr=use_ocr,
        ocr_language=lang.split("+")[0] if "+" in lang else lang,
    )
    with open(raw_md, "w", encoding="utf-8") as f:
        f.write(md)
    return finish_md(raw_md, final_md, clean)


# ---------------- Word / PPT / HTML（pandoc） ----------------
def convert_pandoc(path, outdir, clean):
    base = os.path.splitext(os.path.basename(path))[0]
    if not has_pandoc():
        raise RuntimeError("未找到 pandoc，无法转换该格式（运行 setup_deps.py 或安装 pandoc）。")
    raw_md = os.path.join(outdir, base + "_raw.md")
    final_md = os.path.join(outdir, base + ".md")
    cmd = [PANDOC, path, "-t", "gfm", "--wrap=none", "-o", raw_md]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return finish_md(raw_md, final_md, clean)


# ---------------- Excel / CSV ----------------
def convert_excel(path, outdir, clean):
    import pandas as pd
    base = os.path.splitext(os.path.basename(path))[0]
    raw_md = os.path.join(outdir, base + "_raw.md")
    final_md = os.path.join(outdir, base + ".md")
    ext = os.path.splitext(path)[1].lower()
    parts = []
    if ext == ".csv":
        df = pd.read_csv(path)
        parts.append(f"# {base}\n\n")
        parts.append(df.to_markdown(index=False))
    else:
        sheets = pd.read_excel(path, sheet_name=None)
        for i, (name, df) in enumerate(sheets.items()):
            parts.append(f"# {base}\n\n" if i == 0 else "")
            if len(sheets) > 1:
                parts.append(f"## 工作表：{name}\n\n")
            parts.append(df.to_markdown(index=False) + "\n")
    with open(raw_md, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return finish_md(raw_md, final_md, clean)


# ---------------- 图片 OCR ----------------
def convert_image(path, outdir, ocr, lang):
    base = os.path.splitext(os.path.basename(path))[0]
    final_md = os.path.join(outdir, base + ".md")
    if not ocr:
        raise RuntimeError("图片转换需 OCR，请勿使用 --no-ocr。")
    if not has_tesseract():
        raise RuntimeError("未找到 tesseract，无法识别图片文字（运行 setup_deps.py 或安装 tesseract）。")
    out_base = os.path.join(outdir, base + "_ocr")
    cmd = [TESSERACT, path, out_base, "-l", lang]
    if TESSDATA:
        cmd += ["--tessdata-dir", TESSDATA]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError("OCR 识别失败（语言包可能缺失，检查 --lang 与 tessdata）。")
    txt = out_base + ".txt"
    with open(txt, "r", encoding="utf-8") as f:
        text = f.read()
    with open(final_md, "w", encoding="utf-8") as f:
        f.write(f"# {base}\n\n" + text)
    os.remove(txt)
    return final_md


# ---------------- 主流程 ----------------
def convert_file(path, outdir, clean, embed_images, ocr, lang):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext in PDF_LIKE or ext in BOOK_LIKE:
        return convert_pdf_book(path, outdir, clean, embed_images, ocr, lang)
    if ext in PANDOC_LIKE:
        return convert_pandoc(path, outdir, clean)
    if ext in EXCEL_LIKE:
        return convert_excel(path, outdir, clean)
    if ext in IMAGE_LIKE:
        return convert_image(path, outdir, ocr, lang)
    raise RuntimeError(f"暂不支持格式: {ext or '(无扩展名)'}")


def main(argv=None):
    p = argparse.ArgumentParser(description="全格式 → Markdown 转换")
    p.add_argument("files", nargs="+", help="要转换的文件")
    p.add_argument("--no-clean", action="store_true", help="跳过 pandoc 清洗")
    p.add_argument("--outdir", default=None, help="输出目录")
    p.add_argument("--embed-images", action="store_true", help="PDF 提取内嵌图片")
    p.add_argument("--no-ocr", action="store_true", help="关闭 OCR")
    p.add_argument("--lang", default="chi_sim+eng", help="OCR 语言")
    a = p.parse_args(argv)

    print("=" * 50)
    print(" 全格式 → Markdown 转换工具")
    print(" pandoc:", PANDOC or "不可用",
          "| tesseract:", TESSERACT or "不可用",
          "| OCR:", "开" if not a.no_ocr else "关")
    print("=" * 50)

    failures = []
    for f in a.files:
        # 未指定 --outdir 时，输出到源文件所在目录（拖拽场景的默认行为）
        outdir = a.outdir or os.path.dirname(os.path.abspath(f))
        try:
            out = convert_file(f, outdir=outdir,
                               clean=not a.no_clean,
                               embed_images=a.embed_images,
                               ocr=not a.no_ocr,
                               lang=a.lang)
            print(f"[OK] {os.path.basename(f)}  ->  {out}")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {f} : {e}")
            failures.append(f)
    print("-" * 50)
    if failures:
        print(f"完成，但有 {len(failures)} 个文件失败：")
        for f in failures:
            print("   ", f)
        sys.exit(1)
    print(f"全部 {len(a.files)} 个文件转换成功。")


if __name__ == "__main__":
    main()
