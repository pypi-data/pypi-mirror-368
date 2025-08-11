# TransforX 

Simple Python translation library using Google Translate unofficial API.

## Installation

```bash
pip install transforx
```

- - -

## Usage
```python
from transforx import translate

print(translate("سلام دنیا", to_lang="en"))
# Output: Hello World

print(translate(["سلام", "دنیا"], to_lang="en"))
# Output: ['Hello', 'World']
```

- - -

## Features
- Translate a text or a list of texts.
- Auto-detect source languages.
- No Api-Key Requested.

- - -
## LICENSE
The project is published with MIT License.
