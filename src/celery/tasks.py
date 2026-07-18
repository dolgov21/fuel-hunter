import asyncio
from html import escape

import httpx
from loguru import logger
from sqlalchemy import select
from src.crawler.client import Client

from src.celery.celery_app import app
from src.core.config import TG_BOT_TOKEN
from src.core.database import session_maker
from src.core.models import Station, TelegramUser, UserStationSubscription
from src.crawler.integration import GdeBenzIntegration

_TELEGRAM_API_BASE_URL = "https://api.telegram.org"
_STATUS_LABELS = {
    "yes": "топливо есть",
    "no": "топлива нет",
    "queue": "есть очередь",
    "low": "мало топлива",
}


def _build_notification_text(station: Station) -> str:
    status = station.status.value if station.status is not None else "unknown"
    status_label = escape(_STATUS_LABELS.get(status, status))

    lines = [
        "⚡ Статус АЗС изменился.",
        "",
        f"<b>{status_label}</b>",
        "",
        "Детали:",
    ]
    if station.details:
        lines.append(f"- адрес: <code>{escape(station.details)}</code>")
    if station.brand:
        lines.append(f"- бренд: {escape(station.brand)}")
    if station.name != station.brand:
        lines.append(f"- АЗС: {escape(station.name)}")

    return "\n".join(lines)


@app.task(expires=15 * 60)
def send_notifications_task(osm_id: str) -> None:
    with session_maker() as session:
        station = session.scalar(select(Station).where(Station.osm_id == osm_id))
        if station is None:
            logger.warning(f"Station {osm_id} not found while sending notifications")
            return

        subscriber_ids = list(
            session.scalars(
                select(TelegramUser.telegram_id)
                .join(
                    UserStationSubscription,
                    UserStationSubscription.telegram_user_id
                    == TelegramUser.telegram_id,
                )
                .where(UserStationSubscription.station_osm_id == osm_id)
            )
        )

    if not subscriber_ids:
        logger.info(f"No subscribers for station {osm_id}")
        return

    message_text = _build_notification_text(station)
    for telegram_id in subscriber_ids:
        send_telegram_notification_task.apply_async(
            args=[telegram_id, message_text, osm_id],
            expires=15 * 60,
        )

    logger.info(f"Scheduled {len(subscriber_ids)} notifications for station {osm_id}")


@app.task(
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
    expires=15 * 60,
)
def send_telegram_notification_task(
    telegram_id: int,
    message_text: str,
    osm_id: str,
) -> None:
    if not TG_BOT_TOKEN:
        logger.error("BOT_TOKEN is not configured; notification was not sent")
        return

    endpoint = f"{_TELEGRAM_API_BASE_URL}/bot{TG_BOT_TOKEN}/sendMessage"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                endpoint,
                json={
                    "chat_id": telegram_id,
                    "text": message_text,
                    "parse_mode": "HTML",
                },
            )
    except httpx.HTTPError:
        raise

    if not response.json().get("ok", False):
        logger.warning(f"Telegram API rejected notification for user {telegram_id}")
        return

    logger.info(f"Notification for station {osm_id} sent to user {telegram_id}")


@app.task(expires=15 * 60)
def dispatch_send_notifications_task(osm_ids: list[str]) -> None:
    for osm_id in osm_ids:
        send_notifications_task.delay(osm_id)
        logger.info(f"Scheduled notifications for station {osm_id}")


async def _sync_stations() -> None:
    from src.crawler.usecases import SyncStationsUseCase

    async with Client() as client:
        gde_benz_integration = GdeBenzIntegration(client)
        sync_stations_usecase = SyncStationsUseCase(gde_benz_integration)
        await sync_stations_usecase()


@app.task(expires=4 * 60)
def sync_stations_beat_task() -> None:
    asyncio.run(_sync_stations())


app.add_periodic_task(
    5 * 60,
    sync_stations_beat_task.s(),
    name="sync station statuses every 5 minutes",
)
