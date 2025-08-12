from pytest import fixture

from pydantic_storage._services import FileManager, FileStorage
from tests.mocks.models import FakeUser


# Fixture to create a FileManager instance
# --------------------------------------------
@fixture(scope="module")
def manager() -> FileManager[FakeUser]:
    return FileManager[FakeUser](
        uri="tests/db_files/users.json",
        model_class=FakeUser,
        metadata={
            "version": "1.0.0",
            "title": "User records",
            "description": "User record descriptions",
        },
        auto_id_field="id",
    )


@fixture(scope="module")
def storage() -> FileStorage[FakeUser]:
    return FileStorage[FakeUser](
        file_path="./users.json",
        model_class=FakeUser,
        metadata={
            "version": "1.0.0",
            "title": "User records",
            "description": "User record descriptions",
        },
        unique_fields=["id", "email"],
    )
