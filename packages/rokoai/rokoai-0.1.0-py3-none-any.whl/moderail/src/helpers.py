import yaml
from pathlib import Path
from itertools import chain
from typing import Optional, Dict, Any


def get_default_banned_word_list() -> list[str]:
    """
    Loads the default banned words from a YAML file.
    """
    current_dir = Path(__file__).resolve().parent
    ban_words_path = current_dir / "fixture" / "ban_words.yaml"
    try:
        with open(ban_words_path, "r") as stream:
            ban_words_dict = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Unable to load ban_words.yaml: {exc}")

    banned_words = list(chain.from_iterable(ban_words_dict.values()))
    return banned_words


class Trie:
    """
    Trie data structure for efficient word and prefix lookup.
    """

    END_OF_WORD = "\ue000"  # Unicode private-use character to mark end of a word

    def __init__(self, words: Optional[list[str]] = None):
        """
        Initialize the trie with an optional list of words.
        """
        self.root: Dict[str, Any] = {}
        if words:
            for word in words:
                self.insert(word)

    def insert(self, word: str) -> None:
        """
        Inserts a word into the trie.
        """
        if not word:
            raise ValueError("Empty word cannot be inserted.")
        word = word.lower()
        current = self.root
        for char in word:
            current = current.setdefault(char, {})
        current[self.END_OF_WORD] = True

    def search_prefix(self, prefix: str) -> tuple[bool, int]:
        """
        Searches for any word in the trie that is a prefix of the input.
        Returns (True, length) if a banned word is matched; otherwise (False, None).
        """
        length = 0
        is_match = False
        current = self.root
        for i, char in enumerate(prefix, start=1):
            if char not in current:
                break
            current = current[char]
            if self.END_OF_WORD in current:
                length = i
                is_match = True
        return is_match, length
