from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from src.core.schemas import StationStatus


def to_camel(field_name: str) -> str:
    parts = field_name.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class IntegrationSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class CommentResponseSchema(IntegrationSchema):
    status: StationStatus | None
    confidence_base: float
    updated: datetime | None
    fuels_now: str | None
    addr: str | None

    @field_validator("fuels_now", "addr", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        return None if value is None else value
