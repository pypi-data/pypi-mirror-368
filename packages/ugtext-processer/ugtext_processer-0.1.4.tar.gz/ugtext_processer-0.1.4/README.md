# Text Processing for Uyghur Script

`ugtext_processer` is a Python library for processing Uyghur text. It provides tools for normalization, phonemization, and tokenization.

## Features

*   **Normalizer**: Cleans and normalizes Uyghur text by handling punctuation, abbreviations, currency, dates, and numbers.
*   **Phonemizer**: Converts Uyghur text into IPA or ULY Latin script representations.
*   **Tokenizer**: Supports various tokenization strategies, including word, character, BPE, WordPiece, and SentencePiece.

## Installation
 
```bash
pip install ugtext-processer
```

## Usage

### Normalizer

The `normalizer` module provides a simple interface to clean and normalize Uyghur text.

```python
from ugtext_processer.normalizer import normalize

text = "بۈگۈن 2024/07/26 سائەت 14:30، باھاسى ¥120.5، ئېغىرلىقى 2kg"
normalized_text = normalize(text)
print(normalized_text)
```

### Phonemizer

The `phonemizer` module can convert Uyghur text to IPA or ULY Latin script.

```python
from ugtext_processer.phonemizer import UgPhonemizer

# To ULY Latin script
phonemizer_uly = UgPhonemizer(mod=UgPhonemizer.Mod.ULY)
text = "ياخشىمۇسىز؟"
uly_phonemes = phonemizer_uly.phonemizer(text)
print(f"ULY: {''.join(uly_phonemes)}")

# To IPA
phonemizer_ipa = UgPhonemizer(mod=UgPhonemizer.Mod.IPA)
ipa_phonemes = phonemizer_ipa.phonemizer(text)
print(f"IPA: {''.join(ipa_phonemes)}")
```

### Tokenizer

The `tokenizer` module provides a factory to create different types of tokenizers.

```python
from ugtext_processer.tokenizer import TokenizerFactory, TokenizerType

# Word Tokenizer
word_tokenizer = TokenizerFactory.create_tokenizer(TokenizerType.WORD)
text = "بۇ بىر ئاددىي جۈملە."
tokens = word_tokenizer.tokenize(text)
print(f"Word Tokens: {tokens}")

# Character Tokenizer
char_tokenizer = TokenizerFactory.create_tokenizer(TokenizerType.CHARACTER)
tokens = char_tokenizer.tokenize(text)
print(f"Character Tokens: {tokens}")
```

## Modules

### `ugtext_processer.normalizer`

This module contains functions to normalize Uyghur text. The main function is `normalize`, which applies the following steps in order:

1.  `UyghurPunctuationNormalizer`: Normalizes and cleans punctuation.
2.  `UyghurAbbreviation`: Expands common abbreviations.
3.  `UyghurCurrency`: Converts currency symbols to text.
4.  `UyghurDateNormalizer`: Normalizes dates and times into spoken form.
5.  `UyghurNumberNormalizer`: Converts numbers into spoken form.

### `ugtext_processer.phonemizer`

This module provides the `UgPhonemizer` class for converting Uyghur text into phonetic representations.

*   `UgPhonemizer(mod: Mod)`: The constructor takes a `mod` argument which can be `UgPhonemizer.Mod.IPA` or `UgPhonemizer.Mod.ULY`.
*   `phonemizer(text: str)`: The main method that performs the conversion.

### `ugtext_processer.tokenizer`

This module provides a `TokenizerFactory` for creating various tokenizers.

*   `TokenizerFactory.create_tokenizer(tokenizer_type: TokenizerType, **kwargs)`: Creates a tokenizer instance.
*   `TokenizerType`: An enum with the following values:
    *   `WORD`
    *   `CHARACTER`
    *   `BPE`
    *   `WORDPIECE`
    *   `SENTENCEPIECE`