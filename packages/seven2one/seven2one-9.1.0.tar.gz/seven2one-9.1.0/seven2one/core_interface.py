from abc import ABC, abstractmethod

from seven2one.core_config import TechStackConfig
from seven2one.core_metadata import TechStackMetaData

class ITechStack(ABC):
    @property
    @abstractmethod
    def config(self) -> TechStackConfig:
        pass

    @config.setter
    @abstractmethod
    def config(self, value: TechStackConfig) -> None:
        pass

    @property
    @abstractmethod
    def metaData(self) -> TechStackMetaData:
        pass

    @metaData.setter
    @abstractmethod
    def metaData(self, value: TechStackMetaData) -> None:
        pass

    @abstractmethod
    def get_access_token(self) -> str:
        pass