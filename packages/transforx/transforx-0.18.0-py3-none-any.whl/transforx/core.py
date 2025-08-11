from typing import Union, List
from .engines import google

class Translator:
    def __init__(self):
        self.engines = {
            "google": google.GoogleTranslateEngine(),
            
        }

    def translate(self, text: Union[str, List[str]], to_lang="en", from_lang="auto", engine="google") -> Union[str, List[str]]:
        if engine not in self.engines:
            raise ValueError(f"Engine '{engine}' not supported.")
        engine_instance = self.engines[engine]
        return engine_instance.translate(text, to_lang, from_lang)
