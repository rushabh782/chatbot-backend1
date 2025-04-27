#!/usr/bin/env python
"""
Download required NLTK data.
"""
import nltk

print("Downloading NLTK data...")
nltk.download('punkt')
nltk.download('stopwords')
print("Download complete.")