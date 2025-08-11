from .core import Translator

_translator = Translator()

def translate(text, to_lang="en", from_lang="auto", engine="google"):
    return _translator.translate(text, to_lang, from_lang, engine)

__all__ = ["translate", "Translator"]
