import asyncio

from aiogram import Bot, Dispatcher

from config import TELEGRAM_TOKEN, setup_logging
from handlers import router

logger = setup_logging()

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set. Check your .env file.")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def main():
    logger.info("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
