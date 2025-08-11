from typing import Optional
from gql import Client

class TechStackMetaData():
    def __init__(self) -> None:
        self._client = Client()
        self._scheme = None
        self._structure = {}
        self._objects = {}
        self._inventory = {}
        self._inventoryProperty = {}
        return

    @property
    def scheme(self) -> Optional[dict]:
        return self._scheme

    @scheme.setter
    def scheme(self, value: dict) -> None:
        self._scheme = value

    @property
    def structure(self) -> dict:
        return self._structure

    @structure.setter
    def structure(self, value: dict) -> None:
        self._structure = value

    @property
    def objects(self) -> dict:
        return self._objects

    @objects.setter
    def objects(self, value: dict) -> None:
        self._objects = value

    @property
    def inventory(self) -> dict:
        return self._inventory

    @inventory.setter
    def inventory(self, value: dict) -> None:
        self._inventory = value

    @property
    def inventoryProperty(self) -> dict:
        return self._inventoryProperty

    @inventoryProperty.setter
    def inventoryProperty(self, value: dict) -> None:
        self._inventoryProperty = value