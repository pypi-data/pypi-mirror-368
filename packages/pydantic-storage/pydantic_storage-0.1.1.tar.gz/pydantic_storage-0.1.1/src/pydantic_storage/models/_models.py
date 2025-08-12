from datetime import datetime, timezone
from typing import ClassVar, Generic

from pydantic import BaseModel, ConfigDict, Field

from ..types import T


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Timestamp(BaseModel):
    created_at: datetime = Field(
        default_factory=now_utc,
        description="Creation timestamp (UTC)",
    )
    accessed_at: datetime = Field(
        default_factory=now_utc,
        description="Last accessed timestamp (UTC)",
    )
    modified_at: datetime = Field(
        default_factory=now_utc,
        description="Last modified timestamp (UTC)",
    )


class Storage(BaseModel):
    backend: str = Field(..., description="Storage backend type (e.g., local, s3, ...)")
    format: str = Field(
        ..., description="Storage backend format (e.g., json, yml, ...)"
    )
    encryption: str = Field(..., description="Encryption method used (e.g., AES256)")
    uri: str = Field(..., description="Storage backend location")


class MetaData(BaseModel):
    version: str = Field(
        default="1.0.0",
        description="Schema or file version",
        pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$",
    )
    title: str = Field(..., description="Human-readable title of the file")
    description: str = Field(..., description="Brief description of the file contents")
    storage: Storage | None = None
    timestamps: Timestamp = Timestamp()


class Data(BaseModel, Generic[T]):
    metadata: MetaData
    records: list[T] = Field(
        default_factory=list[T],
        description="Keyed collection of typed records",
    )

    model_config = ConfigDict(extra="forbid")

    json_schema_extra: ClassVar = {
        "examples": [
            {
                "metadata": {
                    "version": "1.0.0",
                    "title": "Example File",
                    "description": "Sample metadata",
                    "storage": {
                        "type": "file",
                        "format": "json",
                        "encryption": "AES256",
                    },
                    "timestamps": {
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-07-01T00:00:00Z",
                    },
                },
                "records": [
                    {"id": 1, "name": "Alice"},
                    {"id": 2, "name": "Bob"},
                ],  # Example records,
            }
        ]
    }
