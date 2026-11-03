from shop_assistant.entity.models import Regulation, Reply

TECHNICAL_ERROR = "Сейчас не получается ответить. Попробуйте, пожалуйста, немного позже."


def render(replies: tuple[Reply, ...], regulation: Regulation) -> str:
    return "\n\n".join(regulation.replies[key] for key in replies)
