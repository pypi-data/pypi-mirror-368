import argparse

class UyghurNumberConverter(object):
    """
    A class for converting numbers to their Uyghur text representation.
    Supports both integer and decimal numbers, with optional CLI usage.
    """

    DOT = "."
    DOT_FULL = "پۈتۈن"
    MINUS = "مىنۇس"
    DIGITS = ["نۆل", "بىر", "ئىككى", "ئۈچ", "تۆت", "بەش", "ئالتە", "يەتتە", "سەككىز", "توققۇز"]
    TWO_UNITS = ["ئون", "يىگىرمە", "ئوتتۇز", "قىرىق", "ئەللىك", "ئاتمىش", "يەتمىش", "سەكسەن", "توقسان"]
    THREE_UNITS = ["بىر يۈز", "ئىككى يۈز", "ئۈچ يۈز", "تۆت يۈز", "بەش يۈز", "ئالتە يۈز", "يەتتە يۈز", "سەككىز يۈز", "توققۇز يۈز"]
    UNITS = ["", "مىڭ", "مىليون", "مىليارد", "تىرىللىيون", "تىرىللىيات"]
    DECIMAL_UNITS = ["ئوندا", "يۈزدە", "مىڭدە", "ئون مىڭدە", "يۈز مىڭدە", "مىليوندا", "ئون مىليوندا", "يۈز مىليوندا",
                     "مىلياردتا", "ئون مىلياردتا", "يۈز مىلياردتا", "تىرىللىيوندا", "ئون تىرىللىيوندا", "يۈز تىرىللىيوندا"]

    def num2str(self, number: float, integer_accepted_length=14) -> str:
        """
        Convert a number to its Uyghur string representation
        :param number: The numeric value to convert
        :param integer_accepted_length: Maximum length of the integer part before splitting for conversion
        :return: The number spelled out in Uyghur
        """
        if number < 0:
            return self.MINUS + self.num2str(-number)

        number_str = str(number)

        if self.DOT in number_str:
            integer_part, decimal_part = number_str.split('.')
        else:
            integer_part, decimal_part = number_str, ''

        # integer part processing
        if len(integer_part) > integer_accepted_length:
            integer = ""
            integers = self.split_large_number(integer_part).split(" ")
            for item in integers:
                if item.startswith('0'):
                    for sub in item:
                        if sub == "0":
                            integer += " " + self.DIGITS[0]
                        else:
                            integer += " " + self.DIGITS[int(sub)]
                else:
                    integer += " " + self.integer2str(item)
        else:
            integer = self.integer2str(integer_part)

        # decimal part processing
        decimal = ""
        if decimal_part != "" and int(decimal_part) != 0:
            integer += " " + self.DOT_FULL
            decimal = self.decimal2str(decimal_part)

        return (integer + " " + decimal).strip()

    def split_large_number(self, number_str):
        """
        Split a large number into space-separated 3-digit groups
        :param number_str: The numeric string to be grouped
        :return: A space-separated string of 3-digit segments
        """
        parts = [number_str[max(i - 3, 0):i] for i in range(len(number_str), 0, -3)]
        return ' '.join(parts[::-1])

    def convert3digit(self, number: str) -> str:
        """
        Convert a 3-digit string to its Uyghur textual equivalent
        :param number: A string with up to 3 digits
        :return: Uyghur representation of the 3-digit number
        """
        if number == "0":
            return self.DIGITS[0]
        result = ""
        if len(number) == 1:
            result = self.DIGITS[int(number)]
        if len(number) == 2:
            if int(number[0]) != 0:
                result = self.TWO_UNITS[int(number[0]) - 1]
            if int(number[1]) != 0:
                result += " " + self.DIGITS[int(number[1])]
        if len(number) == 3:
            if int(number[0]) != 0:
                result = self.THREE_UNITS[int(number[0]) - 1]
            if int(number[1]) != 0:
                result += " " + self.TWO_UNITS[int(number[1]) - 1]
            if int(number[2]) != 0:
                result += " " + self.DIGITS[int(number[2])]
        return result.strip()

    def integer2str(self, integer_part: str) -> str:
        """
        Convert an integer string into its Uyghur word form
        :param integer_part: String representation of the integer portion
        :return: Uyghur representation of the integer
        """
        group3 = [integer_part[max(i - 3, 0):i][::-1] for i in range(len(integer_part), 0, -3)]
        group3 = group3[::-1]
        group3 = [item[::-1] for item in group3]
        length = len(group3)
        result = ""
        for index, digit3 in enumerate(group3):
            con3 = self.convert3digit(digit3)
            more = self.UNITS[length - index - 1]
            result += " " + con3 + " " + more
        return result.strip()

    def decimal2str(self, decimal_part: str) -> str:
        """
        Convert the decimal part of a number into Uyghur text
        :param decimal_part: String representation of decimal digits
        :return: Uyghur representation of the decimal portion
        """
        length = len(decimal_part)
        prefix = self.DECIMAL_UNITS[length - 1] if length <= len(self.DECIMAL_UNITS) else self.DECIMAL_UNITS[0]
        if length > 14:
            decimal_part = decimal_part[:13]
        integer = self.integer2str(decimal_part)
        return prefix + " " + integer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert number to Uyghur text")
    parser.add_argument("--value", type=float, required=True, help="Number to convert")
    args = parser.parse_args()
    converter = UyghurNumberConverter()
    print(converter.num2str(args.value))
