## anyfile2md v0.1.0

把 PDF / Word / PPT / Excel / 图片 / 电子书拖到脚本上，直接得到 Markdown。
Drag PDF / Word / PPT / Excel / images / e-books onto a script and get Markdown back.

---

### 中文说明

**Windows 便携版，解压即用**：`anyfile2md-v0.1.0-win64.zip` 里已经带好 Python 依赖（`lib/`）和 OCR 引擎（`Tesseract-OCR/`），**不需要单独安装 Python，也不需要 pip install**。

只是有一点前提：机器上要能找到 `python.exe`（Python 3.10+）——包里带的是库，不是解释器。如果你装了 Python，直接双击 `markdown_convert.bat` 开始用。

#### 开箱支持

| 格式 | 引擎 | 状态 |
|---|---|---|
| PDF（含扫描版 OCR） | PyMuPDF4LLM | ✅ 直接可用 |
| 电子书 EPUB / MOBI / FB2 / CBZ / XPS / SVG | PyMuPDF4LLM | ✅ 直接可用 |
| Excel (.xlsx/.xls) / CSV | pandas | ✅ 直接可用 |
| 图片 PNG/JPG/TIFF/GIF/BMP/WEBP | tesseract（含 chi_sim + eng） | ✅ 直接可用 |
| Word (.docx) / PPT (.pptx) / HTML | pandoc | ⚠️ 需自装 pandoc |

**关于 pandoc**：`.docx` / `.pptx` / `.html` 依赖 pandoc，它不在包内（官方二进制体积超 GitHub 单文件上限）。缺了它不影响其他格式，只是这几种会失败、格式清洗步骤会自动跳过。装上即可：
```
winget install --id JohnMacFarlane.Pandoc
```

#### 用法

- **拖拽**：把文件拖到 `markdown_convert.bat` 图标上，输出同目录同名 `.md`
- **命令行**：`python converter.py 文件.pdf`
- **重装/升级依赖**：`install.bat`

#### 更新日志

- 首次发布
- 核心转换器路径自动探测，目录可放任意盘符（含中文、空格路径）
- `setup_deps.py`：依赖装进本地 `lib/`，支持 `--upgrade` / `--with-tesseract` / `--fetch-lang`
- 拖拽入口改为 `%~dp0` 定位，修复硬编码路径与 GBK 编码乱码问题

---

### English

**Windows portable build — extract and run.** The zip ships the Python libraries (`lib/`) and the OCR engine (`Tesseract-OCR/`) pre-bundled, so there is no `pip install` step. You still need a `python.exe` (3.10+) on the machine; the bundle contains the libraries, not the interpreter.

#### Works out of the box

| Input | Engine | Status |
|---|---|---|
| PDF (incl. scanned, OCR) | PyMuPDF4LLM | ✅ ready |
| E-books EPUB / MOBI / FB2 / CBZ / XPS / SVG | PyMuPDF4LLM | ✅ ready |
| Excel (.xlsx/.xls) / CSV | pandas | ✅ ready |
| Images PNG/JPG/TIFF/GIF/BMP/WEBP | tesseract (chi_sim + eng) | ✅ ready |
| Word (.docx) / PPT (.pptx) / HTML | pandoc | ⚠️ install pandoc |

**About pandoc**: `.docx` / `.pptx` / `.html` need pandoc, which is not bundled (its official binary exceeds GitHub's per-file limit). Without it those formats fail and the Markdown clean-up step is skipped; everything else keeps working. Install it with:
```
winget install --id JohnMacFarlane.Pandoc
```

#### Usage

```bat
python converter.py report.pdf
python converter.py a.docx b.xlsx c.png
python converter.py scan.pdf --no-clean
```

Or drop files onto `markdown_convert.bat`. Output lands next to the source file as `<name>.md`.

#### Changelog

- First release
- Portable tool discovery — any drive, any folder, Chinese/space paths included
- `setup_deps.py` installs into a local `lib/`; supports `--upgrade`, `--with-tesseract`, `--fetch-lang`
- Drag & drop entries now resolve their own path (`%~dp0`), fixing the hard-coded path and GBK mojibake issues

---

**Full docs**: [README](https://github.com/echoBai83/anyfile2md#readme) · **License**: MIT
