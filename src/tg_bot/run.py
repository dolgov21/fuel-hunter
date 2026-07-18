import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger
from sqlalchemy import literal, select
from sqlalchemy.dialects.postgresql import insert

from src.core.config import TG_BOT_TOKEN
from src.core.database import async_session_maker
from src.core.models import Station, TelegramUser, UserStationSubscription

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()


async def _create_telegram_user(message: Message) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        logger.warning("Cannot create Telegram user: message.from_user is missing")
        return

    phone_number = message.contact.phone_number if message.contact else None

    async with async_session_maker() as session:
        statement = (
            insert(TelegramUser)
            .values(
                telegram_id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
                phone_number=phone_number,
            )
            .on_conflict_do_nothing(index_elements=[TelegramUser.telegram_id])
        )
        await session.execute(statement)
        await session.commit()

        logger.info(
            f"Telegram user {telegram_user.id}, {telegram_user.full_name} created"
        )


async def _subscribe_user_to_all_stations(telegram_id: int) -> None:
    async with async_session_maker() as session:
        statement = (
            insert(UserStationSubscription)
            .from_select(
                ["station_osm_id", "telegram_user_id"],
                select(Station.osm_id, literal(telegram_id)),
            )
            .on_conflict_do_nothing(
                index_elements=[
                    UserStationSubscription.station_osm_id,
                    UserStationSubscription.telegram_user_id,
                ]
            )
        )
        await session.execute(statement)
        await session.commit()
        logger.info(f"Telegram user {telegram_id} subscribed to all stations")


@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    telegram_user = message.from_user
    if telegram_user is None:
        logger.warning("Cannot handle /start: message.from_user is missing")
        return

    await _create_telegram_user(message)
    await _subscribe_user_to_all_stations(telegram_user.id)

    await message.answer(
        "✅ Регистрация прошла успешно!\n\n"
        "⛽ Будем присылать вам уведомления, когда бензин появится на заправках Алатыря."
    )
    logger.info(f"Telegram user {telegram_user.id} registered")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Starting Telegram bot")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
