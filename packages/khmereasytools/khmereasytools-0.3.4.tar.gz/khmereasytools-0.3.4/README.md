
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
# To install support for khmercut (khfilter)
pip install khmereasytools[khmercut]

# To install support for khmernltk (khseg, pos_tag, syllable_segment)
pip install khmereasytools[khmernltk]

# To install support for OCR
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
