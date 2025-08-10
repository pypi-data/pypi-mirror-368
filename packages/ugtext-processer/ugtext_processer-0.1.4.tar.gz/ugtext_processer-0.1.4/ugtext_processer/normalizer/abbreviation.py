import re





EnglishAbbreviations = {
    "kg": " كىلوگىرام",
    "cm": " سېنتىمىتىر",
    "Kg": " كىلوگىرام",
    "Cm": " سېنتىمىتىر",
    "KG": " كىلوگىرام",
    "CM": " سېنتىمىتىر",
    "C°":"سىلسى گىرادۇس",
    "c°":"سىلسى گىرادۇس",

}

ChineseAbbreviations = {

}


UyghurAbbreviations = {


}

class UyghurAbbreviation(object):
    def __init__(self):
        """
        convert abbreviation to abbreviation
        """

    def convert(self, text):
        """
        convert abbreviation to abbreviation
        :param text: abbreviation
        """
        new_dict = {**EnglishAbbreviations, **ChineseAbbreviations, **UyghurAbbreviations}
        for abbrev , expanded in new_dict.items():
            text = text.replace(abbrev, expanded)
        return text





if __name__ == '__main__':
    text = "بۇ يەردە 1kg ئالما بار"
    normalizer = UyghurAbbreviation()
    result = normalizer.convert(text)
    print(result)
