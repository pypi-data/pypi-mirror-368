from src.registry.guard import GuardrailResponseModel
from src.helpers import Trie
from openai.types.responses import ResponseTextDeltaEvent


class BanListStreamingGuardrail:
    """
    A guardrail for streaming responses that validates each output chunk against a list of banned words.
    If any banned phrase is detected in the output, the guardrail will signal failure.
    """

    def __init__(self, banned_word_list: list[str], *args, **kwargs) -> None:
        """
        Initialize the guardrail with a list of banned words.

        :param banned_word_list: A list of banned words/phrases.
        :param kwargs: Optional keyword arguments.
            - MAX_BANNED_WORD_LENGTH: Maximum length of tokens to check (default is 50).
        """
        self.trie = Trie(banned_word_list)
        self.max_banned_word_length = kwargs.get("MAX_BANNED_WORD_LENGTH", 100)

    def add_banned_word(self, word: str) -> None:
        """
        Add a new banned word
        """
        self.trie.insert(word)

    async def validate(
        self, stream: ResponseTextDeltaEvent, *args, **kwargs
    ) -> GuardrailResponseModel:
        """
        Validate a streaming delta event against banned phrases.

        :param stream: The ResponseTextDeltaEvent from the streaming API.
        :param kwargs: Additional keyword arguments.
            - preceding_tokens: A string representing tokens that have been processed before.
        :return: A GuardrailResponseModel indicating if the output is valid or if a banned word was detected.
        """
        if not isinstance(stream, ResponseTextDeltaEvent):
            raise TypeError(f"Expected ResponseTextDeltaEvent, got {type(stream)}")

        preceding_tokens = kwargs.get("preceding_tokens", "")
        if not isinstance(preceding_tokens, str):
            raise TypeError("preceding_tokens must be a string")

        query = (preceding_tokens + stream.delta).lower()

        query = query[-self.max_banned_word_length :]
        n = len(query)

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
