from pydantic_storage._services import FileManager
from tests.mocks.models import FakeUser

# ================
# FileManager Test
# ================


def test_json_file_manager_instance_created(
    manager: FileManager[FakeUser],
) -> None:
    """Testing json file manager instance creation"""
    assert isinstance(manager, FileManager)
    assert isinstance(manager.data, list)
    assert isinstance(manager.metadata.version, str)
    assert len(manager.metadata.version) == 5
    assert isinstance(manager.metadata.title, str)
    assert isinstance(manager.metadata.description, str)


def test_write_data(
    manager: FileManager[FakeUser],
) -> None:
    data: list[FakeUser] = [
        FakeUser(
            name="shailesh",
            email="shailesh@gmail.com",
        ),
        FakeUser(
            name="yash",
            email="yash@gmail.com",
        ),
        FakeUser(
            name="json",
            email="json@gmail.com",
        ),
        FakeUser(
            name="nice",
            email="nice@gmail.com",
        ),
    ]
    manager.write(data=data)
    assert isinstance(manager.data[0], FakeUser)


def test_write_more_data(
    manager: FileManager[FakeUser],
) -> None:
    data: list[FakeUser] = [
        FakeUser(
            name="yashika",
            email="yashika@gmail.com",
        ),
    ]
    manager.write(data=data)
    assert isinstance(manager.data[-1], FakeUser)
