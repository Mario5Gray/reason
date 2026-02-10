from tree_sitter_languages import get_parser

LANG_MAP = {
    "python": "python",
    "js": "javascript",
    "javascript": "javascript",
    "jsx": "javascript",
    "ts": "typescript",
    "tsx": "tsx",
    "css": "css",
    "scss": "scss",
}

def get_ts_parser(language: str):
    lang = LANG_MAP.get(language.lower())
    if not lang:
        raise ValueError(f"Unsupported language: {language}")
    return get_parser(lang)
