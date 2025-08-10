"""Central registry for Uyghur text normalization rules.

This module collects the various normalization steps defined in the
``app.text.normalizer`` package and exposes a single ``normalize`` function
that executes them in sequence.  The original implementation used
top-level imports which only worked when executing the module as a script.
Using explicit relative imports makes the module importable from anywhere
in the project, enabling other components (e.g. training scripts) to reuse
the normalization pipeline.
"""

from .abbreviation import UyghurAbbreviation
from .num_norm import UyghurNumberNormalizer
from .currency import UyghurCurrency
from .date_norm import UyghurDateNormalizer
from .punctuation import UyghurPunctuationNormalizer

_abbr = UyghurAbbreviation()
_currency = UyghurCurrency()
_date = UyghurDateNormalizer()
_punc = UyghurPunctuationNormalizer()
_number = UyghurNumberNormalizer()


def normalize(text: str) -> str:
    """
    Executes all text normalization steps in sequence:
    1. Normalize punctuation and remove noise symbols
    2. Expand abbreviations
    3. Convert currency symbols and codes to Uyghur text
    4. Normalize date and time expressions
    5. Convert numeric values to their Uyghur spoken form
    """

    text = _punc.normalize(text)
    text = _abbr.convert(text)
    text = _currency.convert_currency_symbol_to_text(text)
    text = _date.normalize_all(text)
    text = _number.normalize_numbers(text)
    return text


if __name__ == "__main__":
    sample = "بۈگۈن 2024/07/26 سائەت 14:30، باھاسى ¥120.5، ئېغىرلىقى 2kg"
    print(normalize(sample))

