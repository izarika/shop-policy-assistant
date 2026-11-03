import logging
from typing import Literal

from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field

from shop_assistant.entity.models import QuestionFacts, Topic
from shop_assistant.usecase.answer_question import ClassificationError

logger = logging.getLogger(__name__)


class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    topics: list[Literal["product", "delivery", "order_status", "return", "refund", "discount", "unknown"]] = Field(min_length=1, max_length=7)
    return_days: int | None = Field(ge=0, le=100000)
    opened: bool | None
    defective: bool | None
    product: Literal["x1", "other", "unspecified"]


class LLMClassifier:
    def __init__(self, client: AsyncOpenAI, model: str, prompt: str):
        self.client = client
        self.model = model
        self.prompt = prompt

    async def classify(self, text: str) -> QuestionFacts:
        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=[{"role": "system", "content": self.prompt}, {"role": "user", "content": text}],
                text_format=Extraction,
                reasoning={"effort": "low"},
                max_output_tokens=1500,
                store=False,
            )
            parsed = response.output_parsed
            if response.status != "completed" or parsed is None:
                raise ValueError("Incomplete or refused classification")
            return QuestionFacts(
                topics=tuple(Topic(t) for t in parsed.topics),
                return_days=parsed.return_days,
                opened=parsed.opened,
                defective=parsed.defective,
                product=parsed.product,
            )
        except Exception as exc:
            # Do not log request contents, credentials or provider response bodies.
            logger.warning("classification_failed error_type=%s", type(exc).__name__)
            raise ClassificationError("Classifier unavailable") from None
