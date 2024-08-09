from abc import ABC, abstractmethod


class HazardConfig(ABC):
    @abstractmethod
    def is_complete(self) -> bool:
        pass
