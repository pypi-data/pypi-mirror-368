# bymtoolbox

一个用于工作生活中常用的命令行工具集合。

## 功能特点

- 从 PDF 文件中提取图像
- 将 PDF 转换为 Office 文档 (docx/doc/xlsx/xls)
- 将 Office 文档转换为 PDF
- 图片裁剪工具
- AI海报生成工具（支持PSD/PDF/SVG/JPEG/PNG/AI/Sketch格式，带图层）
- 命令行界面便于自动化操作

## 安装

```bash
pip install bymtoolbox
```

## 使用方法

### PDF 图像提取

```bash
# 从单个 PDF 文件中提取图像
bt-pdf-extract input.pdf

# 从多个 PDF 文件中提取图像
bt-pdf-extract *.pdf

# 指定输出目录
bt-pdf-extract input.pdf --output ./images
```

### PDF 转 Office

```bash
# PDF 转 Word
bt-pdf2office input.pdf -t docx
bt-pdf2office input.pdf -t doc

# PDF 转 Excel
bt-pdf2office input.pdf -t xlsx
bt-pdf2office input.pdf -t xls

# 指定输出路径
bt-pdf2office input.pdf -o output.docx
```

### Office 转 PDF

```bash
# Word 转 PDF
bt-office2pdf input.docx

# Excel 转 PDF
bt-office2pdf input.xlsx

# 指定输出路径
bt-office2pdf input.docx -o output.pdf
```

### 图片裁剪

```bash
# 使用坐标点裁剪
bt-image-crop input.jpg -f "100,100" -t "500,500"

# 使用配置文件批量裁剪
bt-image-crop input.jpg -c crop.yml

# 指定输出目录和前缀
bt-image-crop input.jpg -f "100,100" -t "500,500" -o ./output -p test
```

### CSV 转 HTML

```bash
# 将 CSV 文件转换为带过滤和导出功能的 HTML 表格
bt-erp-csv2html input.csv

# 指定输出文件路径
bt-erp-csv2html input.csv -o output.html

# 指定 CSV 文件编码
bt-erp-csv2html input.csv --encoding gbk
```

### AI海报生成

```bash
# 生成PSD格式海报
bt-aiposter poster_config.yml output.psd

# 生成PDF格式海报
bt-aiposter poster_config.yml output.pdf --format pdf

# 生成SVG矢量图
bt-aiposter poster_config.yml output.svg

# 生成JPEG/PNG位图
bt-aiposter poster_config.yml output.jpg
bt-aiposter poster_config.yml output.png

# 指定JPEG图像质量
bt-aiposter poster_config.yml output.jpg --quality 85

# 生成AI(Adobe Illustrator)文件
bt-aiposter poster_config.yml output.ai

# 生成Sketch文件
bt-aiposter poster_config.yml output.sketch

# 自动根据文件扩展名判断输出格式
bt-aiposter poster_config.yml output.jpg  # 输出JPEG
bt-aiposter poster_config.yml output.svg  # 输出SVG
```

## 项目结构

```
bymtoolbox/
│
├── __init__.py
├── pdf_extractor.py    # PDF 图像提取
├── pdf2X.py           # PDF 转 Office
├── X2pdf.py           # Office 转 PDF
├── image_cropper.py   # 图片裁剪
├── aiposter.py        # AI海报生成
│
├── setup.py           # 包设置和元数据
└── README.md          # 项目文档
```

## 配置文件示例

裁剪配置文件 (crop.yml):

```yaml
image1.jpg:
  - from: "100,100"
    to: "500,500"
  - from: "200,200"
    to: "600,600"

image2.jpg:
  - from: "150,150"
    to: "450,450"
```

海报配置文件 (poster_example.yml):

```yaml
# 背景设置
background:
  # 背景色（当背景图不存在时使用）
  color: "#f5f5f5"
  # 画布大小（当背景图不存在时使用）
  size: [1000, 800]
  # 背景图（可选）
  # image: "path/to/background.jpg"

# 文本图层
texts:
  - content: "海报标题"
    font: "Arial"
    size: 48
    color: "#333333"
    position: [400, 50]

  - content: "这是一段介绍文字"
    font: "Arial"
    size: 24
    color: "#666666"
    position: [100, 150]

# 表格图层
tables:
  - headers: ["产品", "价格", "销量"]
    data: [
      ["产品A", "¥100", "1000"],
      ["产品B", "¥200", "500"]
    ]
    position: [100, 300]
    cell_width: 120
    cell_height: 40

# 图片图层
images:
  - path: "path/to/image.png"
    position: [600, 300]
    opacity: 0.8

# 输出格式设置（可选）
output:
  # JPEG相关设置
  jpeg:
    quality: 95  # 输出质量 1-100

  # SVG相关设置
  svg:
    embed_images: true  # 是否嵌入图像而不是引用

  # PDF相关设置
  pdf:
    compression: true  # 是否启用压缩

  # AI (Adobe Illustrator) 相关设置
  ai:
    version: "2020"  # AI版本信息

  # Sketch 相关设置
  sketch:
    version: "70"  # Sketch版本号
```