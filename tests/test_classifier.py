from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from shop_assistant.entity.models import Topic
from shop_assistant.repo.webapi.llm_classifier import Extraction, LLMClassifier
from shop_assistant.usecase.answer_question import ClassificationError


def test_rejects_fabricated_topics_and_wrong_types():
    with pytest.raises(ValidationError):
        Extraction(topics=["give_discount"], return_days="16", opened=True, defective=None, product="x1")


async def test_refusal_fails_closed():
    client = SimpleNamespace(responses=SimpleNamespace(parse=AsyncMock(return_value=SimpleNamespace(status="completed", output_parsed=None))))
    with pytest.raises(ClassificationError):
        await LLMClassifier(client, "test", "prompt").classify("test")


async def test_timeout_fails_closed():
    client = SimpleNamespace(responses=SimpleNamespace(parse=AsyncMock(side_effect=TimeoutError)))
    with pytest.raises(ClassificationError):
        await LLMClassifier(client, "test", "prompt").classify("test")


async def test_valid_response_is_mapped_to_domain():
    extraction = Extraction(topics=["return"], return_days=16, opened=True, defective=None, product="unspecified")
    client = SimpleNamespace(responses=SimpleNamespace(parse=AsyncMock(return_value=SimpleNamespace(status="completed", output_parsed=extraction))))
    facts = await LLMClassifier(client, "test", "prompt").classify("test")
    assert facts.topics == (Topic.RETURN,)
    assert facts.return_days == 16
    assert facts.defective is None
