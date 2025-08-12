from typing import Optional


class Resource:
    _instance: Optional["Resource"] = None

    def __init__(self) -> None:
        if Resource._instance is not None:
            raise RuntimeError(f"Multiple initialization of singleton class: {self.__class__.__name__}")
        Resource._instance = self

    @classmethod
    def get(cls) -> "Resource":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
