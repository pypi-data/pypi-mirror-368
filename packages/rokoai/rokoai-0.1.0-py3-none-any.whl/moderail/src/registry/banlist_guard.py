from src.registry.guard import Guardrail, GuardrailResponseModel
from src.helpers import Trie, get_default_banned_word_list


class BanListGuardrail(Guardrail):
    """
    Guardrail that flags input as invalid if it contains any banned word.
    """

    def __init__(self, banned_word_list=None, *args, **kwargs):
        """
        Initializes the guardrail with a list of banned words, or loads from default.
        """
        default_banned_word_list = get_default_banned_word_list()
        if banned_word_list is None:
            banned_word_list = []
        banned_word_list.extend(default_banned_word_list)
        self.trie = Trie(banned_word_list)

    def add_banned_word(self, word: str) -> None:
        """
        Add a new banned word
        """
        self.trie.insert(word)

    async def validate(self, query: str, *args, **kwargs) -> GuardrailResponseModel:
        """
        Validates the input query against a list of banned n-grams using a prefix trie.

        The function scans the query for any banned sequences of words—such as unigrams
        (single words), bigrams (two-word phrases), trigrams (three-word phrases), and
        other n-grams—that match entries in a predefined trie structure. Matching is
        case-insensitive and only considers word boundaries to avoid partial word matches.

        For example, it will match:
          - Unigram: "spam"
          - Bigram: "bad word"
          - Trigram: "not safe for"

        A banned word or phrase is considered matched if:
          - It starts at the beginning of the query or after a space.
          - It ends at the end of the query or is followed by a space.
        """
        n = len(query)
        query = query.lower()
        for i in range(n):
            if i > 0 and query[i - 1] != " ":
                continue
            is_match, length = self.trie.search_prefix(query[i:])
            if is_match and (len(query) == i + length or query[i + length] == " "):
                return GuardrailResponseModel(
                    valid=False,
                    failure_message=f"'{query[i : i + length]}' is a banned word",
                    guardrail_failed=self.__class__.__name__,
                )
        return GuardrailResponseModel()
