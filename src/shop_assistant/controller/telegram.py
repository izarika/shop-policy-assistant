import logging
import time

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from shop_assistant.controller.replies import TECHNICAL_ERROR, render
from shop_assistant.entity.models import Regulation
from shop_assistant.usecase.answer_question import AnswerQuestionUseCase, ClassificationError

logger = logging.getLogger(__name__)


def create_router(usecase: AnswerQuestionUseCase, regulation: Regulation) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer("Здравствуйте! Подскажу по наушникам X1, доставке и возврату. Что вас интересует?\n\n/rules — условия покупки.", reply_markup=ReplyKeyboardRemove())

    @router.message(Command("rules"))
    async def rules(message: Message) -> None:
        await message.answer("Условия покупки:\n\n" + "\n\n".join(regulation.source_rules))

    @router.message(F.text)
    async def answer(message: Message) -> None:
        text = message.text or ""
        if len(text) > 3000:
            await message.answer("Пожалуйста, сократите вопрос до 3000 символов.")
            return
        started = time.monotonic()
        try:
            plan = await usecase.execute(text)
            result = render(plan, regulation)
        except ClassificationError:
            result = TECHNICAL_ERROR
        await message.answer(result)
        logger.info("question_processed duration_ms=%d", (time.monotonic() - started) * 1000)

    @router.message()
    async def unsupported(message: Message) -> None:
        await message.answer("Пожалуйста, отправьте вопрос текстом.")

    return router
