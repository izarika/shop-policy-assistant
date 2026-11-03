from dataclasses import dataclass
from enum import StrEnum


class Topic(StrEnum):
    PRODUCT = "product"
    DELIVERY = "delivery"
    ORDER_STATUS = "order_status"
    RETURN = "return"
    REFUND = "refund"
    DISCOUNT = "discount"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class QuestionFacts:
    topics: tuple[Topic, ...]
    return_days: int | None = None
    opened: bool | None = None
    defective: bool | None = None
    product: str = "unspecified"


class Reply(StrEnum):
    PRODUCT = "product"
    DELIVERY = "delivery"
    ORDER_STATUS_UNAVAILABLE = "order_status_unavailable"
    RETURN = "return"
    OPENED_RETURN = "opened_return"
    RETURN_EXPIRED = "return_expired"
    DEFECT = "defect"
    DISCOUNT = "discount"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Regulation:
    return_days: int
    source_rules: tuple[str, ...]
    replies: dict[Reply, str]
