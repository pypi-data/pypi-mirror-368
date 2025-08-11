import requests
import urllib.parse

class GoogleTranslator:
    def translate(self, text, to_lang="en", from_lang="auto"):
        if isinstance(text, list):
            return [self.translate(t, to_lang, from_lang) for t in text]

        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": from_lang,
            "tl": to_lang,
            "dt": "t",
            "q": text
        }

        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Google Translate API request failed with status {response.status_code}")

        result = response.json()
        return result[0][0][0]
