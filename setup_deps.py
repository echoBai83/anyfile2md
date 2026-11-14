# -*- coding: utf-8 -*-
"""
One-click dependency install / environment check
================================================
Installs Python deps into .\\lib (never touches global site-packages) and probes
for pandoc / tesseract.

Usage:
  python setup_deps.py               install pinned versions + probe
  python setup_deps.py --upgrade     upgrade packages to latest
  python setup_deps.py --check       probe only, install nothing
  python setup_deps.py --with-tesseract
                                     also download the tesseract OCR engine
  python setup_deps.py --fetch-lang chi_sim
                                     download one tesseract language pack

Version pinning:
  requirements.txt is the source of truth for the packages this tool is tested
  against. With --upgrade, the resolved versions are read back and written into
  requirements.txt so the next install is reproducible again.
"""
import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(BASE_DIR, "lib")
REQ = os.path.join(BASE_DIR, "requirements.txt")
REQ_HEADER = [
    "# Core deps, pinned to versions this tool was tested against.",
    "# setup_deps.py --upgrade rewrites the pins below, keeping these comments.",
]
FALLBACK_PKGS = ["pymupdf4llm", "pandas", "tabulate", "openpyxl"]

TESSERACT_RELEASE = "5.4.0.20240606"
TESSERACT_URL = ("https://github.com/UB-Mannheim/tesseract/releases/download/"
                 "v{r}/tesseract-ocr-w64-setup-{r}.exe".format(r=TESSERACT_RELEASE))
TESSDATA_URL = ("https://github.com/tesseract-ocr/tessdata_fast/raw/main/"
                "{}.traineddata")
LANGS = ("chi_sim", "eng")


def log(msg=""):
    print(msg, flush=True)


