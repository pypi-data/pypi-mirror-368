import requests
from typing import Union, List

class GoogleTranslateEngine:
    GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

    def translate(self, text: Union[str, List[str]], to_lang="en", from_lang="auto") -> Union[str, List[str]]:
        if isinstance(text, list):
            return [self._translate_single(t, to_lang, from_lang) for t in text]
        else:
            return self._translate_single(text, to_lang, from_lang)

    def _translate_single(self, text: str, to_lang: str, from_lang: str) -> str:
        params = {
            "client": "gtx",
            "sl": from_lang,
            "tl": to_lang,
            "dt": "t",
            "q": text,
        }
        try:
            response = requests.get(self.GOOGLE_TRANSLATE_URL, params=params)
            response.raise_for_status()
            result = response.json()
            translated_text = "".join([item[0] for item in result[0]])
            return translated_text
        except Exception as e:
            return f"Error: {str(e)}"
