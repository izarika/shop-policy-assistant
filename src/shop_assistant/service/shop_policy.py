from shop_assistant.entity.models import QuestionFacts, Reply, Topic


class ShopPolicyService:
    def __init__(self, return_days: int):
        self.return_days = return_days

    def evaluate(self, facts: QuestionFacts) -> tuple[Reply, ...]:
        replies: list[Reply] = []
        topics = set(facts.topics)
        if Topic.PRODUCT in topics:
            replies.append(Reply.UNKNOWN if facts.product == "other" else Reply.PRODUCT)
        if Topic.ORDER_STATUS in topics:
            replies.extend((Reply.ORDER_STATUS_UNAVAILABLE, Reply.DELIVERY))
        elif Topic.DELIVERY in topics:
            replies.append(Reply.DELIVERY)
        if topics & {Topic.RETURN, Topic.REFUND}:
            if facts.product == "other":
                replies.append(Reply.UNKNOWN)
            elif facts.defective is True:
                replies.append(Reply.DEFECT)
            elif facts.return_days is not None and facts.return_days > self.return_days:
                replies.append(Reply.RETURN_EXPIRED)
            elif facts.opened is True:
                replies.append(Reply.OPENED_RETURN)
            else:
                replies.append(Reply.RETURN)
        if Topic.DISCOUNT in topics:
            replies.append(Reply.DISCOUNT)
        if Topic.UNKNOWN in topics or not replies:
            replies.append(Reply.UNKNOWN)
        return tuple(dict.fromkeys(replies))
