# ----------------------------------------------------------------------
#  BaseLock
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2021 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Iterable, List
from abc import ABC, abstractmethod

DEFAULT_TTL = 60.0


class BaseLock(ABC):
    """
    Abstract Base Locking primitive.
    Allows exclusive access to all requested items within category.

    Example
    -------
    ```
    lock = BaseLock("test", "test:12")
    with lock.acquire(["obj1", "obj2"]):
        ...
    ```
    """

    def __init__(self, category: str, owner: str, ttl: Optional[float] = None):
        """
        :param category: Lock category name
        :param owner: Lock owner id
        :param ttl: Default lock ttl in seconds
        """
        self.category = category
        self.owner = owner
        self.ttl = ttl or DEFAULT_TTL

    def acquire(self, items: Iterable[str], ttl: Optional[float] = None) -> "Token":
        """
        Acquire lock context manager.

        Example:

        ```
        with lock.acquire(["obj1", "ob2"]):
            ...
        ```
        """
        return Token(self, items, ttl=ttl)

    @abstractmethod
    def acquire_by_items(self, items: List[str], ttl: Optional[float] = None) -> str:
        """
        Acquire lock by list of items
        """

    @abstractmethod
    def release_by_lock_id(self, lock_id: str) -> None:
        """
        Release lock by id
        """


class Token(object):
    """
    Active lock context manager
    """

    def __init__(self, lock: BaseLock, items: Iterable[str], ttl: Optional[float] = None):
        self.lock = lock
        self.items = list(items)
        self.ttl = ttl
        self.lock_id: Optional[str] = None

    def __enter__(self):
        self.lock_id = self.lock.acquire_by_items(self.items, ttl=self.ttl)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_id:
            self.lock.release_by_lock_id(self.lock_id)
