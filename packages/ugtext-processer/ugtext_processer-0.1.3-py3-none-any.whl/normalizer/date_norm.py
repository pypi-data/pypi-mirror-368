import re
from typing import List
import argparse
from ugtext_processer.normalizer.num2str import UyghurNumberConverter


class UyghurDateNormalizer(object):
    def __init__(self):
        """
        date normalizer
        """
        self._time_re = re.compile(
            r"""\b
                (?:0?[0-9]|1[0-9]|2[0-3])    # hour
                :
                [0-5][0-9]                   # minutes
                (?:
                    :
                    [0-5][0-9]               # seconds (optional)
                )?
                \b
            """,
            re.VERBOSE,
        )
        self._date_re = re.compile(
            r"""\b
                (?:
                    (?:\d{4}[-/.]\d{1,2}[-/.]\d{1,2})     # yyyy-mm-dd
                    |
                    (?:\d{1,2}[-/.]\d{1,2}[-/.]\d{4})     # dd-mm-yyyy
                )
                \b
            """,
            re.VERBOSE,
        )


        self.number_converter = UyghurNumberConverter()


    def find_dates(self, text: str) -> List[str]:
        """
        Return list of matched date strings
        :param text:
        :return:
        """
        return self._date_re.findall(text)

    def find_times(self, text: str) -> List[str]:
        """
        Return list of matched time strings
        :param text: input text
        :return: list of matched time strings
        """
        return self._time_re.findall(text)

    def _to_ordinal(self, text: str) -> str:
        """
        Convert a number string to ordinal Uyghur form
        If it ends with 'ە', remove it before adding 'ئ‍نچى'
        :param text: string to be converted
        :return: string converted to ordinal Uyghur form
        """
        if text.endswith("ە"):
            return text[:-1] + "ئ‍نچى"
        return text + "ئ‍نچى"
    def normalize_all(self, text: str) -> str:
        """
        Normalize all matched dates and times in the text into Uyghur spoken form
        :param text: text to be normalized
        :return: normalized text
        """

        times = list(set(self.find_times(text)))
        for time_str in times:
            parts = list(map(int, time_str.split(":")))
            s = None
            h = None
            m = None
            if len(parts) == 2:
                h, m = parts[0], parts[1]
            if len(parts) == 3:
                h, m, s = parts[0], parts[1], parts[2]
            uy_hour = self.number_converter.num2str(h) + "دىن"
            if s is None:
                # uy_minute = self.number_converter.num2str(m) + "مىنۇت دا"
                uy_minute = self.number_converter.num2str(m) + "مىنۇت"
                replacement = f"{uy_hour} {uy_minute}"
            else:
                uy_minute = self.number_converter.num2str(m) + "مىنۇت"
                uy_second = self.number_converter.num2str(s) + "سىكوت دا"
                replacement = f"{uy_hour} {uy_minute} {uy_second}"
            text = text.replace(time_str, replacement)

        dates = list(set(self.find_dates(text)))
        for date_str in dates:
            if re.match(r"\d{4}[-/.]", date_str):
                y, m, d = re.split(r"[-/.]", date_str)
            else:
                d, m, y = re.split(r"[-/.]", date_str)
            y, m, d = int(y), int(m), int(d)
            uy_year = self._to_ordinal(self.number_converter.num2str(y)) + " يىلى"
            uy_month = self._to_ordinal(self.number_converter.num2str(m)) + " ئاينىڭ"
            uy_day = self._to_ordinal(self.number_converter.num2str(d)) + " كۈنى"

            replacement = f"{uy_year} {uy_month} {uy_day}"

            text = text.replace(date_str, replacement)

        return text


if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="Uyghur Date & Time Normalizer CLI")
    parser.add_argument("text", type=str, help="Input text containing dates or times")
    args = parser.parse_args()

    normalizer = UyghurDateNormalizer()
    result = normalizer.normalize_all(args.text)

    print(result)




