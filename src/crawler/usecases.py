from datetime import datetime, UTC

from loguru import logger
from sqlalchemy import select

from src.celery.tasks import dispatch_send_notifications_task
from src.core.database import async_session_maker
from src.core.models import Station
from src.core.schemas import StationStatus
from src.crawler.integration import GdeBenzIntegration


class SyncStationsUseCase:
    def __init__(self, gde_benz_integration: GdeBenzIntegration):
        self.gde_benz_integration = gde_benz_integration

    async def __call__(self):
        changed_station_ids: list[str] = []
        synchronized_at = datetime.now(UTC)

        async with async_session_maker() as session:
            system_stations = (await session.execute(select(Station))).scalars().all()

            for system_station in system_stations:
                external_station = await self.gde_benz_integration.get_external_status(
                    osm_id=system_station.osm_id
                )

                if system_station.status != external_station.status:
                    previous_status = system_station.status

                    system_station.status = external_station.status
                    system_station.confidence_base = external_station.confidence_base
                    system_station.updated_at = external_station.updated
                    system_station.fuels_now = external_station.fuels_now
                    system_station.details = external_station.addr
                    system_station.updated_at = datetime.now(UTC)

                    # Не уведомляем о неизвестном статусе None
                    unknown_status = external_station.status is None
                    
                    # Не уведомляем о "топлива нет" после None
                    initial_no_fuel = (
                        previous_status is None
                        and external_station.status == StationStatus.NO
                    )
                    
                    if not unknown_status and not initial_no_fuel and external_station.confidence_base > 0.5:
                        changed_station_ids.append(system_station.osm_id)

                    logger.info(
                        f"Station {system_station.osm_id} updated to {external_station.status}"
                    )

                system_station.synchronized_at = synchronized_at

            await session.commit()

        if changed_station_ids:
            dispatch_send_notifications_task.delay(changed_station_ids)
            logger.info(
                f"Dispatched notifications task for {len(changed_station_ids)} stations"
            )
