from uuid import uuid4
import pandas as pd
from typing import Optional, Union
from loguru import logger
from time import sleep
from time import time

from .utils.ut_timeseries import UtilsTimeSeries
from .utils.ut_time import TimeUtils
from .utils.ut_graphql import GraphQLUtil
from .utils.ut_error_handler import ErrorHandler
from .utils.ut_property import PropertyUtil
from .utils.ut_order import OrderUtil
from .core_interface import ITechStack
from .dynamicobjects import IDynamicObjects
from .timeseries_interface import ITimeSeries

class TimeSeries(ITimeSeries):

    def __init__(
        self,
        endpoint: str,
        techStack: ITechStack,
        dynamicObjects: IDynamicObjects
    ) -> None:
        
        self.endpoint = endpoint
        self.techStack = techStack
        self.dynamicObjects = dynamicObjects
        return

    def getVersion(self):
        """
        Returns name and version of the responsible micro service
        """

        return GraphQLUtil.get_service_version(self.techStack, self.endpoint, 'timeSeries')

    def __addTimeSeriesItems(
        self,
        inventoryName: str,
        timeSeriesItems: list
    ) -> Optional[list]:
        """
        Adds new time series and time series group items from a list of 
        dictionaires and returns a list of the created inventoryItemIds.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This list contains the properties of the time series item and the properties
            of the time series feature (unit, timeUnit and factor)

        Example:
        >>> timeSeriesItems = [
                {
                'meterId': 'XYZ123',
                'orderNr': 300,
                'isRelevant': True,
                'dateTime': '2020-01-01T00:00:56Z',
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                'unit': 'kWh'
                },
                {
                'meterId': 'XYZ123',
                'orderNr': 301,
                'isRelevant': True,
                'dateTime': '2020-01-01T00:00:55Z',
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                'unit': 'kWh',
                },
            ]
        >>> client.TimeSeries.addTimeSeriesItems('meterData', timeSeriesItems)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            properties = PropertyUtil.ts_properties_to_string(timeSeriesItems)
            if properties == None:
                return

            key = f'create{inventoryName}'
            graphQLString = f'''mutation addTimeSeriesItems {{
                {key} (input: 
                    {properties}
                )
                {{
                    inventoryItems {{
                        sys_inventoryItemId
                    }}
                    {GraphQLUtil.errors}
                }}
            }} 
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                return
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)

            ids = result[key]['inventoryItems']
            idList = [item['sys_inventoryItemId'] for item in ids]
            logger.info(f"Created {len(idList)} time series items.")

            return idList

    def addTimeSeriesItems(
        self,
        inventoryName: str,
        timeSeriesItems: list,
        chunkSize:int = 5000, 
        pause:int = 1
    ) -> list:
        """
        Adds new time series and time series group items from a list of 
        dictionaires and returns a list of the created inventoryItemIds.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This list contains the properties of the time series item and the properties
            of the time series feature (unit, timeUnit and factor)
        chunkSize : int = 5000
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading. Default is 5000 items per chunk.
        pause : int = 1
            Pause in seconds between each chunk upload to avoid overloading.

        Example:
        >>> timeSeriesItems = [
                {
                'meterId': 'XYZ123',
                'orderNr': 300,
                'isRelevant': True,
                'dateTime': '2020-01-01T00:00:56Z',
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                'unit': 'kWh'
                },
                {
                'meterId': 'XYZ123',
                'orderNr': 301,
                'isRelevant': True,
                'dateTime': '2020-01-01T00:00:55Z',
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                'unit': 'kWh',
                },
            ]
        >>> client.TimeSeries.addTimeSeriesItems('meterData', timeSeriesItems)
        """

        correlationId = str(uuid4())
        result = []
        with logger.contextualize(correlation_id=correlationId):
            if len(timeSeriesItems) > chunkSize:
                lenResult = 0
                for i in range(0, len(timeSeriesItems), chunkSize):
                    result_object = self.__addTimeSeriesItems(inventoryName, timeSeriesItems[i : i + chunkSize])
                    if result_object != None:
                        result.extend(result_object)
                        lenResult = len(result)
                    logger.info(f"{lenResult} items of {len(timeSeriesItems)} imported. Waiting {pause} second(s) before continuing...")
                    sleep(pause)
            else:
                tsResult = self.__addTimeSeriesItems(inventoryName, timeSeriesItems)
                if (tsResult == None):
                    logger.info(f"No items {len(timeSeriesItems)} added.")
                else:
                    logger.info(f"{len(result)} items of {len(timeSeriesItems)} added.")
                    result.extend(tsResult)
        
        return result

    def __addTimeSeriesItemsToGroups(
            self,
            inventoryName: str,
            timeSeriesItems: list
    ):
        """
        Adds new time series items to existing time series groups.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This list contains the properties of the time series items together 
            with the sys_inventoryItemId of the related group time series.

        Example:
        --------
        >>> items = [
                {
                    'issueDate':'2020-11-01T00:00+0200',
                    'name': 'forecast_wind_pro_de',
                    'sys_groupInventoryItemId': 'Sdin6tNl8S'
                }
            ]
        >>> client.TimeSeries.addTimeSeriesItemsToGroups('GroupInventory', instanceItems)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            properties = PropertyUtil.properties_to_string(timeSeriesItems)
            if properties == None:
                return

            key = f'addTimeSeriesTo{inventoryName}'

            graphQLString = f'''mutation addTimeSeriesItemstoGroup {{
            {key} (input: 
                    {properties}
                )
                {{
                    inventoryItems {{
                        sys_inventoryItemId
                    }}
                    {GraphQLUtil.errors}
                }}
            }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                return
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)

            try:
                ids = result[key]['inventoryItems']
                idList = [item['sys_inventoryItemId'] for item in ids]
                logger.info(f"Group instance(s) created.")
                return idList
            except:
                pass
                return

    def addTimeSeriesItemsToGroups(
        self,
        inventoryName: str,
        timeSeriesItems: list,
        chunkSize:int = 5000, 
        pause:int = 1
    ):
        """
        Adds new time series items to existing time series groups.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This list contains the properties of the time series items together 
            with the sys_inventoryItemId of the related group time series.
        chunkSize : int = 5000
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading. Default is 5000 items per chunk.
        pause : int = 1
            Pause in seconds between each chunk upload to avoid overloading.

        Example:
        --------
        >>> items = [
                {
                    'issueDate':'2020-11-01T00:00+0200',
                    'name': 'forecast_wind_pro_de',
                    'sys_groupInventoryItemId': 'Sdin6tNl8S'
                }
            ]
        >>> client.TimeSeries.addTimeSeriesItemsToGroups('GroupInventory', instanceItems)
        """

        correlationId = str(uuid4())
        result = []
        with logger.contextualize(correlation_id=correlationId):
            if len(timeSeriesItems) > chunkSize:
                lenResult = 0
                for i in range(0, len(timeSeriesItems), chunkSize):
                    result_object = self.__addTimeSeriesItemsToGroups(inventoryName, timeSeriesItems[i : i + chunkSize])
                    if result_object != None:
                        result.extend(result_object)
                        lenResult = len(result)
                    logger.info(f"{lenResult} items of {len(timeSeriesItems)} imported. Waiting {pause} second(s) before continuing...")
                    sleep(pause)
            else:
                result = self.__addTimeSeriesItemsToGroups(inventoryName, timeSeriesItems)
                if (result == None):
                    logger.info(f"No items {len(timeSeriesItems)} added.")
                else:
                    logger.info(f"{len(result)} items of {len(timeSeriesItems)} added.") 
        

    def updateTimeSeriesItems(
            self,
            inventoryName: str,
            timeSeriesItem: list
    ) -> Optional[list]:
        """
        Updates existing time series and time series group items from a list of 
        dictionaires and returns a list of the updated inventoryItemIds.
        This can be used to change the resolution of a time series item.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This contains the properties of the time series item and the properties
            of the time series feature (unit, timeUnit and factor)
            It also needs to include the sys_inventoryItemId of the item which should be changed

        Example:
        >>> timeSeriesItem = [
                {
                'sys_inventoryItemId': 'di2WRpTAjA'
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                },
            ]

        >>> client.TimeSeries.updateTimeSeriesItems('meterData', timeSeriesItems)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            properties = PropertyUtil.ts_properties_to_string(timeSeriesItem)
            if properties == None:
                return

            key = f'update{inventoryName}'
            graphQLString = f'''mutation updateTimeSeriesItems {{
                {key} (input: 
                    {properties}
                )
                {{
                    inventoryItems {{
                        sys_inventoryItemId
                    }}
                    {GraphQLUtil.errors}
                }}
            }} 
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                return
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)

            ids = result[key]['inventoryItems']
            idList = [item['sys_inventoryItemId'] for item in ids]
            logger.info(f"Updated {len(idList)} time series items.")

            return idList

    def setTimeSeriesData(
            self,
            inventoryName: str,
            inventoryItemId: str,
            timeUnit: str, factor: int,
            unit: str,
            dataPoints: dict,
            chunkSize: int = 10000
    ) -> None:
        """
        Sets new time series data (timestamp & value) to an existing time series or 
        overwrites existing values. The sys_inventoryItemId of the time series is used. As 
        timestamp format you can use UTC (e.g. 2020-01-01T00:01:00Z) or DateTimeOffset 
        (e.g. 2020-01-01T00:00:00+01:00).

        Parameters
        ---------
        inventoryName: str
            The name of the inventory to which the time series belong.
        inventoryItemId: str
            The inventoryItemId to which data is to be written.
        timeUnit: str
            Is the time unit of the time series item
        factor: int
            Is the factor of the time unit
        unit: str
            The unit of the values to be written. 
        dataPoints: dict
            Provide a dictionary with timestamps as keys.
        chunkSize:int = 10000
            Specifies the chunk size of time series values that are written in 
            a single transaction

        Example: 
        --------
        >>> inventory = 'meterData'
            inventoryItemId = 'TzdG1Gj2GW'
            tsData = {
                '2020-01-01T00:01:00Z': 99.91,
                '2020-01-01T00:02:00Z': 95.93,
            }

        >>> client.TimeSeries.setTimeSeriesData(inventory, inventoryItemId,
                'MINUTE', 1, 'W', tsData)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            inventoryId = self.techStack.metaData.structure[inventoryName]['inventoryId']
            logger.debug(
                f"Found inventoryId {inventoryId} for {inventoryName}.")

            key = f'setTimeSeriesData'

            def _setTimeSeriesData(_dataPoints):

                graphQLString = f'''
                    mutation setTimeSeriesData {{
                    setTimeSeriesData(input: {{
                        sys_inventoryId: "{inventoryId}"
                        sys_inventoryItemId: "{inventoryItemId}",
                        data: {{
                            resolution: {{
                                timeUnit: {timeUnit}
                                factor: {factor}
                                }}
                            unit: "{unit}"
                            dataPoints: [
                                {_dataPoints}
                            ]
                        }}
                    }})
                        {{
                            {GraphQLUtil.errors}
                        }}
                    }}
                '''
                result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                return result

            if len(dataPoints) < chunkSize:
                _dataPoints = UtilsTimeSeries._dataPointsToString(dataPoints)
                result = _setTimeSeriesData(_dataPoints)

                if result == None:
                    return
                elif not isinstance(result, dict):
                    return
                if result[key]['errors']:
                    GraphQLUtil.list_graphQl_errors(result, key)
                else:
                    logger.info(f"{len(dataPoints)} data points set for time series {inventoryItemId}.")
                return

            else:
                dataPointsCount = 0
                for i in range(0, len(dataPoints), chunkSize):
                    #TODO: Check if dicdict(dataPoints.items()) is working
                    dataPointItems = dict(dataPoints.items())
                    sliceDataPoints = UtilsTimeSeries._sliceDataPoints(dataPointItems, i, i + chunkSize)
                    _sliceDataPoints = UtilsTimeSeries._dataPointsToString(
                        sliceDataPoints)
                    result = _setTimeSeriesData(_sliceDataPoints)
                    if result == None:
                        continue
                    elif not isinstance(result, dict):
                        continue
                    if result[key]['errors']:
                        GraphQLUtil.list_graphQl_errors(result, key)

                    dataPointsCount += len(sliceDataPoints)

                logger.info(
                    f"{dataPointsCount} data points set for time series {inventoryItemId}.")

            return

    def __setTimeSeriesDataCollection(
        self,
        timeSeriesData: list
    ) -> Optional[dict]:
        """
        Sets new time series data (timestamp & value) to an existing time series or 
        overwrites existing values. The sys_inventoryId and sys_inventoryItemId of the 
        time series is used. The dictionary represents the GraphQL format.
        As timestamp format you can use UTC (e.g. 2020-01-01T00:01:00Z) or 
        DateTimeOffset (e.g. 2020-01-01T00:00:00+01:00).

        Parameters
        ----------
        data: list
            A list of dictionaries defining inventory, inventoryItemId, resolution, 
            unit and time series values. Is used to write time series values for
            many time series in one single transaction.

        Example: 
        --------
        >>> tsItems = [
                {
                    'sys_inventoryId': 'A6RGwtDbbk', 
                    'sys_inventoryItemId': 'TzdG1Gj2GW', 
                    'data': 
                        {
                            'resolution': {'timeUnit': 'MINUTE', 'factor': 15}, 
                            'unit': 'kW', 
                            'dataPoints': [
                                {
                                    'timestamp': '2021-12-10T07:40:00Z', 
                                    'value': 879.2
                                }
                            ]
                        }
                    },
                ] 
        >>> client.TimeSeries.setTimeSeriesDataCollection(tsItems)
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            try:
                _timeSeriesData = UtilsTimeSeries._tsCollectionToString(
                    timeSeriesData)
            except Exception as err:
                ErrorHandler.error(self.techStack.config.raiseException, f"GraphQL string could not be created out of dictionary. Cause: {err}")
                return

            key = f'setTimeSeriesData'
            graphQLString = f'''
                mutation {key} {{
                {key} (input: {_timeSeriesData})
                    {{
                        {GraphQLUtil.errors}
                    }}
                }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            
            if result == None:
                return
            elif not isinstance(result, dict):
                return
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
            else:
                logger.debug(f"time series data points set.")
            return result
        
    def setTimeSeriesDataCollection(
        self,
        timeSeriesData: list,
        chunkSize: int = 10000,
        pause:int = 1
    ) -> None:
        """
        Sets new time series data (timestamp & value) to an existing time series or 
        overwrites existing values. The sys_inventoryId and sys_inventoryItemId of the 
        time series is used. The dictionary represents the GraphQL format.
        As timestamp format you can use UTC (e.g. 2020-01-01T00:01:00Z) or 
        DateTimeOffset (e.g. 2020-01-01T00:00:00+01:00).

        Parameters
        ----------
        data: list
            A list of dictionaries defining inventory, inventoryItemId, resolution, 
            unit and time series values. Is used to write time series values for
            many time series in one single transaction.
        chunkSize: int = 10000
            Determines the packageSize of time series values that are written in 
            a single transaction

        Example: 
        --------
        >>> tsItems = [
                {
                    'sys_inventoryId': 'A6RGwtDbbk', 
                    'sys_inventoryItemId': 'TzdG1Gj2GW', 
                    'data': 
                        {
                            'resolution': {'timeUnit': 'MINUTE', 'factor': 15}, 
                            'unit': 'kW', 
                            'dataPoints': [
                                {
                                    'timestamp': '2021-12-10T07:40:00Z', 
                                    'value': 879.2
                                }
                            ]
                        }
                    },
                ] 
        >>> client.TimeSeries.setTimeSeriesDataCollection(tsItems)
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            for ts in timeSeriesData:
                items = ts['data']['dataPoints']
                if len(items) > chunkSize:
                    lenItems = len(items)
                    lenResult = 0
                    for i in range(0, lenItems, chunkSize):
                        chunkedTs = ts.copy()
                        chunkedData = items[i : i + chunkSize]
                        chunkedTs['data']['dataPoints'] = chunkedData
                        result_object = self.__setTimeSeriesDataCollection([chunkedTs])
                        if result_object != None:
                            lenResult += len(chunkedData)
                        else:
                            return
                        tsId = ts['sys_inventoryItemId']
                        logger.info(f"{lenResult} datapoints of {lenItems} added to time series '{tsId}'. Waiting {pause} second(s) before continuing...")
                        sleep(pause)
                else:
                    self.__setTimeSeriesDataCollection([ts])
        return
    
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
        """
        Queries time series data and returns its values and properties
        in a DataFrame. Properties without values will be returned as NaN.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        fields: list|str = None
            Properties of the time series to be used as header. Uses inventoryItemId and 
            displayvalue (if available) as default. If fields are not unique for each column, 
            duplicates will be omitted. If you use multiple fields, a MultiIndex DataFrame will be created. 
            To access MultiIndex use syntax like <df[header1][header2]>.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggregation, e.g. 15 for a 15 MINUTE interval.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        includeMissing: bool = False
            If True, timestamps without values will be loaded and lead to a larger DataFrame.
        displayMode: str = pivot
            pivot: pivot display of columns and timestamps, columns without values are dropped
            rows: row display
        displayId: bool = True
            Use False to remove default field inventoryItemId from fields list before applying 
            data frame pivot operations. The field will not be removed if it is the only field.

        Examples:
        ---------
        >>> timeSeriesData('meterData', '2020-10-01', '2020-10-01T:05:30:00Z')
        >>> timeSeriesData('meterData', fromTimepoint='2020-06-01',
                toTimepoint='2020-06-15', fields=['meterId', 'phase']
                where='measure eq "voltage"')
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if timeZone == None:
                timeZone = self.techStack.config.defaults.timeZone
            logger.debug(f"Timezone: {timeZone}")

            _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, timeZone)
            _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, timeZone)

            # where
            handleWhereResult = GraphQLUtil.handle_where_dyno(self.techStack, self.dynamicObjects, where, inventoryName)
            if handleWhereResult == None:
                raise Exception("Could not handle where.")
            topLevelWhere, resolvedFilterDict = handleWhereResult

            # fields
            if fields != None:
                propertyDict = PropertyUtil.properties(self.techStack.metaData.scheme, inventoryName, recursive=True, sys_properties=False)
                if type(fields) != list:
                    fields = [fields]
                if 'sys_inventoryItemId' not in fields:
                    fields += ['sys_inventoryItemId']
                _fields = GraphQLUtil.query_fields(fields, propertyDict['arrayTypeFields'], 50,
                                             filter=resolvedFilterDict, recursive=True)
                if 'pageSize' in _fields:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Array type fields are not supported in 'fields'-argument ({_fields})")
                    return
            else:
                if self.techStack.metaData.structure[inventoryName]['displayValue'] != None:
                    fields = ['sys_displayValue', 'sys_inventoryItemId']
                else:
                    fields = ['sys_inventoryItemId']

                _fields = ''
                for field in fields:
                    _fields += field + '\n'

            unit = GraphQLUtil.arg_none('unit', unit)

            if timeUnit != None:
                aggregation = f'''
                    aggregation: {aggregationRule}
                    resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                    '''
            else:
                aggregation = ''

            if includeMissing == True:
                allowedFlags = f'allowedFlags: [MISSING, VALID, NO_VALUE, INTERPOLATED, ESTIMATED, ACCOUNTED, MANUALLY_REPLACED, SCHEDULE, FAULTY]'
            else:
                allowedFlags = f'allowedFlags: [VALID, INTERPOLATED, ESTIMATED, ACCOUNTED, MANUALLY_REPLACED, SCHEDULE, FAULTY]'

            result = []
            count = 0
            countDp = 0
            lastId = ''
            pageSize = 1  # Initial page size
            maxTimePoints = 40000

            key = inventoryName
            while True:
                start = time()
                graphQLString = f'''query timeSeriesData {{
                    {key} (
                    pageSize: {pageSize}
                    {topLevelWhere}
                    {lastId}
                    )
                    {{
                        {_fields}
                        _dataPoints (input:{{
                            from:"{_fromTimepoint}"
                            to:"{_toTimepoint}"
                            {unit}                        
                            {aggregation}
                            {allowedFlags}
                            }})
                        {{
                            timestamp
                            value
                            flag
                        }}
                    }}
                }}'''

                if count == 0:
                    GraphQLUtil.copyGraphQLString(graphQLString)

                _result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
                if _result == None:
                    ErrorHandler.error(self.techStack.config.raiseException, f"GrapQL query resulted in null value")
                    return
                elif not isinstance(_result, dict):
                    ErrorHandler.error(self.techStack.config.raiseException, f"Returned value is not a dictionary")
                    return

                # Automatic paging
                countDp = 0
                countTs = len(_result[key])
                if countTs == 0:
                    break
                for i in _result[key]:
                    if i['_dataPoints'] == None:
                        continue
                    else:
                        countDp += len(i['_dataPoints'])
                end = round(time()-start, 2)
                logger.debug(
                    f"Iteration: {count}, timeSeries: {countTs}, dataPoints: {countDp}, pageSize: {pageSize}, time: {end}")
                try:
                    pageSize = maxTimePoints * pageSize // countDp
                    if pageSize > 2000:
                        pageSize = 2000
                except ZeroDivisionError:
                    pageSize = 10**(count + 1)
                    if pageSize > 2000:
                        pageSize = 2000
                pageSize = 1 if pageSize == 0 else pageSize

                if _result[inventoryName]:
                    result += _result[inventoryName]
                    count += 1
                try:
                    cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                    lastId = f'lastId: "{cursor}"'
                except Exception as err:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Problem with pagination: {err}")
                    return

            if displayId == False and 'sys_inventoryItemId' in fields and len(fields) > 1:
                fields.remove('sys_inventoryItemId')

            meta = []
            for field in fields:
                if field.count('.') > 0:
                    compoundField = field.split('.')
                    meta.append(compoundField)
                else:
                    meta.append(field)

            df = pd.json_normalize(result, record_path=['_dataPoints'], meta=meta, errors='ignore')
            
            if df.empty:
                logger.info('The query did not produce results.')
                return df

            df = UtilsTimeSeries._processDataFrame(self.techStack, result, df, fields, timeZone, displayMode, includeMissing)
            return df

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
        """
        Queries time series data from time series groups and returns its values and properties 
        for each time series instance in a DataFrame.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        fields: list|str = None
            Properties of the time series group to be used as header. Uses the displayValue 
            (inventoryItemId) as default. If fields are not unique for each column, duplicates 
            will be omitted. If you use multiple fields, a MultiIndex DataFrame will be 
            created. To access MultiIndex use syntax like <df[header1][header2]>.
        instanceFields: list|str = None
            Properties of the time series instance to be used as header. Uses the displayValue 
            (inventoryItemId) as default. 
        instancePrefix: str = 'instance'
            Changes the prefix for all time series instance properties.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        whereInstance: str = None
            Use a string to add where criteria for time series instances.
        unit: str = None
            Use a string to convert time series values into another unit.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggrergation, e.g. 15 for a 15 MINUTE interval.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.

        Examples:
        ---------
        >>> timeSeriesDataGroup('foreCastGroups', '2022-10-01', '2022-10-12')
        >>> timeSeriesDataGroup(
                inventoryName='foreCastGroups', 
                fromTimepoint='2022-10-01',
                toTimepoint='2022-10-12',
                fields=['region', 'measure'],
                instanceFields='issueDate',
                instancePrefix='',
                where='region in ["DE", "FR", "PL"],
                whereInstance='issueDate >= '2022-10-01',
                timeUnit:'DAY'
                )
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if timeZone == None:
                timeZone = self.techStack.config.defaults.timeZone
            logger.debug(f"Timezone: {timeZone}")

            _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, timeZone)
            _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, timeZone)

            deleteIdAfterwards = False
            # where
            handleWhereResult = GraphQLUtil.handle_where_dyno(self.techStack, self.dynamicObjects, where, inventoryName)
            if handleWhereResult == None:
                raise Exception("Could not handle where.")
            topLevelWhere, resolvedFilterDict = handleWhereResult
            
            # fields
            propertyDict= dict()
            if fields != None:
                propertyDict = PropertyUtil.properties(self.techStack.metaData.scheme, inventoryName, recursive=True, sys_properties=False)
                if type(fields) != list:
                    fields = [fields]
                if 'sys_inventoryItemId' not in fields:
                    fields += ['sys_inventoryItemId']
                    deleteIdAfterwards = True
                _fields = GraphQLUtil.query_fields(fields, propertyDict['arrayTypeFields'], 200,
                                             filter=resolvedFilterDict, recursive=True)
                if 'pageSize' in _fields:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Array type fields are not supported in 'fields'-argument ({_fields})")
                    return
                _groupFields = _fields
            else:
                if self.techStack.metaData.structure[inventoryName]['displayValue'] != None and self.techStack.metaData.structure[inventoryName]['displayValue'] != '':
                    fields = ['sys_displayValue', 'sys_inventoryItemId']
                    deleteIdAfterwards = True
                else:
                    fields = ['sys_inventoryItemId']

                _groupFields = ''
                for field in fields:
                    _groupFields += field + '\n' 

            instanceInventoryName = self.techStack.metaData.structure[inventoryName]['properties']['timeSeriesInstances']['inventoryName']
            handleWhereResult = GraphQLUtil.handle_where_dyno(self.techStack, self.dynamicObjects, whereInstance, instanceInventoryName)
            if handleWhereResult == None:
                raise Exception("Could not handle where.")
            instanceWhere, resolvedFilterDict = handleWhereResult

            if instanceFields != None:
                if type(instanceFields) != list:
                    instanceFields = [instanceFields]
                if 'sys_inventoryItemId' not in instanceFields:
                    instanceFields += ['sys_inventoryItemId']
                    deleteIdAfterwards = True
                _fields = GraphQLUtil.query_fields(instanceFields, propertyDict['arrayTypeFields'], 200, filter=resolvedFilterDict, recursive=True)
                if 'pageSize' in _fields:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Array type fields are not supported in 'fields'-argument ({_fields})")
                    return
                _instanceFields = _fields
                print(f'Instance fields {_instanceFields}')                    
            else:
                if self.techStack.metaData.structure[instanceInventoryName]['displayValue'] is not None and self.techStack.metaData.structure[instanceInventoryName]['displayValue'] != '':
                    instanceFields = [
                        'sys_displayValue', 'sys_inventoryItemId']
                else:
                    instanceFields = ['sys_inventoryItemId']

                _instanceFields = ''
                for field in instanceFields:
                    _instanceFields += field + '\n'

            unit = GraphQLUtil.arg_none('unit', unit)

            if timeUnit != None:
                aggregation = f'''
                    aggregation: {aggregationRule}
                    resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                    '''
            else:
                aggregation = ''

            if includeMissing == True:
                allowedFlags = f'allowedFlags: [MISSING, VALID, NO_VALUE, INTERPOLATED, ESTIMATED, ACCOUNTED, MANUALLY_REPLACED, SCHEDULE, FAULTY]'
            else:
                allowedFlags = f'allowedFlags: [VALID, INTERPOLATED, ESTIMATED, ACCOUNTED, MANUALLY_REPLACED, SCHEDULE, FAULTY]'

            instanceDataPoints = f'''_dataPoints (input:{{
                            from:"{_fromTimepoint}"
                            to:"{_toTimepoint}"
                            {unit}
                            {aggregation}
                            {allowedFlags}
                            }})
                        {{
                            timestamp
                            value
                            flag
                        }}
            '''

            key = inventoryName

            result = []
            count = 0
            countDp = 0
            lastId = ''
            pageSize = 1  # Initial page size
            maxTimePoints = 40000

            while True:

                start = time()
                graphQLString = f'''query timeSeriesData {{
                    {key} (
                    pageSize: {pageSize}
                    {topLevelWhere}
                    {lastId}
                    )
                    {{
                        {_groupFields}
                        timeSeriesInstances (
                        pageSize: 5000
                        {instanceWhere}
                        ) {{
                            {_instanceFields}
                            {instanceDataPoints}
                        }}
                    }}
                }}'''

                if count == 0:
                    GraphQLUtil.copyGraphQLString(graphQLString, True)

                _result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
                if _result == None:
                    ErrorHandler.error(self.techStack.config.raiseException, f"GrapQL query resulted in null value")
                    return
                elif not isinstance(_result, dict):
                    ErrorHandler.error(self.techStack.config.raiseException, f"Returned value is not a dictionary")
                    return
                
                try:
                    countDp = 0
                    countInst = 0
                    countGroupTs = len(_result[key])
                    if countGroupTs == 0:
                        break
                    for i in _result[key]:
                        countInst += len(i['timeSeriesInstances'])
                        for j in i['timeSeriesInstances']:
                            if j["_dataPoints"] != None:
                                countDp += len(j['_dataPoints'])
                    end = round(time()-start, 2)
                    logger.debug(
                        f"Iteration: {count}, groupTimeSeries: {countGroupTs}, instances: {countInst}, dataPoints: {countDp}, pageSize: {pageSize}, time: {end}")
                    try:
                        pageSize = maxTimePoints * pageSize // countDp
                        if pageSize > 10000:
                            pageSize = 10000
                    except ZeroDivisionError:
                        pageSize = 10**(count + 1)
                        if pageSize > 10000:
                            pageSize = 10000
                    pageSize = 1 if pageSize == 0 else pageSize
                except Exception as err:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Problem with pagination: {err}")
                    return

                if _result[inventoryName]:
                    result += _result[inventoryName]
                    count += 1
                try:
                    cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                    lastId = f'lastId: "{cursor}"'
                except Exception as err:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Problem with pagination: {err}")
                    return

            if deleteIdAfterwards == True:
                fields.remove('sys_inventoryItemId')

            metaInstances = []
            if type(instanceFields) != list:
                metaInstances.append(['timeSeriesInstances', instanceFields])
            else:
                for field in instanceFields:
                    if field.count('.') == 1:
                        compoundField = field.split('.')
                        metaInstances.append(['timeSeriesInstances', compoundField[0], compoundField[1]])
                    else:                        
                        metaInstances.append(['timeSeriesInstances', field])
            metaInstances.append('sys_inventoryItemId')

            try:
                dfGroupMeta = pd.json_normalize(result, sep='.', errors='ignore')
                dfInstancesTS = pd.json_normalize(result, record_path=['timeSeriesInstances', '_dataPoints'],
                                       meta=metaInstances, errors='ignore')
                dfGroupMeta.drop(columns=['timeSeriesInstances'], inplace = True)
                df = pd.merge(dfGroupMeta, dfInstancesTS, on='sys_inventoryItemId', how='inner')
            except KeyError as err:
                ErrorHandler.error(self.techStack.config.raiseException, f"There is a problem with the provided fields. Probably one or more fields have no values. Exception: {err}")
                return

            # rename columns
            reColumns = []
            for col in df.columns:
                if col.startswith('timeSeriesInstances'):
                    col = col.replace('timeSeriesInstances.', instancePrefix)
                reColumns.append(col)
            df.columns = reColumns

            if "sys_inventoryItemId" not in fields:
                fields.insert(0, "sys_inventoryItemId")
            else:
                fields.remove("sys_inventoryItemId")
                fields.insert(0, "sys_inventoryItemId")

            if "sys_inventoryItemId" not in instanceFields:
                instanceFields.insert(0, "sys_inventoryItemId")
            else:
                instanceFields.remove("sys_inventoryItemId")
                instanceFields.insert(0, "sys_inventoryItemId")
            instanceFields = [f"{instancePrefix}{item}" for item in instanceFields]
 
            pivotColumns = fields + instanceFields
            df = UtilsTimeSeries._processDataFrame(self.techStack, result, df, pivotColumns, timeZone, displayMode, includeMissing)
            return df

    def timeSeriesGroupDataReduced(
            self,
            inventoryName: str,
            fromTimepoint: str,
            toTimepoint: str,
            reduceFunction: str = 'LAST',
            fields: Optional[list] = None ,
            where: Optional[str] = None,
            whereInstance: Optional[str] = None,
            unit: Optional[str] = None,
            timeUnit: Optional[str] = None,
            factor: int = 1,
            timeZone: Optional[str] = None,
            includeMissing: bool = False,
            displayMode: str = 'pivot'
    ) -> Optional[pd.DataFrame]:
        """
        Queries time series group data, reduces time series instances to a single array
        for each time series group and returns its values and properties 
        in a DataFrame.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        reduceFunction: str = 'LAST'
            The function that determines how values from multiple time series instances should be reduced 
            to a single array.
        fields: list|str = None
            Properties of the time series group to be used as header. Uses the displayValue as default. 
            If fields are not unique for each column, duplicates will be omitted. If you use 
            multiple fields, a MultiIndex DataFrame will be created. Use inventoryProperties() 
            to find out which properties are available for an inventory. 
            To access MultiIndex use syntax like <df[header1][header2]>.
        instancePrefix: str = 'instance'
            Changes the prefix for all time series instance properties.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        whereInstance: str = None
            Use a string to add where criteria for time series instances.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggrergation, e.g. 15 for a 15 MINUTE interval.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        displayMode: str = pivot
            pivot: pivot display of columns and timestamps, columns without values are dropped
            rows: row display

        Examples:
        ---------
        >>> timeSeriesDataGroup('foreCastGroups', '2022-10-01', '2022-10-12')
        >>> timeSeriesDataGroup(
                inventoryName='foreCastGroups', 
                fromTimepoint='2022-10-01',
                toTimepoint='2022-10-12',
                fields=['region', 'measure'],
                instancePrefix='',
                where='region in ["DE", "FR", "PL"],
                whereInstance='issueDate >= '2022-10-01',
                timeUnit:'DAY'
                )
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if timeZone == None:
                timeZone = self.techStack.config.defaults.timeZone
            logger.debug(f"Timezone: {timeZone}")

            _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, timeZone)
            _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, timeZone)

            deleteIdAfterwards = False
            # where
            handleWhereResult = GraphQLUtil.handle_where_dyno(self.techStack, self.dynamicObjects, where, inventoryName)
            if handleWhereResult == None:
                raise Exception("Could not handle where.")
            topLevelWhere, resolvedFilterDict = handleWhereResult

            # fields
            if fields != None:
                propertyDict = PropertyUtil.properties(self.techStack.metaData.scheme, inventoryName, recursive=True,
                                                 sys_properties=False)
                if type(fields) != list:
                    fields = [fields]
                if 'sys_inventoryItemId' not in fields:
                    fields += ['sys_inventoryItemId']
                    deleteIdAfterwards = True
                _fields = GraphQLUtil.query_fields(fields, propertyDict['arrayTypeFields'], 200,
                                             filter=resolvedFilterDict, recursive=True)
                if 'pageSize' in _fields:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Array type fields are not supported in 'fields'-argument ({_fields})")
                    return
                _groupFields = _fields
            else:
                if self.techStack.metaData.structure[inventoryName]['displayValue'] != None and self.techStack.metaData.structure[inventoryName]['displayValue'] != '':
                    fields = ['sys_displayValue', 'sys_inventoryItemId']
                    deleteIdAfterwards = True
                else:
                    fields = ['sys_inventoryItemId']

                _groupFields = ''
                for field in fields:
                    _groupFields += field + '\n' 

            resolvedInstanceFilter = ''
            if whereInstance != None:
                handleWhereResult = GraphQLUtil.handle_where_dyno(self.techStack, self.dynamicObjects, whereInstance)
                if handleWhereResult == None:
                    raise Exception("Could not handle where.")
                resolvedInstanceFilter, _ = handleWhereResult

            unit = GraphQLUtil.arg_none('unit', unit)

            if timeUnit != None:
                aggregation = f'''
                    resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                    '''
            else:
                aggregation = ''

            if resolvedInstanceFilter == '':
                instanceInput = ''
            else:
                instanceInput = f'''({resolvedInstanceFilter})'''

            groupInput = f'''input:{{
                            from:"{_fromTimepoint}"
                            to:"{_toTimepoint}"
                            {unit}
                            {aggregation}
                            reducer: {reduceFunction}
                            showMissing: true
                            }}
            '''
            print(f'Top level filter is {topLevelWhere}')
            key = inventoryName
            graphQLString = f'''query timeSeriesData {{
                    {key} (
                    pageSize: 5000 
                    {topLevelWhere}
                    {groupInput}
                    )
                    {{
                        {_groupFields}
                        _dataPoints {{
                            timestamp
                            value
                            flag
                            }}
                        timeSeriesInstances {instanceInput} {{
                            sys_inventoryItemId
                        }}
                    }}
                }}'''

            result = []
            count = 0
            countDp = 0
            lastId = ''
            pageSize = 1  # Initial page size
            maxTimePoints = 40000

            while True:

                start = time()
                graphQLString = f'''query timeSeriesData {{
                    {key} (
                    pageSize: {pageSize}
                    {topLevelWhere}
                    {lastId}
                    {groupInput}
                    )
                    {{
                        {_groupFields}
                        _dataPoints {{
                            timestamp
                            value
                            flag
                            }}
                        timeSeriesInstances {instanceInput} {{
                            sys_inventoryItemId
                        }}
                    }}
                }}'''

                if count == 0:
                    GraphQLUtil.copyGraphQLString(graphQLString)

                _result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
                if (_result == None):
                    ErrorHandler.error(self.techStack.config.raiseException, f"GrapQL query resulted in null value")
                    raise ValueError('No result returned.')
                elif not isinstance(_result, dict):
                    ErrorHandler.error(self.techStack.config.raiseException, f"Returned value is not a dictionary")
                    raise ValueError('No result returned.')

                # Automatic paging
                countDp = 0
                countTs = len(_result[key])
                if countTs == 0:
                    break
                for i in _result[key]:
                    countDp += len(i['_dataPoints'])
                end = round(time()-start, 2)
                logger.debug(
                    f"Iteration: {count}, groupTimeSeries: {countTs}, dataPoints: {countDp}, pageSize: {pageSize}, time: {end}")
                try:
                    pageSize = maxTimePoints * pageSize // countDp
                except ZeroDivisionError:
                    pageSize = 10**(count + 1)
                    if count == 5:
                        count = 1  # To prevent too large pageSize
                pageSize = 1 if pageSize == 0 else pageSize

                if _result[inventoryName]:
                    result += _result[inventoryName]
                    count += 1
                try:
                    cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                    lastId = f'lastId: "{cursor}"'
                except Exception as err:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Problem with pagination: {err}")
                    return

            meta = []
            for field in fields:
                if field.count('.') == 1:
                    compoundField = field.split('.')
                    meta.append([compoundField[0], compoundField[1]])
                else:
                    meta.append(field)            
            try:    
                print(f'field are {fields}')
                df = pd.json_normalize(result, ['_dataPoints'],  meta=meta)
            except KeyError:
                ErrorHandler.error(self.techStack.config.raiseException, f"There is a problem with the provided fields. Probably one or more fields have no values. ")
                return

            pivotColumns = list(df.columns)[3:]

            df = UtilsTimeSeries._processDataFrame(self.techStack, result, df, pivotColumns, timeZone, displayMode, includeMissing)
            return df

    def deleteItems(
        self,
        inventoryName: str,
        inventoryItemIds: Optional[list] = None,
        where: Optional[str] = None,
        force: bool = False,
        pageSize: int = 500
    ) -> None:
        """
        Deletes inventory (variant: TimeSeries) items from a list of inventoryItemIds or by where-criteria. 

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory of variant 'TimeSeries'.
        inventoryItemIds: list = None
            A list of inventoryItemIds that should be deleted.
        where: str = None
            Filter criteria to select items that should be deleted.
        force: bool = False
            Use True to ignore confirmation.
        pageSize: int = 500
            Only a limited amount of items can be deleted at once. 500 is default, however, 
            if this size is too, big, choose a lower pageSize.

        Examples:
        ---------
        >>> deleteItems('meterData', where='changeDate gt "2020-12-01"', force=True, pageSize=100)
        >>> deleteItems('meterData', inventoryItemIds=['El5JrMG2xk'])
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            inventory = self.dynamicObjects.inventories(where=f'name eq "{inventoryName}"', fields=['variant.name'])
            if (inventory is None or inventory.empty):
                raise Exception('No result returned.')
            if inventory.empty:
                ErrorHandler.error(self.techStack.config.raiseException, f"Unknown inventory '{inventoryName}'.")
                return
            if not self.dynamicObjects._isInventoryOfValidVariant(inventoryName, 'TimeSeries'):
                ErrorHandler.error(self.techStack.config.raiseException, f"Items of a non TimeSeries inventory cannot be deleted.")
                return
            # copy from core.deleteItems()
            def delete(ids, n, m):

                _ids = '['
                for id in ids[n:m]:
                    _ids += f'''{{sys_inventoryItemId: "{id}"}}\n'''
                _ids += ']'

                key = f'delete{inventoryName}'
                graphQLString = f'''
                    mutation deleteItems {{
                        {key} ( input: 
                            {_ids}
                        )
                        {{
                            {GraphQLUtil.errors}           
                        }}
                    }}
                    '''
                
                result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                if result == None:
                    logger.error('No result returned.')
                    return
                elif not isinstance(result, dict):
                    logger.error('Invalid result returned.')
                    return
                if result[key]['errors'] != None:
                    logger.error(GraphQLUtil.list_graphQl_errors(result, key))
                    return

            if inventoryItemIds == None and where == None:
                ErrorHandler.error(self.techStack.config.raiseException, f"No list of items and no where-criteria were provided.")
                return

            if inventoryItemIds != None and where != None:
                logger.warning(
                    f"List of items and where-criteria has been provided. Item list is used.")
            ids = list()
            if where != None:
                _result = self.items(inventoryName, fields=['sys_inventoryItemId'], where=where)
                if (_result is None or _result.empty):
                    raise Exception('No result returned.')
                
                if _result.empty:
                    logger.info(f"No results found for provided filter.")
                    return
                ids = list(_result['sys_inventoryItemId'])
            if inventoryItemIds != None:
                _result = self.items(inventoryName, fields=[
                                    'sys_inventoryItemId'], where=f'sys_inventoryItemId in {inventoryItemIds}')
                if (_result is None or _result.empty):
                    raise Exception('No result returned.')
                
                if _result.empty:
                    logger.info(f"Provided id(s) could not be found.")
                    return
                ids = list(_result['sys_inventoryItemId'])
                diff = set(inventoryItemIds).difference(set(ids))
                if diff:
                    ErrorHandler.error(self.techStack.config.raiseException, f"The following item id's are not in the inventory: {ids}")
                    return

            logger.debug(f"GraphQL Ids: {ids}")

            if force:
                confirm = 'y'
            else:
                confirm = input(f"Press 'y' to delete  {len(ids)} items: ")
                
            if confirm == 'y':
                n = 0
                m = n + pageSize

                while True:
                    delete(ids, n, m)
                    n += pageSize
                    m += pageSize

                    if len(ids) - m < pageSize:
                        delete(ids, n, len(ids))
                        break
            else:
                return

            logger.info(f"{len(ids)} items deleted.")
            return

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
        """
        Deletes time series data for a specified time range for multiple time series within an inventory.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be deleted. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The end of the time range up until time series values will be deleted.
        inventoryItemIds: list = None
            A list of inventoryItemIds that should be deleted.
        where: str = None
            Filter criteria to select items that should be deleted.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        force: bool = False
            Use True to ignore confirmation.
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            def createDataPoints(fromTimepoint, toTimepoint, timeUnit, factor) -> list:
                unitMapping = {
                    'MILLISECOND': 'ms',
                    'SECOND': 'S',
                    'MINUTE': 'min',
                    'HOUR': 'H',
                    'DAY': 'D',
                    'WEEK': 'W',
                    'MONTH': 'M',
                    'YEAR': 'YS'
                }
                freq = f'{factor}{unitMapping[timeUnit]}'
                index = pd.date_range(fromTimepoint, toTimepoint, freq=freq)
                logger.debug(f"DateTimeIndex: {index}")

                dataPoints = []
                for timepoint in index:
                    data = {
                        'timestamp': timepoint,
                        'value': 0,
                        'flag': 'MISSING'
                    }
                    dataPoints.append(data)

                return dataPoints

            if timeZone != None:
                tz = timeZone
            else:
                tz = self.techStack.config.defaults.timeZone

            fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, tz)
            toTimepoint = TimeUtils._inputTimestamp(toTimepoint, tz)

            inventory = self.dynamicObjects.inventories(where=f'name eq "{inventoryName}"')
            if (inventory is None or inventory.empty):
                raise Exception('No result returned.')
            
            sys_inventoryId = inventory.loc[0, 'inventoryId']

            if inventoryItemIds == None and where == None:
                ErrorHandler.error(self.techStack.config.raiseException, f"No id list of items and no where-criteria were provided.")
                return

            if inventoryItemIds != None and where != None:
                logger.warning(
                    f"List of items and where-criteria has been provided. Item list is used.")
            
            df = None
            if where != None:
                df = self.dynamicObjects.items(inventoryName, fields=['sys_inventoryItemId', 'resolution'], where=where)
                if (df is None or df.empty):
                    raise Exception('No result returned.')
                
                if df.empty:
                    logger.info(
                        f"The where criteria '{where}' led to no results.")
                    return

            if inventoryItemIds != None:
                idList = '['
                for item in inventoryItemIds:
                    idList += f'"{item}", '
                idList += ']'
                df = self.dynamicObjects.items(inventoryName, fields=['sys_inventoryItemId', 'resolution'], where=f'sys_inventoryItemId in {idList}')
            
            if (df is None or df.empty):
                raise Exception('No result returned.')

            if force:
                confirm = 'y'
            else:
                confirm = input(f"Press 'y' to delete values for {len(df)} time series items: ")
            
            if confirm != 'y':
                return

            for ts in df.iterrows():

                sys_inventoryItemId = ts[1]['sys_inventoryItemId']
                ts_resolution = ts[1]['resolution']
                if (ts_resolution == None):
                    ts_resolution = ''
                else:
                    ts_resolution = str(ts_resolution)
                    
                timeUnit = ts_resolution.split(' ')[1]
                factor = ts_resolution.split(' ')[0]
                dataPoints = createDataPoints(
                    fromTimepoint, toTimepoint, timeUnit, factor)
                resolution = {'timeUnit': timeUnit, 'factor': factor}

                timeSeries = [{
                    'sys_inventoryId': sys_inventoryId,
                    'sys_inventoryItemId': sys_inventoryItemId,
                    'data':
                        {
                            'resolution': resolution,
                            'dataPoints': dataPoints
                        }
                }]

                self.setTimeSeriesDataCollection(timeSeries)
            logger.info(f"Deleted values for {len(df)} time series items")

            return

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
        """
        Returns items of an inventory in a DataFrame.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        references: bool = False
            If True, items of referenced inventories will be added to the DataFrame. If
            the fields-parameter is used, this parameter is ignored.
        fields: list | str = None
            A list of all properties to be queried. If None, all properties will be queried.
            For referenced items use a '.' between inventory name and property.
        where: list | tuple | str = None
            Define arguments critera like  'city eq "Berlin" and use lists for AND-combinations and
            tuples for OR-combinations. For references use the format inventory.property as 
            filter criteria.
        orderBy: dict | list | str = None
            Use a dict in the form of {property:'ASC'|'DESC'} or 
            use a list of properties and the asc-argument for sorting direction
        asc: list | bool = True
            Determines the sort order of items. If set to False, a descending order 
            is applied. Use a list, if more properties are selected in orderBy.
        pageSize: int = 5000
            The page size of items that is used to retrieve a large number of items.
        arrayPageSize: int = 100000
            The page size of list items that is used to page list items in an inventory item.
        top: int = None
            Returns a restricted set of items oriented at the latest entries.
        includeSysProperties: bool = False
            If True, all system properties available will be queried. If False, 
            only 'sys_inventoryItemId' will be queried by default. Despite of that, any system 
            property can be passed to the fields argument as well.
        validityDate: str = None
            If the queried inventory has validity periods enabled, only items will be returned, 
            which have the given timestamp between sys_validTo and sys_validFrom. Items without
            validity periods are shown as well.
        allValidityPeriods: bool = False
            If True and if the queried inventory has validity periods enabled, all validity 
            periods will be returned. If False, items with validity dates will not be returned.


        Example:
        --------
        >>> items('appartments', references=True)
        >>> items(
                'appartments',
                fields=['address', 'owner'],
                where=['city == "Berlin"', 'rooms > 2'],
                orderBy={'size':'DESC', price:'ASC'}
                )
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if inventoryName not in self.techStack.metaData.inventory:
                ErrorHandler.error(self.techStack.config.raiseException, f"'{inventoryName}' does not exist.")
                return

            # where
            try:
                handleWhereResult = GraphQLUtil.handle_where_dyno(self.techStack, self.dynamicObjects, where, inventoryName)
                if handleWhereResult == None:
                    raise Exception("Could not handle where.")
                topLevelWhere, resolvedFilterDict = handleWhereResult
            except:
                ErrorHandler.error(self.techStack.config.raiseException, f"where filter '{where}' does not return data.")
                return

            validityDateStr = GraphQLUtil.arg_none('validityDate', validityDate)
            allValidityPeriodsStr = GraphQLUtil.arg_none('allValidityPeriods', allValidityPeriods)

            # core
            deleteId = False
            propertyDict = PropertyUtil.properties(self.techStack.metaData.scheme, inventoryName, recursive=True,
                                             sys_properties=includeSysProperties)
            if fields != None:
                if type(fields) != list:
                    fields = [fields]
                if 'sys_inventoryItemId' not in fields:
                    deleteId = True
                    fields += ['sys_inventoryItemId']
                _fields = GraphQLUtil.query_fields(fields, propertyDict['arrayTypeFields'], arrayPageSize,
                                             filter=resolvedFilterDict, recursive=True)
            else:
                properties = PropertyUtil.property_list(
                    propertyDict['properties'], recursive=references)
                _fields = UtilsTimeSeries._queryFields(properties, propertyDict['arrayTypeFields'],
                                                       arrayPageSize, filter=resolvedFilterDict, recursive=references)
            logger.debug(f"Fields: {_fields}")

            if len(_fields) == 0:
                ErrorHandler.error(self.techStack.config.raiseException, f"Inventory '{inventoryName}' not found.")
                return

            order = OrderUtil.order_items(self.techStack, orderBy, asc)
            if order == None:
                return

            result = []
            count = 0
            stop = False
            lastId = ''

            while True:

                # Handling top (premature stop)
                if top != None:
                    loadedItems = pageSize * count
                    if top - loadedItems <= pageSize:
                        stop = True
                        pageSize = top - loadedItems

                graphQLString = f'''query getItems {{
                        {inventoryName} (
                                pageSize: {pageSize}
                                {order}
                                {allValidityPeriodsStr}
                                {validityDateStr}
                                {lastId}
                                {topLevelWhere}
                                ) {{
                            {_fields}
                        }}
                    }}
                    '''

                _result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)

                if _result == None:
                    break
                elif not isinstance(_result, dict):
                    break

                if _result[inventoryName]:
                    result += _result[inventoryName]
                    count += 1
                try:
                    cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                    lastId = f'lastId: "{cursor}"'
                except:
                    break

                if stop == True:
                    break

            df = pd.json_normalize(result)

            if fields != None:  # sorts dataframe according to given fields
                try:  # for array field this does not work
                    df = pd.DataFrame(df[fields])
                except:
                    pass
            if deleteId:
                try:
                    del df['sys_inventoryItemId']
                except:
                    pass

            return df

    def units(self) -> Optional[pd.DataFrame]:
        """
        Returns a DataFrame of existing units.

        Examples:
        >>> units()
        """

        graphQLString = f'''query getUnits {{
        units
            {{
            name
            baseUnit
            factor
            isBaseUnit
            aggregation
            }}
        }}
        '''

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            if result == None:
                return
            elif not isinstance(result, dict):
                return

            return pd.json_normalize(result['units'])

    def createUnit(self, unit: str, baseUnit: str, factor: int, aggregation: str) -> None:
        """
        Creates a unit on basis of a base unit.

        Parameters:
        ----------
        unit : str
            The name of the unit to be created.
        baseUnit : str
            The name of an existing base unit.
        factor : float
            The factor related to the base unit.
        aggregation : str
            The enum value for default aggregation. Possible are 'SUM' and 'AVG' This 
            kind of aggregation is used for integral units (kW -> kWh), which are not supported 
            yet.

        Example:
        >>> createUnit('kW', 'W', 1000, 'AVG')
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            graphQLString = f'''
                mutation createUnit {{
                    createUnit(input: {{
                        name: "{unit}"
                        baseUnit: "{baseUnit}"
                        factor: {factor}
                        aggregation: {aggregation}}})
                    {{
                        {GraphQLUtil.errors}
                    }}
                }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            if result == None:
                return
            elif not isinstance(result, dict):
                return

            key = f'createUnit'
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
            else:
                logger.info(f"Unit {unit} created.")
            return

    def createBaseUnit(self, baseUnit: str, aggregation: str) -> None:
        """
        Creates a base unit.

        Parameters:
        ----------
        baseUnit : str
            The name of the base unit to be created.
        aggregation : str
            The enum value for default aggregation. Possible are 'SUM' and 'AVG'.

        Example:
        >>> createBaseUnit('W', 'AVG')
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            graphQLString = f'''
                mutation createBaseUnit {{
                    createBaseUnit(input: {{
                        name: "{baseUnit}"
                        aggregation: {aggregation}}})
                    {{
                        {GraphQLUtil.errors}
                    }}
                }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            if result == None:
                return
            elif not isinstance(result, dict):
                return

            key = f'createBaseUnit'
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
            else:
                logger.info(f"Unit {baseUnit} created.")

            return

    def updateUnit(self, unit: str, baseUnit: Optional[str] = None, factor: Optional[int] = None, aggregation: Optional[str] = None) -> None:
        """
        Updates a unit.

        Parameters:
        ----------
        unit : str
            The name of the unit to be updated.
        baseUnit : str
            The name of an existing base unit.
        factor : float
            The factor related to the base unit.
        aggregation : str
            The enum value for default aggregation. Possible enums are 'SUM' and 'AVG' 

        Example:
        >>> updateUnit('kW', 'W', 1000, 'AVG')
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            baseUnitStr = GraphQLUtil.arg_none('baseUnit', baseUnit)
            factorStr = GraphQLUtil.arg_none('factor', factor)
            aggregationStr = GraphQLUtil.arg_none('aggregation', aggregation, enum=True)

            graphQLString = f'''
                mutation updateUnit {{
                    updateUnit(input: {{
                        name: "{unit}"
                        {baseUnitStr}
                        {factorStr}
                        {aggregationStr}
                        }})
                    {{
                        {GraphQLUtil.errors}
                    }}
                }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            if result == None:
                return
            elif not isinstance(result, dict):
                return
            
            key = f'updateUnit'
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
            else:
                logger.info(f"Unit {unit} updated.")
            return

    def deleteUnit(self, unit: str, force=False) -> None:
        """
        Deletes a unit. Units can only be deleted if there are no Time Series that use this unit. 
        Base units can only be deleted, if no derived units exist.

        Parameters:
        ----------
        unit : str
            Name of the unit to be deleted.
        force : bool
            Optional, use True to ignore confirmation.

        Example:
        >>> deleteUnit('kW', force=True)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if force == False:
                confirm = input(f"Press 'y' to delete unit '{unit}'")
            else:
                confirm = 'y'

            graphQLString = f'''
            mutation deleteUnit{{
                deleteUnit (input: {{
                    name: "{unit}"
                    }})
                        {{
                        {GraphQLUtil.errors}
                    }}
                }}
                '''

            if confirm == 'y':
                result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            else:
                return
            
            if result == None:
                return

            logger.info(f"Unit {unit} deleted.")

            return

    def refreshSchema(self):
        """
        Updates the time series graphQL schema.
        """

        logger.info(f"Refreshing schema.")
            
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            graphQLString = f'''
            mutation refreshSchema{{
                refreshSchema
                }}
                '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            if result == None:
                return

            logger.info(f"Refreshed time series schema.")