# ---------------------------------------------------------------
# Python deps
# ---------------------------------------------------------------
def read_pins():
    """Return [(name, version_or_None)] from requirements.txt."""
    if not os.path.isfile(REQ):
        return [(p, None) for p in FALLBACK_PKGS]
    pins = []
    with open(REQ, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            if "==" in line:
                name, ver = line.split("==", 1)
                pins.append((name.strip(), ver.strip()))
            else:
                pins.append((line, None))
    return pins


def installed_version(dist_name):
    """Version of a package installed under .\\lib, or None."""
    if not os.path.isdir(LIB):
        return None
    sys.path.insert(0, LIB)
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version(dist_name)
        except PackageNotFoundError:
            return None
    finally:
        sys.path.pop(0)


def _read_comments():
    """Keep the human-written comments in requirements.txt when rewriting it."""
    comments = {}
    if not os.path.isfile(REQ):
        return comments
    pending = []
    with open(REQ, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("#"):
                pending.append(s)
                continue
            spec = s.split("#", 1)[0].strip()
            if spec:
                comments[spec.split("==")[0].strip().lower()] = pending
            pending = []
    return comments


def write_pins(pins):
    """Rewrite requirements.txt with `name==version` lines, preserving comments."""
    comments = _read_comments()
    lines = list(REQ_HEADER)
    for name, ver in pins:
        lines += comments.get(name.lower(), [])
        lines.append(f"{name}=={ver}" if ver else name)
    with open(REQ, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    log(f"      requirements.txt updated ({len(pins)} packages)")


def pip_install(pins, upgrade=False):
    """Install into .\\lib. Fresh install honours pins; --upgrade lifts them."""
    if upgrade:
        specs = [name for name, _ in pins]           # let pip resolve newest
    else:
        specs = [f"{n}=={v}" if v else n for n, v in pins]
    log(f"[1/4] Installing Python deps into {LIB} ...")
    log("      " + ", ".join(specs))
    os.makedirs(LIB, exist_ok=True)
    cmd = [sys.executable, "-m", "pip", "install", "--target", LIB]
    if upgrade:
        cmd.append("--upgrade")
    cmd += specs
    if subprocess.run(cmd).returncode != 0:
        log("[FAIL] pip install failed. Check network / pip index configuration.")
        sys.exit(1)
    write_pins([(n, installed_version(n) or v) for n, v in pins])
    log("      done.")


# ---------------------------------------------------------------
# External tools
# ---------------------------------------------------------------
def find_tool(app, env_var, local_subpath, extra_globs=()):
    """Probe order matches converter.py: env var -> local folder -> PATH -> known installs."""
    cands = [os.environ.get(env_var),
             os.path.join(BASE_DIR, local_subpath),
             shutil.which(app)]
    for pat in extra_globs:
        cands += sorted(glob.glob(os.path.expanduser(pat)), reverse=True)
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


def find_pandoc():
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    return find_tool("pandoc.exe", "PANDOC", os.path.join("pandoc", "pandoc.exe"), [
        os.path.join("~", "AppData", "Local", "Pandoc", "*", "pandoc.exe"),
        os.path.join(program_files, "Pandoc", "pandoc.exe"),
    ])


def find_tesseract():
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    return find_tool("tesseract.exe", "TESSERACT",
                     os.path.join("Tesseract-OCR", "tesseract.exe"), [
                         os.path.join(program_files, "Tesseract-OCR", "tesseract.exe"),
                         os.path.join(local_appdata, "Programs", "Tesseract-OCR",
                                      "tesseract.exe"),
                     ])


def tessdata_dir(tess):
    """Pick the tessdata folder: local copy first, else next to the binary."""
    local = os.path.join(BASE_DIR, "Tesseract-OCR", "tessdata")
    if os.path.isdir(local):
        return local
    if tess:
        return os.path.join(os.path.dirname(tess), "tessdata")
    return local


def check_tools():
    log("[3/4] Probing pandoc ...")
    pandoc = find_pandoc()
    if pandoc:
        log(f"      found: {pandoc}")
    else:
        log("      [warn] pandoc not found -- docx/pptx/html conversion and the")
        log("             Markdown clean-up are unavailable. Install with")
        log("             winget install --id JohnMacFarlane.Pandoc")

    log("[4/4] Probing tesseract ...")
    tess = find_tesseract()
    if tess:
        log(f"      found: {tess}")
        td = tessdata_dir(tess)
        langs = []
        if os.path.isdir(td):
            langs = sorted(f[:-len(".traineddata")] for f in os.listdir(td)
                           if f.endswith(".traineddata"))
        log(f"      tessdata: {td}")
        log(f"      languages: {', '.join(langs) or '(none)'}")
        for lang in LANGS:
            if lang not in langs:
                log(f"      [warn] missing {lang}.traineddata -- fetch with:")
                log(f"             python setup_deps.py --fetch-lang {lang}")
    else:
        log("      [warn] tesseract not found -- OCR for images / scanned PDFs is off.")
        log("             python setup_deps.py --with-tesseract")
    return pandoc, tess


# ---------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------
def download(url, target):
    log(f"      downloading {os.path.basename(target)}")
    tmp = target + ".part"
    try:
        urllib.request.urlretrieve(url, tmp)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def fetch_lang(lang):
    """Download one language pack into the tessdata folder."""
    td = tessdata_dir(find_tesseract())
    try:
        os.makedirs(td, exist_ok=True)
    except OSError as e:
        log(f"      [warn] cannot create {td}: {e}")
        return None
    target = os.path.join(td, lang + ".traineddata")
    if os.path.isfile(target):
        log(f"      {lang}.traineddata already present, skipped")
        return target
    download(TESSDATA_URL.format(lang), target)
    return target


def install_tesseract():
    """Download the UB-Mannheim installer and run it silently into .\\Tesseract-OCR."""
    dest = os.path.join(BASE_DIR, "Tesseract-OCR")
    os.makedirs(dest, exist_ok=True)
    exe = os.path.join(os.environ.get("TEMP", BASE_DIR), "tesseract-setup.exe")
    log(f"[2/4] Downloading tesseract {TESSERACT_RELEASE} ...")
    download(TESSERACT_URL, exe)
    log(f"      running installer silently into {dest}")
    r = subprocess.run([exe, "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART",
                        f"/DIR={dest}", "/COMPONENTS=main"])
    if r.returncode != 0:
        log(f"      [warn] installer returned {r.returncode}"
            " (admin rights may be required).")
    for lang in LANGS:
        target = os.path.join(dest, "tessdata", lang + ".traineddata")
        if os.path.isfile(target):
            log(f"      {lang}.traineddata already present, skipped")
        else:
            download(TESSDATA_URL.format(lang), target)
    log("      tesseract ready.")


def main():
    p = argparse.ArgumentParser(description="Markdown converter dependency setup")
    p.add_argument("--upgrade", action="store_true",
                   help="upgrade to newest versions, then re-lock requirements.txt")
    p.add_argument("--check", action="store_true", help="probe only, install nothing")
    p.add_argument("--with-tesseract", action="store_true",
                   help="download and install the tesseract OCR engine")
    p.add_argument("--fetch-lang", metavar="LANG",
                   help="download a tesseract language pack, e.g. chi_sim")
    a = p.parse_args()

    log("=" * 60)
    log(" Markdown Converter - setup / environment check")
    log(f" Python {platform.python_version()} @ {sys.executable}")
    log("=" * 60)

    if platform.python_version_tuple() < ("3", "10"):
        log("[warn] Python 3.10+ is recommended.")

    if not a.check:
        pip_install(read_pins(), upgrade=a.upgrade)
    if a.with_tesseract:
        install_tesseract()
    if a.fetch_lang:
        path = fetch_lang(a.fetch_lang)
        if path:
            log(f"      language data: {path}")
    check_tools()

    log("")
    log("=" * 60)
    log(" Done. Usage:")
    log("   drag & drop : drop files onto markdown_convert.bat")
    log("   command line: python converter.py file.pdf")
    log("=" * 60)


if __name__ == "__main__":
    main()
