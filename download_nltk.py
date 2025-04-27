#!/usr/bin/env python
"""
Download required NLTK data.
"""
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print("Downloading NLTK data...")
nltk.download('punkt')
nltk.download('stopwords')
print("Download complete.")