import re
import argparse

class UyghurCurrency:
    def __init__(self):
        """
        convert currency
        """
        self.symbol_to_uyghur = {
            "$": "ئامېرىكا دوللىرى",
            "€": "ياۋرو",
            "¥": "يۈەن",
            "₺": "تۈركىيە لىراسى",
            "USD": "ئامېرىكا دوللىرى",
            "EUR": "ياۋرو",
            "CNY": "يۈەن",
            "TRY": "تۈركىيە لىراسى",
            "JPY": "ياپونىيە يېنى",
        }

    def convert_currency_symbol_to_text(self, text):
        """
        currency symbol or code convert to Uyghur text
        :param text: uyghur text
        """
        for symbol, uyghur_name in self.symbol_to_uyghur.items():
            if symbol in {"$", "€", "¥", "₺"}:
                pattern = rf"\{symbol}(\d+(?:\.\d+)?)"
            else:
                pattern = rf"\b{symbol}(\d+(?:\.\d+)?)"
            text = re.sub(pattern, rf"\1 {uyghur_name}", text)
        return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert currency symbols/codes to Uyghur text.")
    parser.add_argument("text", type=str, help="Input text containing currency symbols or codes.")
    args = parser.parse_args()

    conv = UyghurCurrency()
    result = conv.convert_currency_symbol_to_text(args.text)
    print(result)
