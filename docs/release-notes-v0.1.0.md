## anyfile2md v0.1.0

把 PDF / Word / PPT / Excel / 图片 / 电子书拖到脚本上，直接得到 Markdown。
Drag PDF / Word / PPT / Excel / images / e-books onto a script and get Markdown back.

---

### 中文说明

**Windows 便携版，解压即用**：`anyfile2md-v0.1.0-win64.zip` 已带好 Python 依赖（`lib/`）和 OCR 引擎（`Tesseract-OCR/`），**不需要 pip install**。

前提只有一个：机器上要有 `python.exe`（Python 3.10+）。包内带的是库，不是解释器。

#### 开箱支持

| 格式 | 引擎 | 状态 |
|---|---|---|
| PDF（含扫描版 OCR） | PyMuPDF4LLM | ✅ 直接可用 |
| 电子书 EPUB / MOBI / FB2 / CBZ / XPS / SVG | PyMuPDF4LLM | ✅ 直接可用 |
| Excel (.xlsx/.xls) / CSV | pandas | ✅ 直接可用 |
| 图片 PNG/JPG/TIFF/GIF/BMP/WEBP | tesseract（含 chi_sim + eng） | ✅ 直接可用 |
| Word (.docx) / PPT (.pptx) / HTML | pandoc | ❌ 本版不含 |

#### 关于 pandoc

`.docx` / `.pptx` / `.html` 依赖 pandoc，它**没有打进这个包**（官方二进制 233MB，超过 GitHub 单文件上限）。缺了它这几个格式会直接报错提示，其他格式不受任何影响。

便携版有意**不借用你系统里已装的 pandoc**——包自带的 `lib/` 一存在，程序就进入便携模式，只用包内的工具，行为和在一台干净机器上完全一致。想用系统 pandoc，请改用源码版。

两种处理方式：

```bat
:: 装进包内（推荐，保持自包含）
::   下载 pandoc 的 windows-x86_64.zip，解压出 pandoc.exe 放到
::   anyfile2md-v0.1.0\pandoc\pandoc.exe，程序会自动识别

:: 或用环境变量临时指向
set PANDOC=D:\path\to\pandoc.exe
```

#### 用法

- **拖拽**：把文件拖到 `markdown_convert.bat` 图标上，输出同目录同名 `.md`
- **命令行**：`python converter.py 文件.pdf`
- **环境自检**：`python setup_deps.py --check`

#### 更新日志

- 首次发布
- 转换器路径自动探测，目录可放任意盘符（含中文、空格路径）
- 便携模式：包内有 `lib/` 时只使用包内工具，不读取宿主机 PATH
- `setup_deps.py`：依赖装进本地 `lib/`，支持 `--upgrade` / `--with-tesseract` / `--fetch-lang`
- 拖拽入口改用 `%~dp0` 定位，修复硬编码路径与 GBK 编码乱码问题

---

### English

**Windows portable build — extract and run.** The zip bundles the Python libraries (`lib/`) and the OCR engine (`Tesseract-OCR/`), so there is **no `pip install` step**.

The one prerequisite is a `python.exe` (3.10+) on the machine — the bundle ships libraries, not the interpreter.

#### Works out of the box

| Input | Engine | Status |
|---|---|---|
| PDF (incl. scanned, OCR) | PyMuPDF4LLM | ✅ ready |
| E-books EPUB / MOBI / FB2 / CBZ / XPS / SVG | PyMuPDF4LLM | ✅ ready |
| Excel (.xlsx/.xls) / CSV | pandas | ✅ ready |
| Images PNG/JPG/TIFF/GIF/BMP/WEBP | tesseract (chi_sim + eng) | ✅ ready |
| Word (.docx) / PPT (.pptx) / HTML | pandoc | ❌ not bundled |

#### About pandoc

`.docx` / `.pptx` / `.html` need pandoc, which is **not** bundled (its official Windows binary is 233MB and exceeds GitHub's per-file limit). Without it those three formats raise a clear error; everything else keeps working.

The portable build deliberately **ignores a pandoc installed on your system**: as soon as a local `lib/` exists the program runs in portable mode and only uses bundled tools, so behaviour matches a clean machine exactly. Use the source build if you want system-wide tool discovery.

To add it:

- drop `pandoc.exe` into `anyfile2md-v0.1.0\pandoc\pandoc.exe` (auto-detected), or
- set the `PANDOC` environment variable to point at it.

#### Usage

```bat
python converter.py report.pdf
python converter.py a.xlsx b.png
python converter.py scan.pdf --no-clean
```

Or drop files onto `markdown_convert.bat`; output lands next to the source as `<name>.md`.

#### Changelog

- First release
- Portable tool discovery — any drive, any folder, Chinese/space paths included
- Portable mode: bundled `lib/` means only bundled tools are used, host `PATH` is ignored
- `setup_deps.py` installs into a local `lib/`; supports `--upgrade`, `--with-tesseract`, `--fetch-lang`
- Drag & drop entries resolve their own path (`%~dp0`), fixing the hard-coded path and GBK mojibake issues

---

**Full docs**: [README](https://github.com/echoBai83/anyfile2md#readme) · **License**: MIT
