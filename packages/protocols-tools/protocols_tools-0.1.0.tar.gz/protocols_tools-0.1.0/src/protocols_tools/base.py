from __future__ import annotations
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

class RequestResult(Enum):
    SUCCESS = 1
    FAILED = 0


@dataclass
class RequestResponse:
    """ A wrapper around a client's request to indicate the cli
    how to display the result (as FAILED or SUCCEDD)
    """
    status: RequestResult
    content: Any


class BaseClient(ABC):

    @abstractmethod
    def request(self) -> RequestResponse:
        raise NotImplementedError


    @abstractmethod
    def connect(self) -> None:
        """ Should do everything before a request"""
        raise NotImplementedError

    def __enter__(self) -> BaseClient:
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass