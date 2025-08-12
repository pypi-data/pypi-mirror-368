import cleantext

SPECIAL_SYMBOLS = ["♠", "♦", "♣", "♥", "®", "™", "©"]


class Cleaner(object):
    @staticmethod
    def clean(sentence: str, **kwargs):
        for sp in SPECIAL_SYMBOLS:
            sentence = sentence.replace(sp, "")
        return cleantext.clean(sentence, **kwargs)
