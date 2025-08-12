from pathlib import Path

from pydantic import ValidationError
from pytest import mark, raises

from pydantic_storage._services import FileStorage
from tests.mocks.models import FakeUser


def test_json_file_storage_initialization(storage: FileStorage[FakeUser]) -> None:
    """Test the initialization of FileStorage."""
    assert isinstance(storage.file_path, Path)
    assert isinstance(storage.model_class, FakeUser)
    assert isinstance(storage.unique_fields, list)


def test_all_records(storage: FileStorage[FakeUser]) -> None:
    """Test the all method of FileStorage."""
    items = storage.all()
    assert isinstance(items, list)
    assert all(isinstance(item, FakeUser) for item in items)


def test_get_record(storage: FileStorage[FakeUser]) -> None:
    """Test the get method of FileStorage."""
    user = storage.get(name="John Doe")
    assert isinstance(user, FakeUser)
    assert user.name == "John Doe"

    # Test with non-existing key-value pair
    user = storage.get(name="Non Existent")
    assert user is None

    # Test with multiple key-value pair
    user = storage.get(
        name="Alice",
        email="alice@gmail.com",
    )
    assert isinstance(user, FakeUser)

    # Test with non-existing multiple key-value pair
    user = storage.get(
        name="Alice",
        email="shailesh@gmail.com",
    )
    assert user is None

    # Test with invalid field
    with raises(ValidationError):
        storage.get(age=25)


def test_first_record(storage: FileStorage[FakeUser]) -> None:
    """Test the first method of FileStorage."""
    first_item = storage.first()
    assert isinstance(first_item, FakeUser)
    assert first_item.id == 1


def test_last_record(storage: FileStorage[FakeUser]) -> None:
    """Test the last records of FileStorage."""
    last_item = storage.last()
    assert isinstance(last_item, FakeUser)
    assert last_item.id == len(storage.all())


def test_count_records(storage: FileStorage[FakeUser]) -> None:
    """Test the count records of FileStorage records"""
    assert len(storage.all()) == storage.count()


def test_exist_record(storage: FileStorage[FakeUser]) -> None:
    """Test the exist method of FileStorage."""
    assert storage.exists(name="John Doe")
    assert not storage.exists(name="Non Existent")

    # Test with multiple key-value pair
    user_exist = storage.exists(
        name="Alice",
        email="alice@gmail.com",
    )
    assert user_exist is True

    # Test with non-existing multiple key-value pair
    user_exist = storage.exists(
        name="Alice",
        email="shailesh@gmail.com",
    )
    assert user_exist is False


@mark.skip(reason="Break pravious test")
def test_create_record(storage: FileStorage[FakeUser]) -> None:
    """Create a new item in the storage."""
    records: list[FakeUser] = storage.create(
        [
            FakeUser(
                id=storage.next_id(),
                name="yash",
                email="yash@gmail.com",
            ),
            FakeUser(
                id=storage.next_id(),
                name="hsialesh",
                email="hsialesh@gmail.com",
            ),
        ]
    )

    assert len(records) == 2


def test_update_record(storage: FileStorage[FakeUser]) -> None:
    """Update an item in the storage."""
    user = storage.get(name="John Doe")
    assert user is not None

    updated_user = storage.update(user, email="johndoeupdated@gmail.com")
    assert updated_user.email == "johndoeupdated@gmail.com"

    # Verify the update
    user_after_update = storage.get(name="John Doe")
    assert user_after_update is not None
    assert user_after_update.email == "johndoeupdated@gmail.com"

    # Test with non-existing record
    with raises(ValidationError):
        storage.update(
            FakeUser(
                id=999,
                name="Non Existent",
                email="johndoeupdated@gmail.com",
            ),
            email="nonexistent@gmail.com",
        )


def test_filter_records(storage: FileStorage[FakeUser]) -> None:
    """Filter items based on kwargs."""
    filtered_users = storage.filter(name="Alice")
    assert isinstance(filtered_users, list)
    assert all(isinstance(user, FakeUser) for user in filtered_users)
    assert len(filtered_users) > 0
    assert filtered_users[0].id == 1
    assert filtered_users[0].name == "Alice"

    # Test with non-existing filter
    filtered_users = storage.filter(name="Non Existent")
    assert len(filtered_users) == 0

    # Test with multiple filters
    filtered_users = storage.filter(
        name="Alice",
        email="alice@gmail.com",
    )
    assert filtered_users[0].id == 1
    assert filtered_users[0].name == "Alice"
