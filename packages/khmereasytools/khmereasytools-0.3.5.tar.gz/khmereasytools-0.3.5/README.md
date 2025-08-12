
# Khmer Easy Tools

A simple, user-friendly Python library for common Khmer Natural Language Processing (NLP) tasks. This package uses optional dependencies to provide different features.

## Installation

Install the base package (which includes `is_khmer` and stop word utilities):
```bash
pip install khmereasytools
```

### Installing Optional Features

You can install the features you need. This is useful if one of the dependencies has installation issues on your system.

```bash
# To install support for khmercut (for khfilter)
pip install khmereasytools[khmercut]

# To install support for khmernltk (for khseg, khpos, khsyllable)
pip install khmereasytools[khmernltk]

# To install support for OCR (for khocr)
pip install khmereasytools[ocr]

# To install everything
pip install khmereasytools[all]
```

**For OCR functionality**, you must also install Google's Tesseract OCR engine on your system.
-   [Tesseract Installation Guide](https://github.com/tesseract-ocr/tesseract/wiki)
-   Make sure to install the Khmer (`khm`) language data.

## How to Use

### Khmer Character Validation (`is_khmer`)
```python
import khmereasytools as ket
print(ket.is_khmer("សួស្តី"))  # True
```

### Keyword Extraction (`khfilter`)
*Requires `khmercut` to be installed.*
```python
import khmereasytools as ket
# pip install khmereasytools[khmercut]
text = "នេះគឺជាប្រាសាទអង្គរវត្តស្ថិតនៅក្នុងខេត្តសៀមរាប"
keywords = ket.khfilter(text)
print(f"Keywords: '{{keywords}}'")
```

### Text Segmentation (`khseg`)
*Requires `khmernltk` to be installed.*
```python
import khmereasytools as ket
# pip install khmereasytools[khmernltk]
text = "នេះគឺជាប្រាសាទអង្គរវត្ត"
words = ket.khseg(text)
print(f"Segmented Words: {words}")
```

### Syllable Segmentation (`khsyllable`)
*Requires `khmernltk` to be installed.*
```python
import khmereasytools as ket
text = "សាលារៀន"
syllables = ket.khsyllable(text)
print(f"Syllables: {syllables}")
```

### Part-of-Speech Tagging (`khpos`)
*Requires `khmernltk` to be installed.*
```python
import khmereasytools as ket
text = "ខ្ញុំ ស្រឡាញ់ ភាសាខ្មែរ"
tags = ket.khpos(text)
print(f"POS Tags: {tags}")
```

### OCR from Image (`khocr`)
*Requires `ocr` dependencies to be installed.*
```python
import khmereasytools as ket
# pip install khmereasytools[ocr]
# Make sure you have an image file e.g., 'khmer_text.png'
# text_from_image = ket.khocr('khmer_text.png')
# print(f"Text from OCR: {{text_from_image}}")
```
