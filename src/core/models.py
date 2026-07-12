from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class StationStatus(StrEnum):
    YES = "yes"
    NO = "no"
    QUEUE = "queue"
    LOW = "low"


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    lon: Mapped[float] = mapped_column(Float(precision=53), nullable=False)

    stations: Mapped[list["Station"]] = relationship(
        back_populates="location",
    )


class Station(Base):
    __tablename__ = "stations"

    osm_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    brand: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[StationStatus | None] = mapped_column(
        Enum(
            StationStatus,
            name="station_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=True,
    )
    confidence_base: Mapped[float] = mapped_column(Float, nullable=False)
    fuels_now: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    synchronized_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="UTC time when the sync beat task synchronized this station.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="UTC time when this station was updated on the source website.",
    )

    location: Mapped[Location] = relationship(
        back_populates="stations",
    )
