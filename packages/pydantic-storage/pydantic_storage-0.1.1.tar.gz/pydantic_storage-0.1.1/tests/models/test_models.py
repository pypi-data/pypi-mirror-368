import re
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from pydantic_storage.models import (
    BaseMetaData,
    FileData,
    FileMetaData,
    Storage,
    Timestamp,
)
from tests.mocks.models import FakeUser

# ===============
# Timestamp Tests
# ===============


def test_timestamp_defaults() -> None:
    ts = Timestamp()
    assert isinstance(ts.created_at, datetime)
    assert isinstance(ts.updated_at, datetime)
    assert ts.created_at.tzinfo == timezone.utc
    assert ts.updated_at.tzinfo == timezone.utc
    assert ts.updated_at >= ts.created_at


def test_timestamp_custom_created_at() -> None:
    custom_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
    ts = Timestamp(created_at=custom_time)
    assert ts.created_at == custom_time
    assert ts.updated_at >= custom_time


# =============
# Storage Tests
# =============


def test_valid_storage() -> None:
    s = Storage(type="s3", encryption="AES256")
    assert s.type == "s3"
    assert s.encryption == "AES256"


def test_invalid_storage_missing_field() -> None:
    with pytest.raises(ValidationError):
        Storage(type="s3")  # type: ignore (missing encryption)


# ==============
# Metadata Tests
# ==============


def test_valid_metadata_version_pattern() -> None:
    meta = BaseMetaData(
        version="1.0.0",
        title="Test File",
        description="Testing metadata",
    )
    assert meta.version == "1.0.0"
    assert re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$", meta.version)


def test_invalid_metadata_version_pattern() -> None:
    with pytest.raises(ValidationError):
        BaseMetaData(
            version="v1",
            title="Invalid",
            description="Bad version pattern",
        )


# ===================
# File Metadata Tests
# ===================


def test_file_metadata_with_timestamps() -> None:
    ts = Timestamp()
    s = Storage(type="local", encryption="none")
    meta = FileMetaData(
        version="1.0.0",
        title="File with TS",
        description="File that has timestamps",
        storage=s,
        timestamps=ts,
    )
    assert isinstance(meta.timestamps, Timestamp)


def test_file_metadata_without_timestamps() -> None:
    s = Storage(type="s3", encryption="AES256")
    meta = FileMetaData(
        version="1.0.0",
        title="File without TS",
        description="Testing no timestamp",
        storage=s,
    )
    assert meta.timestamps is None


# ===============
# File Data Tests
# ===============


def test_file_data_with_records() -> None:
    storage = Storage(type="s3", encryption="AES256")
    metadata = FileMetaData(
        version="1.0.0",
        title="Test File",
        description="File with data",
        storage=storage,
    )
    record = FakeUser(id=1, name="Alice", email="alice@gmail.com")
    file_data: FileData[FakeUser] = FileData[FakeUser](
        metadata=metadata, records={1: record}
    )

    assert file_data.records[1].name == "Alice"
    assert isinstance(file_data.metadata, FileMetaData)


def test_file_data_forbid_extra_fields() -> None:
    storage = Storage(type="local", encryption="none")
    metadata = FileMetaData(
        version="1.0.0",
        title="Test File",
        description="Extra field test",
        storage=storage,
    )
    record = FakeUser(id=2, name="Bob", email="bob@gmail.com")
    data: dict[str, FileMetaData | dict[int, FakeUser] | str] = {
        "metadata": metadata,
        "records": {2: record},
        "extra": "not allowed",
    }

    with pytest.raises(ValidationError):
        FileData[FakeUser](**data)  # type: ignore[arg-type]
