from datetime import time
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ClientBase(BaseModel):
    name: str
    status: str
    timezone: str = "America/New_York"
    primary_contact_name: str | None = None
    primary_contact_email: EmailStr | None = None


class ClientCreate(ClientBase):
    pass


class ClientOut(ClientBase):
    id: UUID

    class Config:
        from_attributes = True


class ClientConfigBase(BaseModel):
    alert_mode: str
    daily_brief_time: time | None = None
    daily_brief_delivery_channel: str | None = "email"
    urgent_alert_channel: str | None = "email"
    scenario_frequency_per_week: int = 2
    brief_tone: str = "institutional_concise"
    focus_tags: list[str] | None = None
    high_priority_event_types: list[str] | None = None
    urgent_alert_threshold: float | None = None
    active: bool = True


class ClientConfigCreate(ClientConfigBase):
    client_id: UUID


class ClientConfigOut(ClientConfigBase):
    id: UUID
    client_id: UUID

    class Config:
        from_attributes = True
