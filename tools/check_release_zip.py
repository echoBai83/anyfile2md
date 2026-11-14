import zipfile
import sys

z = zipfile.ZipFile(sys.argv[1])
names = z.namelist()
root = "anyfile2md-v0.1.0/"
src = z.read(root + "converter.py").decode("utf-8")
problems = []

if "def portable_mode" not in src:
    problems.append("converter.py is missing portable_mode()")
if "def _search_pandoc" not in src:
    problems.append("converter.py is missing _search_pandoc()")
if any("__pycache__" in n for n in names):
    problems.append("zip contains __pycache__ entries")
for required in (
    root + "Tesseract-OCR/tesseract.exe",
    root + "Tesseract-OCR/tessdata/chi_sim.traineddata",
    root + "Tesseract-OCR/tessdata/eng.traineddata",
    root + "lib/pymupdf4llm/__init__.py",
    root + "lib/pandas/__init__.py",
    root + "markdown_convert.bat",
    root + "install.bat",
    root + "setup_deps.py",
    root + "README.md",
):
    if required not in names:
        problems.append("missing entry: " + required)

print("entries:", len(names))
if problems:
    for p in problems:
        print("PROBLEM:", p)
    sys.exit(1)
print("zip contents OK")
