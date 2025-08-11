from abc import ABC
import pandas as pd
from typing import Optional, Union

class ITimeSeries(ABC):
    def getVersion(self) -> str:
        raise NotImplementedError

    def addTimeSeriesItems(
        self,
        inventoryName: str,
        timeSeriesItems: list,
        chunkSize: int = 5000,
        pause: int = 1
    ) -> list:
        raise NotImplementedError

    def addTimeSeriesItemsToGroups(
        self,
        inventoryName: str,
        timeSeriesItems: list,
        chunkSize: int = 5000,
        pause: int = 1
    ) -> None:
        raise NotImplementedError

    def updateTimeSeriesItems(
        self,
        inventoryName: str,
        timeSeriesItem: list
    ) -> Optional[list]:
        raise NotImplementedError

    def setTimeSeriesData(
        self,
        inventoryName: str,
        inventoryItemId: str,
        timeUnit: str,
        factor: int,
        unit: str,
        dataPoints: dict,
        chunkSize: int = 10000
    ) -> None:
        raise NotImplementedError

    def setTimeSeriesDataCollection(
        self,
        timeSeriesData: list,
        chunkSize: int = 10000,
        pause: int = 1
    ) -> None:
        raise NotImplementedError

    def timeSeriesData(
        self,
        inventoryName: str,
        fromTimepoint: str,
        toTimepoint: str,
        fields: Optional[list] = None,
        where: Optional[str] = None,
        unit: Optional[str] = None,
        timeUnit: Optional[str] = None,
        factor: int = 1,
        aggregationRule: str = 'AVG',
        timeZone: Optional[str] = None,
        includeMissing: bool = False,
        displayMode: str = 'pivot',
        displayId: bool = True
    ) -> Optional[pd.DataFrame]:
        raise NotImplementedError

    def timeSeriesGroupData(
        self,
        inventoryName: str,
        fromTimepoint: str,
        toTimepoint: str,
        fields: Optional[list] = None,
        instanceFields: Optional[list] = None,
        instancePrefix: str = 'instance.',
        where: Optional[str] = None,
        whereInstance: Optional[str] = None,
        unit: Optional[str] = None,
        timeUnit: Optional[str] = None,
        factor: int = 1,
        aggregationRule: str = 'AVG',
        timeZone: Optional[str] = None,
        includeMissing: bool = False,
        displayMode: str = 'pivot'
    ) -> Optional[pd.DataFrame]:
        raise NotImplementedError

    def timeSeriesGroupDataReduced(
        self,
        inventoryName: str,
        fromTimepoint: str,
        toTimepoint: str,
        reduceFunction: str = 'LAST',
        fields: Optional[list] = None,
        where: Optional[str] = None,
        whereInstance: Optional[str] = None,
        unit: Optional[str] = None,
        timeUnit: Optional[str] = None,
        factor: int = 1,
        timeZone: Optional[str] = None,
        includeMissing: bool = False,
        displayMode: str = 'pivot'
    ) -> Optional[pd.DataFrame]:
        raise NotImplementedError

    def deleteItems(
        self,
        inventoryName: str,
        inventoryItemIds: Optional[list] = None,
        where: Optional[str] = None,
        force: bool = False,
        pageSize: int = 500
    ) -> None:
        raise NotImplementedError

    def deleteTimeSeriesData(
        self,
        inventoryName: str,
        fromTimepoint: str,
        toTimepoint: str,
        inventoryItemIds: Optional[list] = None,
        where: Optional[str] = None,
        timeZone: Optional[str] = None,
        force: bool = False
    ) -> None:
        raise NotImplementedError

    def items(
        self,
        inventoryName: str,
        references: bool = False,
        fields: Union[list, str, None] = None,
        where: Union[list, tuple, str, None] = None,
        orderBy: Union[dict, list, str, None] = None,
        asc: Union[list, str, bool] = True,
        pageSize: int = 5000,
        arrayPageSize: int = 100000,
        top: int = 100000,
        validityDate: Optional[str] = None,
        allValidityPeriods: bool = False,
        includeSysProperties: bool = False
    ) -> Optional[pd.DataFrame]:
        raise NotImplementedError

    def units(self) -> Optional[pd.DataFrame]:
        raise NotImplementedError

    def createUnit(self, unit: str, baseUnit: str, factor: int, aggregation: str) -> None:
        raise NotImplementedError

    def createBaseUnit(self, baseUnit: str, aggregation: str) -> None:
        raise NotImplementedError

    def updateUnit(self, unit: str, baseUnit: Optional[str] = None, factor: Optional[int] = None, aggregation: Optional[str] = None) -> None:
        raise NotImplementedError

    def deleteUnit(self, unit: str, force: bool = False) -> None:
        raise NotImplementedError

    def refreshSchema(self) -> None:
        raise NotImplementedError
