from typing import Protocol

from shop_assistant.entity.models import QuestionFacts, Reply
from shop_assistant.service.shop_policy import ShopPolicyService


class ClassificationError(Exception):
    """The external classifier could not produce a valid result."""


class Classifier(Protocol):
    async def classify(self, text: str) -> QuestionFacts: ...


class AnswerQuestionUseCase:
    def __init__(self, classifier: Classifier, policy: ShopPolicyService):
        self.classifier = classifier
        self.policy = policy

    async def execute(self, text: str) -> tuple[Reply, ...]:
        facts = await self.classifier.classify(text)
        return self.policy.evaluate(facts)
