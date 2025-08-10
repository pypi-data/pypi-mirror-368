import re

from ugtext_processer.normalizer.num2str import UyghurNumberConverter


class UyghurNumberNormalizer(object):
    def __init__(self):
        self.converter = UyghurNumberConverter()
        self._number_pattern = re.compile(
            r'(?<![\w.])[-+]?\d+(?:\.\d+)?(?![\w.])'
        )

    def normalize_numbers(self, text: str) -> str:
        """
        Normalize numbers in the given text to their Uyghur string representation.
        """
        def replacer(match):
            num_str = match.group()
            try:
                return self.converter.num2str(float(num_str))
            except Exception:
                return num_str

        return self._number_pattern.sub(replacer, text)

if __name__ == '__main__':
    text = "بۈگۈن 2024/07/26، سائەت 14:30، باھاسى ¥120.5، تېمپېراتۇرا -5.0°C"

    normalizer = UyghurNumberNormalizer()
    result = normalizer.normalize_numbers(text)
    print(text)
    print(result)
