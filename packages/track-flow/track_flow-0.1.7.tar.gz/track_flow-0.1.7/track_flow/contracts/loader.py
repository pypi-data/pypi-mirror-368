from abc import ABC, abstractmethod


class loader(ABC):
    @classmethod
    @abstractmethod
    def load(self, file_path: str, s3_key: str):
        pass
