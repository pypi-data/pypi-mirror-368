
# Khmer Easy Tools

A simple, user-friendly Python library for common Khmer Natural Language Processing (NLP) tasks. This package provides easy-to-use functions for keyword extraction, segmentation, POS tagging, OCR, and character validation.

## Installation

Install the package using pip:

```bash
pip install khmereasytools
```

**For OCR functionality**, you must also install Google's Tesseract OCR engine on your system.
-   [Tesseract Installation Guide](https://github.com/tesseract-ocr/tesseract/wiki)
-   Make sure to install the Khmer (`khm`) language data.

## How to Use

### Khmer Character Validation (`is_khmer`)
Checks if a string contains Khmer characters.
```python
import khmereasytools as ket

print(ket.is_khmer("សួស្តី"))  # True
print(ket.is_khmer("Hello")) # False
```

### Keyword Extraction (`khfilter`)
Segments text and removes stop words.
```python
import khmereasytools as ket
text = "នេះគឺជាប្រាសាទអង្គរវត្តស្ថិតនៅក្នុងខេត្តសៀមរាប"
keywords = ket.khfilter(text)
print(f"Keywords: '{{keywords}}'")
```

### Text Segmentation (`khseg`)
Segments text into words using `khmer-nltk`.
```python
import khmereasytools as ket
text = "នេះគឺជាប្រាសាទអង្គរវត្ត"
words = ket.khseg(text)
print(f"Segmented Words: {words}")
```

### Syllable Segmentation (`syllable_segment`)
Segments text into syllables.
```python
import khmereasytools as ket
text = "សាលារៀន"
syllables = ket.syllable_segment(text)
print(f"Syllables: {syllables}")
```

### Part-of-Speech Tagging (`pos_tag`)
Tags words with their part of speech.
```python
import khmereasytools as ket
text = "ខ្ញុំ ស្រឡាញ់ ភាសាខ្មែរ"
tags = ket.pos_tag(text)
print(f"POS Tags: {tags}")
```

### OCR from Image (`ocr_from_image`)
Extracts Khmer text from an image.
```python
import khmereasytools as ket
# Make sure you have an image file e.g., 'khmer_text.png'
# text_from_image = ket.ocr_from_image('khmer_text.png')
# print(f"Text from OCR: {{text_from_image}}")
```
