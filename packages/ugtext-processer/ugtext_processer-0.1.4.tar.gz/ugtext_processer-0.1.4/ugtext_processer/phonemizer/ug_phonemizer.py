from enum import Enum
import epitran
import re


class UgPhonemizer(object):
    class Mod(Enum):
        IPA = "ipa"
        ULY = "uly latin"

    def __init__(self, mod: Mod = Mod.IPA, punctuation_pattern: str = None,keep_punctuation: bool = False,phonem_boundary:str="_",sentence_boundary: str = "/"):
        """
        Uyghur phonemizer for Arabic-script Uyghur text
        :param mod: Phonemization mode, either IPA or ULY
        :param punctuation_pattern: Optional punctuation pattern override
        :param keep_punctuation: If True, keeps punctuation in the output
        :param sentence_boundary: Token to use for word boundaries
        :param phonem_boundary: Token to use for phoneme boundaries
        """
        self.phonem_boundary = phonem_boundary
        self.mod = mod
        self.punctuation_pattern = punctuation_pattern
        self.keep_punctuation = keep_punctuation
        self.sentence_boundary = sentence_boundary
        if self.mod == self.Mod.IPA:
            self.epi = epitran.Epitran("uig-Arab")

        self.uly_map = {
            # Multi-character sequences
            "ئا": "a", "ئە": "e", "ئې": "ë", "ئى": "i", "ئو": "o", "ئۇ": "u", "ئۆ": "ö", "ئۈ": "ü",

            # Single character mappings
            "ب": "b", "پ": "p", "ت": "t", "ج": "j", "چ": "ch", "خ": "x", "د": "d", "ر": "r",
            "ز": "z", "ژ": "zh", "س": "s", "ش": "sh", "غ": "gh", "ف": "f", "ق": "q", "ك": "k",
            "گ": "g", "ڭ": "ng", "ل": "l", "م": "m", "ن": "n", "ھ": "h", "ۋ": "w", "ي": "y",

            # Vowels
            "ا": "a", "ە": "e", "ې": "ë", "ى": "i", "و": "o", "ۆ": "ö", "ۈ": "ü", "ۇ": "u",

            # Silent character
            "ئ": "i",
        }

        punctuation = {
            '“': '"', '”': '"', '‘': "'", '’': "'",
            '،': ',', '；': ';', '：': ':',
            '؟': '?', '！': '!',
            '（': '(', '）': ')',
            '【': '[', '】': ']',
            '—': '-', '…': '...', '《': '"', '》': '"',".": "。",
        }

        self.punctuation = list(punctuation.keys())

        self.comb_keys = sorted(
            [k for k in self.uly_map.keys() if len(k) > 1], key=lambda x: -len(x)
        )

    def normalize_punctuation(self, text: str) -> str:
        """
        Normalize and remove unwanted punctuation.
        :param text: Input Uyghur text in Arabic script
        :return: Text with punctuation normalized
        """
        if self.keep_punctuation:
            return text
        default_pattern = r"[،！؛؟!,.:‌ـ]"
        pattern = self.punctuation_pattern if self.punctuation_pattern else default_pattern
        text = re.sub(pattern, " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def ipa_phonemizer(self, text: str):
        text = self.normalize_punctuation(text)
        words = text.strip().split()
        phonemes = []
        for i, word in enumerate(words):
            ipa = self.epi.transliterate(word)
            ipa = ipa.replace(" ", "")
            ipa = re.sub(r"[ʔˈʼ]", "", ipa)
            phones = list(ipa)
            phones = [p for ph in phones for p in (ph, self.phonem_boundary)][:-1]
            phonemes.extend(phones)
            if i < len(words) - 1:
                phonemes.append(self.sentence_boundary)

        if phonemes and phonemes[-1] == self.phonem_boundary:
            phonemes.pop()
        return phonemes

    def uly_latin_phonemizer(self, text: str):
        text = self.normalize_punctuation(text)
        phonemes = []
        words = text.strip().split()
        for w_i, word in enumerate(words):
            i = 0
            while i < len(word):
                matched = False
                for k in self.comb_keys:
                    if word[i:i+len(k)] == k:
                        phoneme = self.uly_map[k]
                        matched = True
                        i += len(k)
                        break
                if not matched:
                    c = word[i]
                    if self.keep_punctuation and c in self.punctuation:
                        phonemes.append(c)
                        i += 1
                        continue
                    phoneme = self.uly_map.get(c, " ")

                    i += 1

                if phoneme:
                    phonemes.append(phoneme)
                    phonemes.append(self.phonem_boundary)

            if w_i < len(words) - 1:
                phonemes.append(self.sentence_boundary)

        if phonemes and phonemes[-1] == self.phonem_boundary:
            phonemes.pop()
        return phonemes

    def phonemizer(self, text: str):
        if self.mod == self.Mod.IPA:
            return self.ipa_phonemizer(text)
        elif self.mod == self.Mod.ULY:
            return self.uly_latin_phonemizer(text)
        else:
            raise ValueError("Unsupported mode")


if __name__ == "__main__":



    mode = UgPhonemizer.Mod.ULY
    phonemizer = UgPhonemizer(mod=mode,keep_punctuation=False,phonem_boundary="|",sentence_boundary="/")
    text = "ياخشىمۇسىز؟، ئەسسالامۇ！"
    result = phonemizer.phonemizer(text)
    print(result)