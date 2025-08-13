from datetime import datetime, timezone
from typing import Optional

from dateutil.parser import isoparse
from pydantic import BaseModel, Field


class APIKey(BaseModel):
    hash_key: Optional[str] = Field(default=None)
    organization_id: str
    api_key: str
    key_name: str
    integration_name: str
    user_id: str = Field(default="")
    security_group_id: str = Field(default="")
    expire_timestamp: datetime
    monthly_request_limit: int
    created_by: str
    created_at: datetime

    def is_expired(self) -> bool:
        """Check if the API key is expired based on the expire_timestamp."""
        current_time = datetime.now()
        return current_time >= self.expire_timestamp


class APIKeyCreate(BaseModel):
    key_name: str
    integration_name: str
    user_id: str = Field(default="")
    security_group_id: str = Field(default="")
    expire_days: int
    monthly_request_limit: int
