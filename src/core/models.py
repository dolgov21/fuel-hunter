from datetime import datetime
from src.core.schemas import StationStatus

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


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
        nullable=True,
        comment="UTC time when the sync beat task synchronized this station.",
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="UTC time when this station was updated on the source website.",
    )

    location: Mapped[Location] = relationship(
        back_populates="stations",
    )
    subscriptions: Mapped[list["UserStationSubscription"]] = relationship(
        back_populates="station",
        cascade="all, delete-orphan",
    )


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str | None] = mapped_column(nullable=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    phone_number: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    subscriptions: Mapped[list["UserStationSubscription"]] = relationship(
        back_populates="telegram_user",
        cascade="all, delete-orphan",
    )


class UserStationSubscription(Base):
    __tablename__ = "user_station_subscriptions"
    __table_args__ = (UniqueConstraint("station_osm_id", "telegram_user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    station_osm_id: Mapped[str] = mapped_column(
        ForeignKey("stations.osm_id", ondelete="CASCADE"),
        nullable=False,
    )
    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("telegram_users.telegram_id", ondelete="CASCADE"),
        nullable=False,
    )

    station: Mapped["Station"] = relationship(back_populates="subscriptions")
    telegram_user: Mapped["TelegramUser"] = relationship(back_populates="subscriptions")
