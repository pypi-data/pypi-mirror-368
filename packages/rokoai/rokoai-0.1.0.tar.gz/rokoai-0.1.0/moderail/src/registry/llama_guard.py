import logging
from enum import Enum
from openai import AsyncOpenAI
from src.registry.guard import Guardrail, GuardrailResponseModel
from src.config import (
    litellm_base_url,
    litellm_api_key,
    default_timeout,
)


# Configure logging
logger = logging.getLogger(__name__)


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class LlamaGuardrail(Guardrail):
    """
    Leverages LLAMA Guard models via the litellm API to detect harmful or policy-violating content.

    Categories that can be detected and blocked include:
    - S1: Violent Crimes
    - S2: Non-Violent Crimes
    - S3: Sex-Related Crimes
    - S4: Child Sexual Exploitation
    - S5: Defamation
    - S6: Specialized Advice
    - S7: Privacy
    - S8: Intellectual Property
    - S9: Indiscriminate Weapons
    - S10: Hate
    - S11: Suicide & Self-Harm
    - S12: Sexual Content
    - S13: Elections

    Example:
        guardrail = LlamaGuardrail(
            api_key="api_key",
            base_url="https://api.staging.ai71.ai/model-access" ,
            blocked_categories_codes = ["S1", "S2","S12"],
            model="meta-llama/Llama-Guard-3-8B"
        )
        result = await guardrail.validate("I will kill you")
    """

    def __init__(
        self,
        blocked_categories_codes: list[str],
        model: str,
        base_url: str = litellm_base_url,  # type: ignore
        api_key: str = litellm_api_key,  # type: ignore
        timeout: float = default_timeout,
        *args,
        **kwargs,
    ):
        self.category_code_to_name_map = {
            "S1": "Violent Crimes",
            "S2": "Non-Violent Crimes",
            "S3": "Sex-Related Crimes",
            "S4": "Child Sexual Exploitation",
            "S5": "Defamation",
            "S6": "Specialized Advice",
            "S7": "Privacy",
            "S8": "Intellectual Property",
            "S9": "Indiscriminate Weapons",
            "S10": "Hate",
            "S11": "Suicide & Self-Harm",
            "S12": "Sexual Content",
            "S13": "Elections",
        }
        self.blocked_categories_codes = self.validate_blocked_categories_codes(
            blocked_categories_codes
        )

        if not model:
            raise ValueError("Model name cannot be None.")
        self.model = model

        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.timeout = timeout

    async def validate(
        self, query: str | None, conversation: list | None = None, *args, **kwargs
    ) -> GuardrailResponseModel:
        """
        Validates a query or conversation against the blocked categories.

        Args:
            query: The query string to validate.
            conversation: A list representing the conversation context.

        Returns:
            GuardrailResponseModel: The result of the validation.

        Raises:
            ValueError: If neither query nor conversation is provided.
        """
        if conversation is None and query is None:
            raise ValueError("At least one of conversation/query should be set.")

        if not conversation:
            role: Role = kwargs.get("role", Role.USER)
            conversation = await self.prepare_conversation_from_query(query, role=role)  # type: ignore

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=conversation,
                timeout=self.timeout,
            )
        except Exception as e:
            logger.exception("Error in calling LLAMA Guard model")
            return GuardrailResponseModel(
                valid=False,
                failure_message=f"Error in calling LLAMA guardrail. Error: {e}",
                guardrail_failed=self.__class__.__name__,
            )

        response = self.post_processor(response.choices[0].message.content)

        if response[0] == "safe" or (response[1] not in self.blocked_categories_codes):
            return GuardrailResponseModel(valid=True)
        else:
            return GuardrailResponseModel(
                valid=False,
                failure_message=f"Guardrail was triggered due to category {response[1]}: {self.category_code_to_name_map[response[1]]}",
                guardrail_failed=self.__class__.__name__,
            )

    @staticmethod
    async def prepare_conversation_from_query(query: str, role: Role) -> list:
        """
        Prepares a conversation structure from a query string and role.

        Args:
            query: The query string to convert into a conversation.
            role: The role of the participant in the conversation.

        Returns:
            A structured conversation list.

        Raises:
            ValueError: If the role is not a valid Role enum value.
        """
        if role not in [Role.USER, Role.ASSISTANT]:
            raise ValueError("Role should be Role.USER or Role.ASSISTANT.")
        return [
            {
                "role": role.value,
                "content": [
                    {"type": "text", "text": query},
                ],
            }
        ]

    @staticmethod
    def post_processor(response: str) -> tuple:
        """
        Processes the response from the litellm API to determine safety and category.

        Args:
            response: The raw response string from the API.

        Returns:
            A tuple indicating if the content is 'safe' and the category code if applicable.
        """
        response = response.strip()
        if "unsafe" not in response:
            return "safe", None
        return tuple(response.split("\n"))

    def validate_blocked_categories_codes(
        self, blocked_categories_codes: list[str]
    ) -> list[str]:
        """
        Validates the list of blocked category codes against known valid codes.

        Args:
            blocked_categories_codes: The list of category codes to validate.

        Returns:
            The validated list of category codes.

        Raises:
            ValueError: If any code is invalid or if the list is empty.
        """
        if not blocked_categories_codes:
            raise ValueError("Blocked categories codes cannot be an empty list.")
        valid_codes = set(self.category_code_to_name_map.keys())
        for code in blocked_categories_codes:
            if code not in valid_codes:
                raise ValueError(
                    f"Blocked category code '{code}' is not valid. Valid codes are: {valid_codes}"
                )
        return blocked_categories_codes
