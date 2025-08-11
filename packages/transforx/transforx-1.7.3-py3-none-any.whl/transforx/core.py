from .engines.google import GoogleTranslator

class Translator:
    def __init__(self):
        self.engines = {
            "google": GoogleTranslator()
        }

    def translate(self, text, to_lang="en", from_lang="auto", engine="google"):
        engine_obj = self.engines.get(engine)
        if not engine_obj:
            raise ValueError(f"Engine '{engine}' not found.")
        return engine_obj.translate(text, to_lang, from_lang)
