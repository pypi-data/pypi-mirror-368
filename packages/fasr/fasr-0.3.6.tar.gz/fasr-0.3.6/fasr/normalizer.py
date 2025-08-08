import re
import string
from pathlib import Path

from kaldifst import TextNormalizer as normalizer


DEFAULT_DIR = Path(__file__).parent / "asset" / "wetext"

EOS = "<EOS>"
TN_ORDERS = {
    "date": ["year", "month", "day"],
    "fraction": ["denominator", "numerator"],
    "measure": ["denominator", "numerator", "value"],
    "money": ["value", "currency"],
    "time": ["noon", "hour", "minute", "second"],
}
EN_TN_ORDERS = {
    "date": ["preserve_order", "text", "day", "month", "year"],
    "money": ["integer_part", "fractional_part", "quantity", "currency_maj"],
}
ITN_ORDERS = {
    "date": ["year", "month", "day"],
    "fraction": ["sign", "numerator", "denominator"],
    "measure": ["numerator", "denominator", "value"],
    "money": ["currency", "value", "decimal"],
    "time": ["hour", "minute", "second", "noon"],
}


class Token:
    def __init__(self, name):
        self.name = name
        self.order = []
        self.members = {}

    def append(self, key, value):
        self.order.append(key)
        self.members[key] = value

    def string(self, orders):
        output = self.name + " {"
        if self.name in orders.keys():
            if (
                "preserve_order" not in self.members.keys()
                or self.members["preserve_order"] != "true"
            ):
                self.order = orders[self.name]

        for key in self.order:
            if key not in self.members.keys():
                continue
            output += ' {}: "{}"'.format(key, self.members[key])
        return output + " }"


class TokenParser:
    def __init__(self, lang, operator="tn"):
        assert lang in ("en", "zh")
        if lang == "en":
            if operator == "tn":
                self.orders = EN_TN_ORDERS
            else:
                raise NotImplementedError()
        else:
            if operator == "tn":
                self.orders = TN_ORDERS
            elif operator == "itn":
                self.orders = ITN_ORDERS

    def load(self, input):
        assert len(input) > 0
        self.index = 0
        self.text = input
        self.char = input[0]
        self.tokens = []

    def read(self):
        if self.index < len(self.text) - 1:
            self.index += 1
            self.char = self.text[self.index]
            return True
        self.char = EOS
        return False

    def parse_ws(self):
        not_eos = self.char != EOS
        while not_eos and self.char == " ":
            not_eos = self.read()
        return not_eos

    def parse_char(self, exp):
        if self.char == exp:
            self.read()
            return True
        return False

    def parse_chars(self, exp):
        ok = False
        for x in exp:
            ok |= self.parse_char(x)
        return ok

    def parse_key(self):
        assert self.char != EOS
        assert self.char not in string.whitespace

        key = ""
        while self.char in string.ascii_letters + "_":
            key += self.char
            self.read()
        return key

    def parse_value(self):
        assert self.char != EOS
        escape = False

        value = ""
        while self.char != '"':
            value += self.char
            escape = self.char == "\\"
            self.read()
            if escape:
                escape = False
                value += self.char
                self.read()
        return value

    def parse(self, input):
        self.load(input)
        while self.parse_ws():
            name = self.parse_key()
            self.parse_chars(" { ")

            token = Token(name)
            while self.parse_ws():
                if self.char == "}":
                    self.parse_char("}")
                    break
                key = self.parse_key()
                self.parse_chars(': "')
                value = self.parse_value()
                self.parse_char('"')
                token.append(key, value)
            self.tokens.append(token)

    def reorder(self, input):
        self.parse(input)
        output = ""
        for token in self.tokens:
            output += token.string(self.orders) + " "
        return output.strip()


class Normalizer:
    def __init__(
        self,
        tagger_path=None,
        verbalizer_path=None,
        lang="auto",
        operator="tn",
        remove_erhua=False,
        enable_0_to_9=False,
    ):
        self.lang = lang
        self.operator = operator
        self.taggers = {}
        self.verbalizers = {}
        if tagger_path is None or verbalizer_path is None:
            repo_dir = DEFAULT_DIR
            assert lang in ("auto", "en", "zh") and operator in ("tn", "itn")

            taggers = {"en": "tagger.fst", "zh": "tagger.fst"}
            verbalizers = {"en": "verbalizer.fst", "zh": "verbalizer.fst"}
            if operator == "itn" and enable_0_to_9:
                taggers["zh"] = "tagger_enable_0_to_9.fst"
            if operator == "tn" and remove_erhua:
                verbalizers["zh"] = "verbalizer_remove_erhua.fst"

            for lang in ("en", "zh"):
                if self.lang in ("auto", lang):
                    self.taggers[lang] = normalizer(
                        str(repo_dir / lang / operator / taggers[lang])
                    )
                    self.verbalizers[lang] = normalizer(
                        str(repo_dir / lang / operator / verbalizers[lang])
                    )
        else:
            assert lang in (
                "en",
                "zh",
            ), "Language must be 'en' or 'zh' when using custom tagger and verbalizer."
            self.taggers[lang] = normalizer(tagger_path)
            self.verbalizers[lang] = normalizer(verbalizer_path)

    def tag(self, text, lang=None):
        lang = lang or self.lang
        return self.taggers[lang](text)

    def verbalize(self, text, lang=None):
        lang = lang or self.lang
        text = TokenParser(lang, self.operator).reorder(text)
        return self.verbalizers[lang](text)

    @staticmethod
    def contains_chinese(string):
        for ch in string:
            if "\u4e00" <= ch <= "\u9fff":
                return True
        return False

    def normalize(self, text):
        if self.operator == "itn" or bool(re.search(r"\d", text)):
            lang = self.lang
            if lang == "auto":
                lang = "zh" if Normalizer.contains_chinese(text) else "en"
            return self.verbalize(self.tag(text, lang), lang)
        return text
