
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="khmereasytools",
    version="0.3.2",
    author="Nimol Thuon",
    author_email="nimol.thuon@gmail.com",
    description="A simple library for Khmer text processing, including keyword extraction, segmentation, OCR, and validation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/back-kh/khmereasytools",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires='>=3.6',
    install_requires=[
        "khmercut>=0.1.0",
        "khmernltk>=1.6",
        "pytesseract>=0.3.8",
        "Pillow>=9.0.0"
    ],
)
