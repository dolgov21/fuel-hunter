"""add telegram users and station subscriptions

Revision ID: 5aa8d6cf6f81
Revises: 621c4d5079bc
Create Date: 2026-07-15 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "5aa8d6cf6f81"
down_revision: Union[str, Sequence[str], None] = "621c4d5079bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telegram_users",
        sa.Column("telegram_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("telegram_id", name=op.f("pk_telegram_users")),
    )
    op.create_table(
        "user_station_subscriptions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("station_osm_id", sa.String(length=64), nullable=False),
        sa.Column("telegram_user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["station_osm_id"],
            ["stations.osm_id"],
            name=op.f(
                "fk_user_station_subscriptions_station_osm_id_stations"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["telegram_user_id"],
            ["telegram_users.telegram_id"],
            name=op.f(
                "fk_user_station_subscriptions_telegram_user_id_telegram_users"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_station_subscriptions")),
        sa.UniqueConstraint(
            "station_osm_id",
            "telegram_user_id",
            name=op.f("uq_user_station_subscriptions_station_osm_id"),
        ),
    )


def downgrade() -> None:
    op.drop_table("user_station_subscriptions")
    op.drop_table("telegram_users")
