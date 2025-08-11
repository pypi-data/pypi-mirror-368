from setuptools import setup, find_packages

setup(
    name="bymtoolbox",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[
        "PyMuPDF>=1.18.0",
        "click>=7.0",
        "Pillow>=9.0.0",
        "PyYAML>=6.0",
        "psd-tools>=1.9.0",
        "reportlab>=3.6.0",
        "pandas>=1.3.0",
        "svgwrite>=1.4.1",
        "PyPDF2>=2.0.0",
        "requests>=2.25.0",
        "easyocr>=1.7.0",
        "paddlepaddle",
        "paddleocr",
        "openpyxl>=3.0.0"
    ],
    entry_points={
        'console_scripts': [
            'bt-pdf-extract=bymtoolbox.pdf_extractor:main',
            'bt-image-crop=bymtoolbox.image_cropper:main',
            'bt-image-resize=bymtoolbox.image_resizer:main',
            'bt-pdf2office=bymtoolbox.pdf2X:main',
            'bt-office2pdf=bymtoolbox.X2pdf:main',
            'bt-aiposter=bymtoolbox.aiposter:main',
            'bt-erp-xlsx2html=bymtoolbox.erp_xlsx2html:main',
            'bt-erp-csv2html=bymtoolbox.erp_csv2html:main',
            'bt-cny2asean=bymtoolbox.cny2asean:main',
            'bt-translate=bymtoolbox.bttranslate:main',
            'bt-zh-cate-data=bymtoolbox.zhcateoverview:main',
            # 注意：如果你在 setup.py 目录下没有 __init__.py，或者 bymtoolbox 不是顶层包，安装后可能找不到模块
            # 推荐在 setup.py 同级目录下新建一个空的 __init__.py 文件，确保 bymtoolbox 是包
            'bt-picblend=bymtoolbox.picblend:main',
        ],
    },
    author="Armin",
    author_email="xielingwang@gmail.com",
    description="收集工作生活中常用的命令行工具",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/winmax/bymtool", # FIXME: Replace with your project's GitHub URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,  # 确保包内的 __init__.py 被包含
    zip_safe=False,             # 避免以zip方式安装，防止找不到包
)