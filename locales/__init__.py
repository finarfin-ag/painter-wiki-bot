from locales.en import STRINGS as EN
from locales.fa import STRINGS as FA

def get(key: str, lang: str = "en", **kwargs) -> str:
    strings = FA if lang == "fa" else EN
    template = strings.get(key, EN.get(key, ""))
    return template.format(**kwargs) if kwargs else template

def detect_lang(text: str) -> str:
    """Detect if text contains Persian/Arabic script."""
    for char in text:
        if "\u0600" <= char <= "\u06FF":
            return "fa"
    return "en"
