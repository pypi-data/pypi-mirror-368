import tree_sitter_c_sharp as tscs

from tree_sitter import Language, Parser, Tree


class TreeSitterService:
    def __init__(self):
        # Preload supported languages using their PyPI packages
        self._language_cache = {
            "c_sharp": Language(tscs.language()),
        }

    def parse_code(self, source_code: str, language_name: str = "c_sharp") -> Tree:
        language = self._get_language(language_name)
        parser = Parser(language)
        return parser.parse(source_code.encode("utf-8"))

    def _get_language(self, language_name: str) -> Language:
        if language_name not in self._language_cache:
            raise ValueError(f"Unsupported language: {language_name}")
        return self._language_cache[language_name]
