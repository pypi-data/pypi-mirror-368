class DuplicateEntryError(Exception):
    """Raised when a record being added violates uniqueness constraints."""

    def __init__(self, unique_by: list[str]) -> None:
        super().__init__(f"Duplicate entry found for fields: {unique_by}")
