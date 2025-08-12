from typing import Any

from pydantic import TypeAdapter, ValidationError
from pydantic.fields import FieldInfo

from pydantic_storage._services import FileManager
from pydantic_storage.abstractions import BaseFileStorage
from pydantic_storage.types._generic_types import T
from pydantic_storage.types._model_dict_types import MetaDataDict


class FileStorage(BaseFileStorage[T]):
    def __init__(
        self,
        file_path: str,
        model_class: type[T],
        metadata: MetaDataDict,
        unique_fields: list[str] | None = None,
    ) -> None:
        """Initialize the JsonFileStorage."""
        super().__init__(file_path, model_class, metadata, unique_fields)
        self.manager = FileManager(file_path, model_class, metadata)

    def all(self) -> list[T]:
        """Retrieve all items from the storage."""
        records = self.manager.read().records
        return list(records.values())

    def __validate_kwargs(self, kwargs: dict[str, Any]) -> None:
        field_list: dict[str, FieldInfo] = self.model_class.model_fields
        for key, value in kwargs.items():
            if key not in field_list:
                raise ValidationError(
                    f"Field '{key}' is not a valid field of the model."
                )

            field_info = field_list[key]
            annotation = field_info.annotation

            # Safe validation using Pydantic TypeAdapter
            try:
                TypeAdapter(annotation).validate_python(value)
            except Exception as _:
                raise ValidationError(
                    f"Value for field '{key}' must be of type {annotation}, got {value!r}"
                )

    def get(self, **kwargs: Any) -> T | None:
        """Retrieve an items baased on key-value pairs."""
        self.__validate_kwargs(kwargs)
        for record in self.all():
            if all(getattr(record, k) == v for k, v in kwargs.items()):
                return record
        return None

    def first(self) -> T | None:
        """Retrieve the first item from the storage."""
        records = self.all()
        if len(records) > 0:
            return records[0]
        return None

    def last(self) -> T | None:
        """Retrieve the last item from the storage."""
        records = self.all()
        if len(records) > 0:
            return records[-1]
        return None

    def count(self) -> int:
        """Count the number of items in the storage."""
        return len(self.all())

    def exists(self, **kwargs: Any) -> bool:
        """Check if an item exists by key and value."""
        self.__validate_kwargs(kwargs)
        for record in self.all():
            if all(getattr(record, k) == v for k, v in kwargs.items()):
                return True
        return False

    def next_id(self) -> int:
        """Return next id as for previous recods"""
        previous_recod = self.count()
        return previous_recod + 1

    def create(self, items: list[T]) -> list[T]:
        """Create a new item in the storage."""
        created_records: list[T] = []
        for item in items:
            if not isinstance(item, self.model_class):
                raise ValidationError(
                    f"Item must be an instance of {self.model_class.__name__}, got {type(item).__name__}"
                )
            if not self.exists(**item.model_dump()):
                self.manager.write(
                    {self.next_id(): item},
                )
                created_records.append(item)
        return created_records

    def update(self, items: T, **kwargs: Any) -> T:
        """Update item with provided kwargs"""
        if not isinstance(items, self.model_class):
            raise ValidationError(
                f"Item must be an instance of {self.model_class.__name__}, got {type(items).__name__}"
            )
        self.__validate_kwargs(kwargs)

        records = self.all()
        for i, record in enumerate(records):
            if record == items:
                for key, value in kwargs.items():
                    setattr(record, key, value)
                records[i] = record
                self.manager.write({i + 1: record})
                return record
        raise ValidationError(f"Item {items} not found in storage for update.")

    def filter(self, **kwargs: Any) -> list[T]:
        """Filter items based on kwargs"""
        self.__validate_kwargs(kwargs)
        filtered_records: list[T] = []
        for record in self.all():
            if all(getattr(record, k) == v for k, v in kwargs.items()):
                filtered_records.append(record)
        return filtered_records

    def delete(self, **kwargs: Any) -> list[T] | None:
        """Delete an item by key and value."""
        self.__validate_kwargs(kwargs)
        deleted_record: list[T] = []
        non_deleted_records: dict[int, T] = {}
        for i, record in enumerate(self.all()):
            if all(getattr(record, k) == v for k, v in kwargs.items()):
                deleted_record.append(record)
                del record
                self.manager.write(non_deleted_records)
                return deleted_record
            else:
                non_deleted_records[i + 1] = record
        return None

    def clear(self) -> bool:
        """Clear all items from the storage."""
        self.manager.write({})
        return True
