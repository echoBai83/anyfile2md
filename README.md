# anyfile2md · 任意文件转 Markdown

把常见办公 / 文档 / 图片文件一键转成 Markdown。**把文件拖到脚本图标上就完成转换**。

按需加载、按需调用：每个文件一个一次性进程，转完即退，**无后台常驻**。

```
PDF / Word / PPT / HTML / 电子书 / Excel / CSV / 图片  →  .md
```

---

## 功能一览

| 格式 | 引擎 | 说明 |
|---|---|---|
| **PDF** | PyMuPDF4LLM | 主功能；扫描版可走 OCR |
| **Word (.docx)** | pandoc | 标题 / 列表 / 表格结构还原完整 |
| **PPT (.pptx)** | pandoc | 提取文本与层级结构 |
| **HTML (.html / .htm)** | pandoc | 保留链接与表格 |
| **电子书** EPUB / MOBI / FB2 / CBZ / XPS / SVG | PyMuPDF4LLM / pandoc | |
| **Excel (.xlsx / .xls) / CSV** | pandas | 逐个工作表转成 Markdown 表格 |
| **图片** PNG / JPG / TIFF / GIF / BMP / WEBP | tesseract OCR | 默认识别简体中文 + 英文 |

> 旧版 `.doc` / `.ppt`（2003 格式）不支持，请先用 Office / WPS 另存为 `.docx` / `.pptx`。

---

## 快速开始

### 1. 安装 Python 依赖

需要 **Python 3.10+**（Windows 上装时记得勾选 *Add Python to PATH*）。

```bat
install.bat
```

依赖会装进本目录的 `lib\`，**不污染系统 Python 环境**。想顺带装 OCR 引擎：

```bat
install.bat --with-tesseract
```

### 2. 装两个外部工具（按需）

| 工具 | 用途 | 安装 |
|---|---|---|
| **pandoc** | docx / pptx / html 转换 + Markdown 清洗 | `winget install --id JohnMacFarlane.Pandoc` 或 [官网](https://pandoc.org/installing.html) |
| **tesseract** | 图片、扫描版 PDF 的 OCR | `install.bat --with-tesseract`，或 [UB-Mannheim 构建](https://github.com/UB-Mannheim/tesseract/wiki) |

> 不装也能用：没有 pandoc 就走「跳过清洗」路径（除 docx/pptx/html 外都正常），没有 tesseract 就不做 OCR。

### 3. 转换

**拖拽**：把一个或多个文件拖到 `markdown_convert.bat` 图标上，松开即可。输出与源文件同目录、同名 `.md`。

**命令行**：

```bat
python converter.py 报告.pdf
python converter.py a.pdf b.docx c.xlsx        :: 批量
python converter.py 扫描件.pdf --lang chi_sim  :: 指定 OCR 语言
python converter.py a.pdf --outdir D:\out      :: 指定输出目录
python converter.py a.pdf --no-clean           :: 跳过 pandoc 清洗
python converter.py a.pdf --embed-images       :: 提取 PDF 内嵌图片
python converter.py a.png --no-ocr             :: 关闭 OCR
```

两个拖拽入口的区别：`markdown_convert.bat` = 转换 + pandoc 清洗（日常用这个）；`markdown_convert_noclean.bat` = 保留引擎原始输出，便于排查格式问题。

---

## 目录结构

```
markdown自动转化\
├── markdown_convert.bat          ★ 拖拽入口：转换 + pandoc 清洗
├── markdown_convert_noclean.bat    拖拽入口：原始输出（不清洗）
├── install.bat                    一键安装 / 升级依赖
├── setup_deps.py                  依赖安装与环境探测（跨平台）
├── converter.py                   核心脚本
├── requirements.txt               锁定的依赖版本
├── markdown_convert.ico           图标（可自选快捷方式图标）
├── docs/                          示例文件与图标源图
├── lib/                           ← 安装后生成，不进仓库
└── Tesseract-OCR/                 ← 可选，OCR 引擎，不进仓库
```

---

## 路径与换电脑部署

`converter.py` **不写死任何绝对路径**。pandoc / tesseract 的查找顺序：

1. 环境变量 `PANDOC` / `TESSERACT`
2. 本目录下 `pandoc\pandoc.exe`、`Tesseract-OCR\tesseract.exe`
3. 系统 `PATH`
4. Windows 常见安装位置（`%LOCALAPPDATA%\Pandoc\*`、`%ProgramFiles%\Tesseract-OCR` 等）

所以换电脑只需三步：装 Python → 跑 `install.bat` →（需要 OCR 的话）`install.bat --with-tesseract`。工具目录可以放在任意盘符、任意路径，包括带中文和空格的路径。

---

## 低负荷设计

- **一次性进程**：转完即退，关掉终端后零内存、零 CPU 占用。
- **按需加载**：转哪个格式才 `import` 对应的库，启动快、内存小。
- **按需调用 OCR**：tesseract 只在处理图片 / 扫描 PDF 时启动，转普通文档完全不触发。
- **逐个释放**：批量转换时逐个文件处理，不累积占用。

---

---

## 便携版（免安装）

不想折腾 Python 依赖的话，可以直接下载 **Release** 页面的 `anyfile2md-v0.1.0-win64.zip`：包内已带好 `lib/` 与 `Tesseract-OCR/`，解压即用，不需要 `pip install`（仍需机器上有 Python 3.10+ 解释器）。

需要注意：**包内一旦存在 `lib/`，程序就进入便携模式**，只使用包内自带的 pandoc / tesseract，不再读取系统 `PATH` 上的安装。这是为了保证行为可复现——用系统工具请用源码版。

## 已知限制

- `.doc` / `.ppt` 旧格式不支持。
- 纯图片的扫描 PDF 若不装 tesseract，只会得到空白或图片引用。
- Excel 的超大表格按整表渲染，单文件几万行以上会明显变慢。
- OCR 准确率取决于原图清晰度；`tessdata_fast` 语言包偏向速度，需要更高准确率可换 `tessdata_best`。

## License

MIT，见 [LICENSE](LICENSE)。
