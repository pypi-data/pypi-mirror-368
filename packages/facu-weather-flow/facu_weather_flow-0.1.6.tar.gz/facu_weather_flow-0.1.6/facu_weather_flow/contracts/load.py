from abc import ABC, abstractmethod


class loader(ABC):
    @classmethod
    @abstractmethod
    def loadData(self):
        pass
