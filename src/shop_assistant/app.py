import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from openai import AsyncOpenAI

from shop_assistant.config import RESOURCES, Settings, load_knowledge
from shop_assistant.controller.telegram import create_router
from shop_assistant.repo.webapi.llm_classifier import LLMClassifier
from shop_assistant.service.shop_policy import ShopPolicyService
from shop_assistant.usecase.answer_question import AnswerQuestionUseCase


def build_usecase(settings: Settings, client: AsyncOpenAI):
    regulation = load_knowledge()
    prompt = (RESOURCES / "system_prompt.txt").read_text(encoding="utf-8")
    classifier = LLMClassifier(client, settings.model, prompt)
    return AnswerQuestionUseCase(classifier, ShopPolicyService(regulation.return_days)), regulation


async def run() -> None:
    settings = Settings.load()
    if not settings.telegram_token:
        raise ValueError("Set TELEGRAM_BOT_TOKEN in .env")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    async with AsyncOpenAI(api_key=settings.api_key, timeout=25, max_retries=1) as client:
        usecase, regulation = build_usecase(settings, client)
        async with Bot(settings.telegram_token) as bot:
            await bot.set_my_commands([
                BotCommand(command="start", description="Начать работу"),
                BotCommand(command="rules", description="Условия покупки"),
            ])
            dispatcher = Dispatcher()
            dispatcher.include_router(create_router(usecase, regulation))
            logging.getLogger(__name__).info("bot_starting model=%s", settings.model)
            await dispatcher.start_polling(bot, tasks_concurrency_limit=4, close_bot_session=False)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
