from abc import ABC
from typing import Optional, Union
import pandas as pd

class IDynamicObjects(ABC):
    def inventories(self, fields: Optional[list] = None, where: Optional[str] = None, orderBy: Optional[str] = None, asc: bool = True) -> Optional[pd.DataFrame]:
        raise NotImplementedError

    def items(self, inventoryName: str, references: bool = False, fields: Union[list, str, None] = None, where: Union[list, tuple, str, None] = None, orderBy: Union[dict, list, str, None] = None, asc: Union[list, str, bool] = True, pageSize: int = 5000, arrayPageSize: int = 100000, top: int = 100000, validityDate: Optional[str] = None, allValidityPeriods: bool = False, includeSysProperties: bool = False, maxRecursionDepth: int = 2) -> pd.DataFrame:
        raise NotImplementedError

    def inventoryProperties(self, inventoryName: str, namesOnly: bool = False) -> Union[pd.DataFrame, list, None]:
        raise NotImplementedError

    def propertyList(self, inventoryName: str, references: bool = False, dataTypes: bool = False, maxRecursionDepth: int = 2) -> Union[pd.Series, list, None]:
        raise NotImplementedError

    def filterValues(self, inventoryName: str, top: int = 10000) -> pd.DataFrame:
        raise NotImplementedError

    def addItems(self, inventoryName: str, items: list, chunkSize: int = 5000, pause: int = 1) -> list:
        raise NotImplementedError

    def addValidityItemsToParents(self, inventoryName: str, items: list, chunkSize: int = 5000, pause: int = 1) -> list:
        raise NotImplementedError

    def updateItems(self, inventoryName: str, items: Union[list, dict]) -> Optional[str]:
        raise NotImplementedError

    def updateDataFrameItems(self, inventoryName: str, dataFrame: pd.DataFrame, columns: Optional[list] = None) -> None:
        raise NotImplementedError

    def createInventory(self, name: str, properties: list, variant: Optional[str] = None, propertyUniqueness: Optional[list] = None, historyEnabled: bool = False, hasValitityPeriods: bool = False, isDomainUserType: bool = False) -> Optional[str]:
        raise NotImplementedError

    def deleteInventories(self, inventoryNames: list, deleteWithData: bool = False, force: bool = False) -> None:
        raise NotImplementedError

    def variants(self) -> Optional[pd.DataFrame]:
        raise NotImplementedError

    def deleteVariant(self, variantId: str, force: bool = False) -> None:
        raise NotImplementedError

    def deleteItems(self, inventoryName: str, inventoryItemIds: Optional[list] = None, where: Optional[str] = None, force: bool = False, pageSize: int = 500) -> None:
        raise NotImplementedError

    def clearInventory(self, inventoryName: str, force: bool = False, pageSize: int = 500) -> None:
        raise NotImplementedError

    def updateVariant(self, variantName: str, newName: Optional[str] = None, icon: Optional[str] = None) -> None:
        raise NotImplementedError

    def updateArrayProperty(self, inventoryName: str, inventoryItemId: str, arrayProperty: str, operation: str, arrayItems: Optional[list] = None, cascadeDelete: bool = False) -> None:
        raise NotImplementedError

    def addInventoryProperties(self, inventoryName: str, properties: list) -> None:
        raise NotImplementedError

    def updateDisplayValue(self, inventoryName: str, displayValue: str) -> None:
        raise NotImplementedError

    def updateInventoryName(self, inventoryName: str, newName: str) -> None:
        raise NotImplementedError

    def removeProperties(self, inventoryName: str, properties: list) -> None:
        raise NotImplementedError

    def updateProperty(self, inventoryName: str, propertyName: str, newPropertyName: Optional[str] = None, nullable: Optional[bool] = None) -> None:
        raise NotImplementedError

    def resync(self) -> None:
        raise NotImplementedError

    def defaultDataFrame(self, maxRows: int, maxColumns: int) -> None:
        raise NotImplementedError

    def _convertId(self, sys_inventoryItemId: str) -> Optional[str]:
        raise NotImplementedError

    def _isInventoryOfValidVariant(self, inventoryName: str, variantName: Optional[str] = None) -> Optional[bool]:
        raise NotImplementedError
