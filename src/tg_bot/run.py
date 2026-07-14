import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from sqlalchemy import literal, select
from sqlalchemy.dialects.postgresql import insert
from loguru import logger

from src.core.config import TG_BOT_TOKEN
from src.core.database import async_session_maker
from src.core.models import Station, TelegramUser, UserStationSubscription

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()

async def _create_telegram_user(telegram_id: int, name: str) -> None:
    async with async_session_maker() as session:
        statement = (
            insert(TelegramUser)
            .values(telegram_id=telegram_id, name=name)
            .on_conflict_do_nothing(index_elements=[TelegramUser.telegram_id])
        )
        await session.execute(statement)
        await session.commit()

        logger.info(f"Telegram user {telegram_id} created")


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
    await _create_telegram_user(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name,
    )
    await _subscribe_user_to_all_stations(message.from_user.id)

    await message.answer(
        "✅ Регистрация прошла успешно!\n\n"
        "⛽ Будем присылать вам уведомления, когда бензин появится на заправках Алатыря."
    )
    logger.info(f"Telegram user {message.from_user.id} registered")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
