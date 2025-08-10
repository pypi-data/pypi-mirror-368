from abc import ABC, abstractmethod

from pydantic import BaseModel


class GuardrailResponseModel(BaseModel):
    valid: bool = True
    failure_message: str | None = None
    guardrail_failed: str | None = None

    class Config:
        extra = "allow"


class Guardrail(ABC):
    @abstractmethod
    async def validate(
        self, query: str, *args, **kwargs
    ) -> GuardrailResponseModel:  # pragma: no cover
        pass
