import pytest

from shop_assistant.config import load_knowledge
from shop_assistant.controller.replies import render
from shop_assistant.entity.models import QuestionFacts, Reply, Topic
from shop_assistant.service.shop_policy import ShopPolicyService


@pytest.fixture
def regulation():
    return load_knowledge()


@pytest.mark.parametrize("facts, expected", [
    (QuestionFacts((Topic.ORDER_STATUS,)), (Reply.ORDER_STATUS_UNAVAILABLE, Reply.DELIVERY)),
    (QuestionFacts((Topic.RETURN,), 16, True), (Reply.RETURN_EXPIRED,)),
    (QuestionFacts((Topic.DISCOUNT,)), (Reply.DISCOUNT,)),
    (QuestionFacts((Topic.RETURN,), 14, True, False), (Reply.OPENED_RETURN,)),
    (QuestionFacts((Topic.RETURN,), 15, True, False), (Reply.RETURN_EXPIRED,)),
    (QuestionFacts((Topic.RETURN,), 16, True, True), (Reply.DEFECT,)),
    (QuestionFacts((Topic.RETURN,), 3, True, True), (Reply.DEFECT,)),
    (QuestionFacts((Topic.REFUND,), defective=True), (Reply.DEFECT,)),
    (QuestionFacts((Topic.RETURN,), 3, False, False), (Reply.RETURN,)),
    (QuestionFacts((Topic.UNKNOWN,)), (Reply.UNKNOWN,)),
    (QuestionFacts((Topic.PRODUCT,), product="other"), (Reply.UNKNOWN,)),
    (QuestionFacts((Topic.PRODUCT, Topic.UNKNOWN)), (Reply.PRODUCT, Reply.UNKNOWN)),
    (QuestionFacts((Topic.ORDER_STATUS, Topic.DELIVERY)), (Reply.ORDER_STATUS_UNAVAILABLE, Reply.DELIVERY)),
    (QuestionFacts((Topic.RETURN, Topic.REFUND), defective=True), (Reply.DEFECT,)),
])
def test_policy_decisions(regulation, facts, expected):
    assert ShopPolicyService(regulation.return_days).evaluate(facts) == expected


def test_defect_does_not_promise_three_day_refund(regulation):
    plan = ShopPolicyService(regulation.return_days).evaluate(QuestionFacts((Topic.REFUND,), defective=True))
    text = render(plan, regulation)
    assert "экспертизу" in text
    assert "3 рабочих дня" not in text


def test_expired_return_does_not_promise_refund(regulation):
    plan = ShopPolicyService(regulation.return_days).evaluate(QuestionFacts((Topic.RETURN,), 16, True))
    text = render(plan, regulation)
    assert "экспертиз" not in text.lower()
    assert "брак" not in text.lower()
    assert "на ту же карту" not in text
