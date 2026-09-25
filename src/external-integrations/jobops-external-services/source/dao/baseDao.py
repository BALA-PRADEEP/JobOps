from typing import Generic, TypeVar
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseDao(Generic[T]):
    """Small persistence primitive shared by domain repositories.

    Business queries remain in domain repositories; this class only centralizes
    basic session operations.
    """

    def __init__(self, session: Session):
        self.session = session

    def add(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    def flush(self) -> None:
        self.session.flush()
