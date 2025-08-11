from uuid import uuid4
from loguru import logger
from time import sleep
from typing import Callable, Optional, Union
import pandas as pd

from seven2one.core_interface import ITechStack
from seven2one.dynamicobjects_interface import IDynamicObjects
from .utils.ut_data_frame import DataFrameUtil
from .utils.ut_graphql import GraphQLUtil
from .utils.ut_error_handler import ErrorHandler
from .utils.ut_order import OrderUtil
from .utils.ut_property import PropertyUtil
from datetime import datetime, timedelta

class DynamicObjects(IDynamicObjects):
    def __init__(self, endpoint: str, techStack: ITechStack, dynoSchemaChanged: Callable[..., None], timeseriesSchemaChanged: Callable[..., None]) -> None:
        self.endpoint = endpoint
        self.techStack = techStack
        self.dynoSchemaChanged = dynoSchemaChanged
        self.timeseriesSchemaChanged = timeseriesSchemaChanged

    def inventories(
        self,
        fields: Optional[list] = None,
        where: Optional[str] = None,
        orderBy: Optional[str] = None,
        asc: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Returns a DataFrame of existing inventories.

        Parameters:
        ----------
        fields: list=None
            The list of fields to be queried, e.g.
            ['name', 'inventoryId, variant.name']
        where: str=None
            Use a string to add where criteria like 'name eq "meterData"'.
            The argument is momentarily very limited.
        orderBy: str=None
            Select one field to sort by.
        asc: bool=True
            Determines the sort order of items. Set to False to apply descending order.

        Examples:
        >>> inventories()
        >>> inventories(fields=['name', 'inventoryId'], 
                where='city eq "Hamburg"', 
                orderBy='variant', asc=True)
        """
        
        if fields == None:
            fields = ['name', 'inventoryId', 'variant.name',
                      'historyEnabled', 'hasValidityPeriods', 'isDomainUserType']
            _fields = GraphQLUtil.query_fields(fields, recursive=True)
        else:
            if type(fields) != list:
                fields = [fields]
            try:
                _fields = GraphQLUtil.query_fields(fields, recursive=True)
            except:
                ErrorHandler.error(self.techStack.config.raiseException, "Fields must be provided as list, e.g. ['name', 'inventoryId, variant.name']")
                return

        handleWhereResult = GraphQLUtil.handle_where_dyno(self.techStack, self, where)
        if handleWhereResult == None:
            raise Exception("Could not handle where.")
        topLevelWhere, _ = handleWhereResult

        if orderBy != None:
            if asc != True:
                _orderBy = f'order: {{ {orderBy}: DESC }}'
            else:
                _orderBy = f'order: {{ {orderBy}: ASC }}'
        else:
            _orderBy = ''

        graphQLString = f'''query inventories {{
        inventories 
            (pageSize:1000 {_orderBy} {topLevelWhere})
            {{
            {_fields}
            }}
        }}
        '''
        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return None
        elif not isinstance(result, dict):
            raise Exception("Could not get inventories.")

        df = pd.json_normalize(result['inventories'])
        return df

    def items(
        self,
        inventoryName:str, 
        references:bool=False, 
        fields:Union[list, str, None]=None,
        where:Union[list,tuple,str,None]=None, 
        orderBy:Union[dict,list,str, None]=None, 
        asc:Union[list,str,bool]=True, 
        pageSize:int=5000, 
        arrayPageSize:int=100000, 
        top:int=100000,
        validityDate:Optional[str]=None,
        allValidityPeriods:bool=False,
        includeSysProperties:bool=False,
        maxRecursionDepth=2
    ) -> pd.DataFrame:
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
            Optional property 'sys_revision': Returns number of updates of an item.
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
        maxRecursionDepth: int = 2
            Maximum recursion level following the references to other inventories.

        Example:
        --------
        >>> items('appartments', references=True)
        >>> items(
                'appartments',
                fields=['address', 'owner', 'sys_revision'],
                where=['city == "Berlin"', 'rooms > 2'],
                orderBy={'size':'DESC', price:'ASC'}
                )
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if inventoryName not in self.techStack.metaData.inventory:
                ErrorHandler.error(self.techStack.config.raiseException, f"'{inventoryName}' does not exist.")
                return pd.DataFrame()

            # where
            try:
                handleWhereResult = GraphQLUtil.handle_where_dyno(self.techStack, self, where, inventoryName)
                if handleWhereResult == None:
                    raise Exception("Could not handle where.")
                topLevelWhere, resolvedFilterDict = handleWhereResult
            except Exception as error:
                ErrorHandler.error(self.techStack.config.raiseException, f"Could not handle where. Error: {error}")
                return pd.DataFrame() # TODO not good for error handling, you only know that there was something wrong by looking into logs or set the raiseException flag to True

            validityDateStr = GraphQLUtil.arg_none('validityDate', validityDate)
            allValidityPeriodsStr = GraphQLUtil.arg_none('allValidityPeriods', allValidityPeriods)

            # core
            deleteId = False
            propertyDict = PropertyUtil.properties(self.techStack.metaData.scheme, inventoryName, recursive=True,
                sys_properties=includeSysProperties, max_recursion_depth=maxRecursionDepth)
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
                _fields = GraphQLUtil.query_fields(properties, propertyDict['arrayTypeFields'],
                                             arrayPageSize, filter=resolvedFilterDict, recursive=references)
            logger.debug(f"Fields: {_fields}")

            if len(_fields) == 0:
                ErrorHandler.error(self.techStack.config.raiseException, f"Inventory '{inventoryName}' not found.")
                return pd.DataFrame()

            order = OrderUtil.order_items(self.techStack, orderBy, asc)
            if order == None:
                return pd.DataFrame()

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

                graphQLString = f''' query getItems {{
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

                _result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                if not isinstance(_result, dict):
                    raise Exception("Result is not a dictionary.")
                
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
            
            if(df is None or df.empty):
                return pd.DataFrame()
            
            nested_columns = [col for col in df.columns if "." in col]
            if nested_columns:
                base_property_names = [col.split('.')[0] for col in nested_columns]
                subset_columns = [col for col in df.columns if col not in base_property_names]
                df = df[subset_columns]
        
            if fields != None: #sorts dataframe according to given fields
                try: # for array field this does not work
                    df = df[fields]
                except:
                    pass
            if deleteId:
                try:
                    if isinstance(df, pd.DataFrame) and not (df is None or df.empty):
                        del df['sys_inventoryItemId']
                except:
                    pass

            return pd.DataFrame(df)

    def inventoryProperties(
        self,
        inventoryName,
        namesOnly=False
    ) -> Union[pd.DataFrame, list, None]:
        """
        Returns a DataFrame of a query of properties of an inventory.

        Parameters:
        ----------
        inventoryName : str
            The name of the inventory.
        namesOnly : bool
            If True, only property names will be returned

        Example:
        --------
        >>> inventoryProperties('appartments') 


        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            propertyFields = f'''
                name          
                ... Scalar
                isArray
                nullable
                ... Reference
                type
                propertyId
            '''

            graphQLString = f'''query Inventory {{
            inventory
                (inventoryName: "{inventoryName}")
                {{
                properties {{
                    {propertyFields}
                    }}
                }}
            }}
            fragment Scalar on IScalarProperty {{
                dataType
                }}
            fragment Reference on IReferenceProperty {{
                inventoryId
                inventoryName
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if (result == None or (not isinstance(result, dict))):
                raise Exception("Could not get inventory properties.")
            
            if result['inventory'] == None:
                ErrorHandler.error(self.techStack.config.raiseException, f"Inventory '{inventoryName}' not found.")
                return

            df = pd.json_normalize(result['inventory']['properties'])

            if namesOnly == True:
                return list(df['name'])
            else:
                return df

    def propertyList(self, inventoryName: str, references=False, dataTypes=False, maxRecursionDepth=2) -> Union[pd.Series, list, None]:
        """
        Returns a list of properties of an inventory and its referenced inventories
        by reading out the scheme.

        Parameters:
        ----------
        inventoryName : str
            The name of the inventory.
        references : bool
            If True, properties of referenced inventories included.
        dataTypes : bool
            If True, result will be displayed as Series with properties as index and
            dataTypes as values.
        maxRecursionDepth: int = 2
            Maximum recursion level following the references to other inventories.

        Example:
        --------
        >>> propertyList('appartments') 

        """

        propertyDict = PropertyUtil.properties(self.techStack.metaData.scheme, inventory_name=inventoryName, 
                                               recursive=references, max_recursion_depth=maxRecursionDepth)

        if dataTypes == False:
            properties = PropertyUtil.property_list(propertyDict['properties'], recursive=references)
        else:
            properties = pd.Series(PropertyUtil.property_types(propertyDict['properties']))

        return properties

    def filterValues(
        self,
        inventoryName: str,
        top: int = 10000
    ) -> pd.DataFrame:
        """
        Returns a DataFrame of values that can be used in a where-string. 
        Only string data types are returned. 

        Parameters:
        ----------
        inventoryName : str
            The name of the inventory.
        top: int = None
            Uses a restricted set of items oriented at the latest entries to 
            provide a value set.

        Example:
        --------
        >>> filterValues('appartments') 

        """
        properties = self.propertyList(inventoryName, dataTypes=True)
        if (type(properties) != pd.Series):
            raise Exception("Could not get property list.")
        
        logger.debug(f"Properties: {properties}")

        propertyList = []
        for property, dataType in zip(properties.index, properties):
            if 'sys_' in property:
                continue
            if dataType != 'String':
                continue
            propertyList.append(property)
        logger.debug(f"PropertyList: {propertyList}")

        df = self.items(inventoryName, fields=propertyList, top=top)
        if (df is None or df.empty):
            raise Exception("Could not get items.")
        
        logger.debug(f"Used columns: {df.columns}")

        propertyValues = {}
        for property in propertyList:
            if 'sys_' in property:
                continue
            if len(set(df[property])) == len(df):
                continue
            propertySet = set(df[property])
            logger.debug(f"PropertySet: {propertySet}")
            try:
                propertySet.remove(None)
            except:
                pass
            propertyValues.setdefault(
                df[property].name, sorted(list(propertySet)))

        valuesDf = pd.DataFrame.from_dict(propertyValues, orient='index').T
        valuesDf.fillna(value='-', inplace=True)
        return valuesDf

    def __addItems(
        self,
        inventoryName: str,
        items: list
    ) -> Optional[list]:
        """
        Adds from a list of dicts new items and returns a list
        of inventoryItemIds.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        items : list
            A list with dictionaries for each item.

        Example:
        --------
        >>> items = [
                {
                'meterId': '86IEDD99',
                'dateTime': '2020-01-01T05:50:59Z'
                },
                {
                'meterId': '45IXZ52',
                'dateTime': '2020-01-07T15:41:14Z'
                }
            ]
        >>> addItems('meterData', items)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            itemsStr = PropertyUtil.properties_to_string(items)
            key = f'create{inventoryName}'

            graphQLString = f'''mutation addItems {{
                {key} (input: 
                    {itemsStr}
                )
                    {{
                        {GraphQLUtil.errors}           
                    inventoryItems {{
                        sys_inventoryItemId
                    }}
                }}
            }} 
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
            
            return result[key]['inventoryItems']

    def addItems(
        self,
        inventoryName:str, 
        items:list,
        chunkSize:int = 5000, 
        pause:int = 1
        ) -> list:
        """
        Adds from a list of dicts new items and returns a list
        of inventoryItemIds.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        items : list
            A list with dictionaries for each item.
        chunkSize : int = 5000
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading. Default is 5000 items per chunk.
        pause : int = 1
            Pause in seconds between each chunk upload to avoid overloading.

        Example:
        --------
        >>> items = [
                {
                'meterId': '86IEDD99',
                'dateTime': '2020-01-01T05:50:59Z'
                },
                {
                'meterId': '45IXZ52',
                'dateTime': '2020-01-07T15:41:14Z'
                }
            ]
        >>> addItems('meterData', items)        
        """
        
        correlationId = str(uuid4())
        result = []
        with logger.contextualize(correlation_id=correlationId):
            if len(items) > chunkSize:
                lenResult = 0
                for i in range(0, len(items), chunkSize):
                    result_object = self.__addItems(inventoryName, items[i : i + chunkSize])
                    if result_object != None:
                        result.extend(result_object)
                        lenResult = len(result)
                    logger.info(f"{lenResult} items of {len(items)} added. Waiting {pause} second(s) before continuing...")
                    sleep(pause)
            else:
                result_object = self.__addItems(inventoryName, items)
                if (result_object != None):
                    result.extend(result_object)
                logger.info(f"{len(result)} items added.")
        
        return result

    def __addValidityItemsToParents(
        self, 
        inventoryName:str, 
        items:list
    ) -> Optional[list]:
        """
        Adds from a list of dicts items with validity periods to an existing parent items. 
        The 'sys_parentInventoryItemId' and either 'sys_validFrom' or 'sys_validFrom' are required
        system properties.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        items : list
            A list with dictionaries for each item.

        Example:
        --------
        >>> items = [
                {
                'meterId': '86IEDD99',
                'userId': 'DlvK5PCm4u',
                'sys_parentInventoryItemId': 'EaM9zHA8Mi',
                'sys_validFrom': '2023-12-31T23:00:00.000Z',
                'sys_validTo': '2024-06-30T23:00:00.000Z',
                },
                {
                'meterId': '86IEDD99',
                'userId': 'DlvK5PCm8i',
                'sys_parentInventoryItemId': 'EaM9zHA8Mi',
                'sys_validFrom': '2024-07-31T23:00:00.000Z',
                'sys_validTo': '2024-09-30T23:00:00.000Z',
                }
            ]
        >>> addValidityItemsToParents('meterData', items)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            itemsStr = PropertyUtil.properties_to_string(items)
            key = f'create{inventoryName}ValidityPeriods'

            graphQLString = f'''mutation addValidityPeriodItemsToParents {{
                {key} (input: 
                    {itemsStr}
                )
                    {{
                        {GraphQLUtil.errors}           
                    inventoryItems {{
                        sys_inventoryItemId
                        sys_versionId
                    }}
                }}
            }} 
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            if (not isinstance(result, dict)):
                raise Exception("Result is not a dictionary.")
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
            return result[key]['inventoryItems']

    def addValidityItemsToParents(
        self, 
        inventoryName:str, 
        items:list,
        chunkSize:int = 5000, 
        pause:int = 1
        ) -> list:
        """
        Adds from a list of dicts items with validity periods to an existing parent items. 
        The 'sys_parentInventoryItemId' and either 'sys_validFrom' or 'sys_validFrom' are required
        system properties.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        items : list
            A list with dictionaries for each item.
        chunkSize : int = 5000
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading. Default is 5000 items per chunk.
        pause : int = 1
            Pause in seconds between each chunk upload to avoid overloading.

        Example:
        --------
        >>> items = [
                {
                'meterId': '86IEDD99',
                'userId': 'DlvK5PCm4u',
                'sys_parentInventoryItemId': 'EaM9zHA8Mi',
                'sys_validFrom': '2023-12-31T23:00:00.000Z',
                'sys_validTo': '2024-06-30T23:00:00.000Z',
                },
                {
                'meterId': '86IEDD99',
                'userId': 'DlvK5PCm8i',
                'sys_parentInventoryItemId': 'EaM9zHA8Mi',
                'sys_validFrom': '2024-07-31T23:00:00.000Z',
                'sys_validTo': '2024-09-30T23:00:00.000Z',
                }
            ]
        >>> addValidityItemsToParents('meterData', items)
        """

        correlationId = str(uuid4())
        result = []
        with logger.contextualize(correlation_id=correlationId):
            if len(items) > chunkSize:
                lenResult = 0
                for i in range(0, len(items), chunkSize):
                    result_object = self.__addValidityItemsToParents(inventoryName, items[i : i + chunkSize])
                    if result_object != None:
                        result.extend(result_object)
                        lenResult = len(result)
                    logger.info(f"{lenResult} validity items of {len(items)} added. Waiting {pause} second(s) before continuing...")
                    sleep(pause)
            else:
                result_object = self.__addValidityItemsToParents(inventoryName, items)
                if (result_object != None):
                    result.extend(result_object)
                logger.info(f"{len(result)} validity items added.")
        
        return result

    def updateItems(
        self,
        inventoryName: str,
        items: Union[list, dict]
    ) -> Optional[str]:
        """
        Updates from a list of dicts existing items and returns a list
        of inventoryItemIds. The 'sys_inventoryItemId'
        must be passed to each item.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        items : list
            A list with dictionaries for each item.

        Example:
        --------
        >>> items = [
                {
                'sys_inventoryItemId':'118312438662692864',
                'meterId': '86IEDD99',
                'dateTime': '2020-01-01T05:50:59Z'
                },
                {
                'sys_inventoryItemId':'118312438662692864',
                'meterId': '45IXZ52',
                'dateTime': '2020-01-07T15:41:14Z'
                }
            ]
        >>> updateItems('meterData', items)
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            itemsStr = PropertyUtil.properties_to_string(items)
            key = f'update{inventoryName}'

            graphQLString = f'''mutation updateItems {{
                {key} (input: 
                    {itemsStr}
                )
                    {{
                        {GraphQLUtil.errors}           
                        inventoryItems {{
                            sys_inventoryItemId
                    }}
                }}
            }}
            '''
            logger.trace(graphQLString)
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)

            logger.info(
                f"{len(result[key]['inventoryItems'])} item(s) updated.")
            return result[key]['inventoryItems']

    def updateDataFrameItems(
        self,
        inventoryName: str,
        dataFrame: pd.DataFrame,
        columns: Optional[list] = None
    ) -> None:

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            #TODO: Set the definition to Union[list, dict] to tell pyright everything is fine. Needs to be check if this is correct.
            def convertDfToDict(df: pd.DataFrame, timeSeries: bool, columns: Optional[list] = None) -> Union[list, dict]:

                def createDict(df: pd.DataFrame):
                    items = []
                    for _, row in df.iterrows():
                        item = {}
                        for header, value in zip(df.columns, row):
                            if not pd.isna(value):
                                item.setdefault(header, value)
                        items.append(item)
                    return items

                if timeSeries == True:
                    tsProperties = ['resolution', 'unit']
                    if columns == None:
                        columns = [
                            col for col in df.columns if col not in tsProperties]
                    else:
                        columns = [
                            col for col in columns if col not in tsProperties]

                if columns == None:
                    return createDict(df)
                else:
                    if 'sys_inventoryItemId' not in columns:
                        columns.append('sys_inventoryItemId')
                    subDf = df[columns]
                    if isinstance(subDf, pd.Series):
                        return subDf.to_dict()
                    return subDf.to_dict('records')

            if not 'sys_inventoryItemId' in dataFrame.columns:
                logger.error(
                    "Missing column 'sys_inventoryItemId'. Items cannot be updated without this information.")
                return

            if self.techStack.metaData.structure[inventoryName]['variant'] == None:
                items = convertDfToDict(dataFrame, False, columns=columns)
            elif self.techStack.metaData.structure[inventoryName]['variant']['name'] not in ['TimeSeries', 'TimeSeriesGroup']:
                items = convertDfToDict(dataFrame, False, columns=columns)
            else:
                items = convertDfToDict(dataFrame, True, columns=columns)

            if items is not None and len(items) > 0:
                if isinstance(items, (list, tuple)):
                    logger.debug(f"Items to write: {items[:3]}")
                else:
                    logger.debug(f"Items to write: {list(items.items())[:3]}")

            self.updateItems(inventoryName, items)
            return

    def createInventory(
        self,
        name: str,
        properties: list,
        variant: Optional[str] = None,
        propertyUniqueness: Optional[list] = None,
        historyEnabled: bool = False,
        hasValitityPeriods: bool = False,
        isDomainUserType: bool = False
    ) -> Optional[str]:
        """
        Creates a new inventory. After creation, access rights must be set to add items.

        Parameters:
        ----------
        name : str
            Name of the new inventory (only alphanumeric characters allowed, 
            may not begin with a number)
        properties : list
            A list of dicts with the following mandatory keys: 
                name: str
                dataType: enum (STRING, BOOLEAN, DECIMAL, INT, LONG, DATE_TIME, 
                DATE_TIME_OFFSET)
            Optional keys:
                isArray: bool (Default = False)
                nullable: bool (Default = True)
                isReference: bool (Default = False)
                inventoryId: str (mandatory if hasReference = True)
        variant : str
            The inventory variant.
        propertyUniqueness : list
            A list of properties that should be unique in its combination. 
        historyEnabled : bool
            If True, changes in properties will be recorded in item history.
        hasValidityPeriods : bool
            If true, a validity period can be added to the item.    

        Example:
        --------
        >>> propertyDefinitions = [
            {
                'name': 'street',
                'dataType': 'STRING',
                'nullable': False,
            },
            {
                'name': 'postCode',
                'dataType': 'STRING',
                'nullable': False,
            },
            ]
            uniqueness = [{'uniqueKey': 'address', 'properties': ['street', 'postCode']}
        >>> createInventory('appartment', 'propertyDefinitions', propertyUniqueness=uniqueness) 
        """

        logger.info(f"Creating new inventory {name}.")
        
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            _properties = PropertyUtil.properties_to_string(properties)

            if variant != None:
                variants = self.variants()
                if (variants is None or variants.empty):
                    raise Exception("Could not get variants.")
                
                _variantId = f'{DataFrameUtil.get_variant_id(variants, variant)}'
                logger.debug(f"Found variantId: {_variantId}")
                if type(_variantId) != str:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Variant name '{name}' not found")
                    return

                _variant = f'variantId: "{_variantId}"'
            else:
                _variant = ''

            if propertyUniqueness != None:
                _propertyUniqueness = 'propertyUniqueness: ' + \
                    GraphQLUtil.uniqueness_to_string(propertyUniqueness)
                logger.debug(_propertyUniqueness)
            else:
                _propertyUniqueness = ''

            _history = 'true' if historyEnabled != False else 'false'
            _validityPeriods = 'true' if hasValitityPeriods != False else 'false'
            _domainUser = 'true' if isDomainUserType != False else 'false'

            graphQLString = f'''
            mutation createInventory {{
                createInventory (input: {{
                    name: "{name}"        
                    properties: {_properties}
                    {_variant}
                    historyEnabled: {_history}
                    hasValidityPeriods: {_validityPeriods}
                    isDomainUserType: {_domainUser}
                    {_propertyUniqueness}
                    }})
                    {{
                    inventory {{
                        inventoryId
                        }}
                    {GraphQLUtil.errors}           
                }}
            }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            if result['createInventory']['errors']:
                GraphQLUtil.list_graphQl_errors(result, 'createInventory')
                return

            logger.info(f"New inventory {name} created.")

            if variant != None:
                self.timeseriesSchemaChanged()
                logger.info(f"Timeseries schema changed.")

            return result['createInventory']['inventory']['inventoryId']

    def deleteInventories(
        self,
        inventoryNames: list,
        deleteWithData: bool = False,
        force: bool = False
    ) -> None:
        """ 
        Deletes one or more inventories with the possibility to delete containing data.

        Parameters:
        -----------
        inventoryNames : list
            A list of inventory names that should be deleted.
        deleteWithData : bool = False
            If True, containing data will be deleted.
        force : bool
            Use True to ignore confirmation.

        Example:
        ---------
        >>> deleteInventories(['meterData'], deleteWithData=True, force=True)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            inventoryIds = []
            errorNames = []
            for name in inventoryNames:
                if deleteWithData and not self._isInventoryOfValidVariant(name):
                    ErrorHandler.error(self.techStack.config.raiseException, f"TimeSeries inventory {name} cannot be deleted with option 'deleteWithData'.")
                    continue
                try:
                    inventoryIds.append(self.techStack.metaData.structure[name]['inventoryId'])
                except:
                    errorNames.append(name)

            if errorNames:
                ErrorHandler.error(self.techStack.config.raiseException, f"Unknown inventory names '{errorNames}'.")
                return
            if len(inventoryIds) == 0:
                logger.info(f"No inventories to delete.")
                return

            _inventoryIds = GraphQLUtil.graphQL_list(inventoryIds)

            confirm = None
            if force == False:
                confirm = input(f"Press 'y' to delete '{inventoryNames}': ")

            key = 'deleteInventory'
            graphQLString = f'''mutation deleteInventories {{
                {key} (input:
                    {{
                        inventoryIds: {_inventoryIds}
                        ignoreData: {GraphQLUtil.to_graphql(deleteWithData)}
                    }}
                )
                    {{
                        {GraphQLUtil.errors}           
                    }}
                }}
                '''

            if force == True:
                confirm = 'y'
                
            if confirm == 'y':
                result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                if result == None:
                    return
                elif not isinstance(result, dict):
                    raise Exception("Result is not a dictionary.")
                
                if result[key]['errors']:
                    GraphQLUtil.list_graphQl_errors(result, key)
                    return
                else:
                    logger.info(f"Inventories '{inventoryNames}' deleted.")
            else:
                return

    def variants(self) -> Optional[pd.DataFrame]:
        """
            Returns a dataframe of available variants.
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            key = 'variants'
            graphQLString = f'''query getVariants {{
            {key} {{
                name
                variantId
                }}
            }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            df = pd.json_normalize(result[key])
            return df

    def deleteVariant(
        self,
        variantId: str,
        force: bool = False
    ) -> None:
        """Deletes a variant

        Parameters
        -----------
        variantId : str
            The id of the variant.
        force : bool
            Use True to ignore confirmation.
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            confirm = None
            if force == False:
                confirm = input(
                    f"Press 'y' to delete  variant with Id {variantId}: ")

            key = 'deleteVariant'
            graphQLString = f'''mutation deleteVariant {{
                {key}(input: {{ variantId: "{variantId}" }}) {{
                    errors {{
                    message
                    code
                    }}
                }}
            }}
            '''

            if force == True:
                confirm = 'y'
            if confirm == 'y':
                result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                if result == None:
                    return
            else:
                return

            if not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
             
            if result[key]['errors'] != None:
                GraphQLUtil.list_graphQl_errors(result, key)
            else:
                logger.info(f"Variant deleted.")

    def deleteItems(
        self,
        inventoryName: str,
        inventoryItemIds: Optional[list] = None,
        where: Optional[str] = None,
        force: bool = False,
        pageSize: int = 500
    ) -> None:
        """
        Deletes inventory items from a list of inventoryItemIds or by where-criteria. 

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
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
            if not self._isInventoryOfValidVariant(inventoryName):
                ErrorHandler.error(self.techStack.config.raiseException, f"Items of a TimeSeries inventory cannot be deleted. Use TimeSeries.deleteItems() instead.")
                return
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

                if (not isinstance(result, dict)):
                    raise Exception("Result is not a dictionary.")
                
                if result[key]['errors'] != None:
                    logger.error(GraphQLUtil.list_graphQl_errors(result, key))
                    return

            if inventoryItemIds == None and where == None:
                ErrorHandler.error(self.techStack.config.raiseException, f"No list of items and no where-criteria were provided.")
                return

            if inventoryItemIds != None and where != None:
                logger.warning(f"List of items and where-criteria has been provided. Item list is used.")

            ids = []
            if where != None:
                _result = self.items(inventoryName, fields=['sys_inventoryItemId'], where=where)
                if (_result is None or _result.empty):
                    raise Exception("Could not get items.")
                
                if _result.empty:
                    logger.info(f"No results found for provided filter.")
                    return
                ids = list(_result['sys_inventoryItemId'])
            if inventoryItemIds != None:
                _result = self.items(inventoryName, fields=['sys_inventoryItemId'], where=f'sys_inventoryItemId in {inventoryItemIds}')
                if (_result is None or _result.empty):
                    raise Exception("Could not get items.")
                
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

    def clearInventory(
        self,
        inventoryName: str,
        force: bool = False,
        pageSize: int = 500
    ) -> None:
        """
        Deletes all items from the inventory

        Parameters
        -----------
        inventoryName : str
            The name of the inventory.
        force : bool
            Use True to ignore confirmation.
        pageSize : str = 500
            The number of items to be deleted in a chunk (the maximum number 
            of items that can be deleted in one mutation is restricted).

        Example:
        ---------
        >>> clearInventory('meterData', force=True)
        """

        count = 0
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if not self._isInventoryOfValidVariant(inventoryName):
                ErrorHandler.error(self.techStack.config.raiseException, f"Items of a TimeSeries inventory cannot be deleted. Use TimeSeries.deleteItems() instead.")
                return
            
            if force:
                confirm = 'y'
            else:
                confirm = input(f"Press 'y' to delete all items in inventory {inventoryName}: ")
            if confirm != 'y':
                return

            lastId = ''
            
            deleteKey = f'delete{inventoryName}'

            while True:
                graphQLString = f''' query getItems {{
                        {inventoryName} (
                                pageSize: {pageSize} 
                                {lastId}
                                ) {{
                            sys_inventoryItemId
                        }}
                    }}
                    '''

                _result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                if (not isinstance(_result, dict)):
                    raise Exception("Result is not a dictionary.")
                
                ids = [item['sys_inventoryItemId'] for item in _result[inventoryName]]
                latestCount = len(ids)
                count += latestCount

                _ids = ''
                for id in ids:
                    _ids += f'{{sys_inventoryItemId: "{id}"}}\n'

                result = None
                if latestCount > 0:
                    try:
                        cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                        lastId = f'lastId: "{cursor}"'

                        graphQLString = f'''
                            mutation deleteItems {{
                                {deleteKey} ( input: 
                                    [{_ids}]
                                )
                                {{
                                    {GraphQLUtil.errors}           
                                }}
                            }}
                        '''
                        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                    except Exception as error:
                        ErrorHandler.error(self.techStack.config.raiseException, 
                                        f"Inventory is empty. No items were deleted. Error {error}")
                        break
                
                if latestCount == 0 or result == None:
                    logger.info(f"Inventory is empty. No items were deleted in last request.")
                    break
                if not isinstance(result, dict):
                    raise Exception("Result is not a dictionary.")
                
                if result[deleteKey]['errors'] != None:
                    GraphQLUtil.list_graphQl_errors(result, deleteKey)
                else:
                    logger.info(f"{latestCount} items deleted in last request.")

            if count == 0:
                logger.info(f"Inventory is empty. No items were deleted.")
            
        logger.info(f"{count} items deleted.")
        return

    def updateVariant(
        self,
        variantName,
        newName=None,
        icon=None
    ) -> None:
        """Updates a variant"""

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            variants = self.variants()
            if (variants is None or variants.empty):
                raise Exception("Could not get variants.")
            
            _variantId = DataFrameUtil.get_variant_id(variants, variantName)
            logger.debug(f"Found variantId: {_variantId}")

            if newName != None:
                _name = f'name: "{newName}"'
            else:
                _name = 'null'

            if icon != None:
                _icon = f'icon: "{icon}"'
            else:
                _icon = 'null'

            key = 'updateVariant'
            graphQLString = f'''mutation updateVariant {{
                {key} (input:{{
                    variantId: "{_variantId}"
                    {_name}
                    {_icon}
                    }})
                    {{
                        {GraphQLUtil.errors}           
                    }}
                }}
                '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return

            return

    def updateArrayProperty(
        self,
        inventoryName: str,
        inventoryItemId: str,
        arrayProperty: str,
        operation: str,
        arrayItems: Optional[list] = None,
        cascadeDelete: bool = False
    ) -> None:
        """
        Updates a single array property of a single inventoryItemId. Arrays with and without 
        references are supported.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory where the item is located.
        inventoryItemId: str
            The sys_inventoryItemId of the item.
        arrayProperty: str
            The name of the property whose array items are to be updated.
        operation: str
            The update operation to be performed. Options:
            insert: inserts a list of array items.
            removeById: removes array items by a list of given ids.
            removeByIndex: removes array items by a list of given indices.
            removeAll: removes all array items
        arrayItems: list = None
            A list of indices or item Ids
        cascadeDelete: bool = False
            If array items are refencences, True will delete also the reference items. 

        Examples:
        ---------
        >>> client.updateArrayProperty('meterData', 'A5N45hOOmm',
                'timeSeries', action='insert', arrayItems=['A5FdSjehbE'])
        >>> client.updateArrayProperty('meterData', 'A5N45hOOmm',
                'timeSeries', action='removeByIndex', arrayItems=[0,1], cascadeDelete=True)
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            operations = ['insert', 'removeById', 'removeByIndex', 'removeAll']
            if operation not in operations:
                ErrorHandler.error(self.techStack.config.raiseException, f"Action '{operation}' allowed. Possible update operations: {operations}.")
                return

            if operation == 'removeAll':
                try:
                    propertyDf = self.inventoryProperties(inventoryName)
                    if (type(propertyDf) != pd.DataFrame):
                        raise Exception("Could not get properties.")
                    
                    arrayProps = propertyDf[propertyDf['name'] == arrayProperty]
                    logger.debug(f"Properties of array: {arrayProps}")
                    if arrayProps['type'].item() == 'reference':
                        arrDf = self.items(inventoryName, where=f'sys_inventoryItemId eq "{inventoryItemId}"', \
                                           fields=[f'{arrayProperty}.sys_inventoryItemId'],
                                                )
                    else:
                        arrDf = self.items(inventoryName, fields=[{arrayProperty}], \
                                           where=f'sys_inventoryItemId eq "{inventoryItemId}"')
                except Exception as err:
                    ErrorHandler.error(self.techStack.config.raiseException, f'{err}')
                    return
                
                if (arrDf is None or arrDf.empty):
                    raise Exception("Could not get array items.")
                
                countArray = len(arrDf[arrayProperty].item())
                arrayItems = [num for num in range(countArray)]
                logger.debug(f"Array Items: {arrayItems}")
            
            if (arrayItems == None):
                arrayItems = []
            _arrayItems = GraphQLUtil.array_items_to_string(arrayItems, operation, cascadeDelete)
            logger.debug(f"Array Items as String: {_arrayItems}")

            key = f'update{inventoryName}ArrayProperties'
            graphQLString = f'''mutation updateArray {{
                {key} (
                    input: {{
                    sys_inventoryItemId: "{inventoryItemId}"
                    {arrayProperty}: {{
                        {_arrayItems}
                        }}
                    }}
                ) 
                {{
                    {GraphQLUtil.errors}           
                }}
            }}'''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            if result[key]['errors'] != None:
                GraphQLUtil.list_graphQl_errors(result, key)
            else:
                logger.info(
                    f"Array property {arrayProperty} for item {inventoryItemId} updated.")

    def addInventoryProperties(
        self,
        inventoryName: str,
        properties: list
    ) -> None:
        """
        Adds one or more inventory properties to an existing inventory.

        Parameters:
        ----------
        inventoryName: str
            Name of inventory
        properties: list
            A list of dicts with the following mandatory keys: 
                name: str
                dataType: enum (STRING, BOOLEAN, DECIMAL, INT, LONG, DATE_TIME, 
                DATE_TIME_OFFSET)
            Optional keys:
                isArray: bool (Default = False)
                nullable: bool (Default = True)
                isReference: bool (Default = False)
                inventoryId: str (mandatory if hasReference = True)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            key = 'addProperty'
            inventory = self.inventories(where=f'name eq "{inventoryName}"')

            if inventory is None or inventory.empty:
                ErrorHandler.error(self.techStack.config.raiseException, f"Unknown inventory '{inventoryName}'.")
                return

            inventoryId = inventory.loc[0, 'inventoryId']
            _properties = PropertyUtil.properties_to_string(properties)

            graphQLString = f'''
            mutation {key} {{
            {key} (input: {{
                inventoryId: "{inventoryId}"	
                properties: {_properties}
                }}) 
                {{
                    {GraphQLUtil.errors}           
                }}
            }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
                return
            else:
                self.dynoSchemaChanged()
                logger.info(f"New property(ies) added.")

    def updateDisplayValue(
        self,
        inventoryName: str,
        displayValue: str
    ) -> None:

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            inventoryId = self.techStack.metaData.structure[inventoryName]['inventoryId']

            key = 'updateInventory'
            graphQLString = f'''mutation updateDisplayValue {{
                {key} (input: {{
                    inventoryId: "{inventoryId}"
                    displayValue: "{displayValue}"
                    }}) {{
                    {GraphQLUtil.errors}
                }}
            }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
                return
            else:
                self.dynoSchemaChanged()
                logger.info(f"Display value updated.")
                return

    def updateInventoryName(
        self,
        inventoryName: str,
        newName: str
    ) -> None:

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            inventoryId = self.techStack.metaData.structure[inventoryName]['inventoryId']
            key = 'updateInventory'

            graphQLString = f'''mutation updateInventoryName {{
                {key} (input: {{
                    name: "{newName}"
                    inventoryId: "{inventoryId}"
                }}) {{
                    {GraphQLUtil.errors}
                    }}
                }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
                return
            else:
                logger.info(f"Inventory name updated.")
                self.dynoSchemaChanged()
                return

    def removeProperties(
        self,
        inventoryName: str,
        properties: list
    ) -> None:
        """
        Removes a list of properties given as property names. Properties can 
        only be removed if they have no content or are of type 'reference'.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory where the item is located.
        properties: list
            A list of property names.
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if type(properties) != list:
                properties = [properties]

            propertyList = '['
            for argProperty in properties:
                try:
                    propertyId = self.techStack.metaData.structure[inventoryName]['properties'][argProperty]['propertyId']
                    propertyList += f'"{propertyId}",'
                except:
                    logger.warning(
                        f"Property '{argProperty}' not found in inventory '{inventoryName}'.")
            propertyList += ']'

            inventoryId = self.techStack.metaData.structure[inventoryName]['inventoryId']

            key = 'removeProperty'
            graphQLString = f'''mutation removeProperty {{
                {key} (input: {{
                        inventoryId: "{inventoryId}"
                        propertyIds: {propertyList}
                }}) {{
                    {GraphQLUtil.errors}
                    }}
                }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
                return
            else:
                self.dynoSchemaChanged()
                logger.info(f"Properties have been removed.")
                return

    def updateProperty(
        self,
        inventoryName: str,
        propertyName: str,
        newPropertyName: Optional[str] = None,
        nullable: Optional[bool] = None
    ) -> None:

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            inventoryId = self.techStack.metaData.structure[inventoryName]['inventoryId']
            newPropertyNameStr = GraphQLUtil.arg_none('name', newPropertyName)
            nullableStr = GraphQLUtil.arg_none('nullable', nullable)

            try:
                propertyId = self.techStack.metaData.structure[inventoryName]['properties'][propertyName]['propertyId']
            except:
                ErrorHandler.error(self.techStack.config.raiseException, f"Property '{propertyName}' not found in inventory '{inventoryName}'.")
                return

            key = 'updateInventory'
            graphQLString = f'''mutation removeProperty {{
                {key} (input: {{
                        inventoryId: "{inventoryId}"
                        properties: [{{
                            propertyId: "{propertyId}"
                            {newPropertyNameStr}
                            {nullableStr}
                        }}]
                }}) {{
                    {GraphQLUtil.errors}
                    }}
                }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
                return
            else:
                self.dynoSchemaChanged()
                logger.info(f"Property updated.")
                return

    def resync(self) -> None:
        """Resynchronizes read databases"""

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            key = 'reSyncReadDatabase'
            graphQLString = f'''mutation resync{{
                {key}
                }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            self.dynoSchemaChanged()

            return

    def defaultDataFrame(
        self,
        maxRows,
        maxColumns
    ) -> None:
        """Sets default sizes for a DataFrame for the current session"""
        pd.options.display.max_rows = maxRows
        pd.options.display.max_columns = maxColumns
        return

    def _convertId(
        self,
        sys_inventoryItemId: str
    ) -> Optional[str]:
        """Convers a sys_inventoryItemId into a HAKOM name"""

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            graphQLString = f'''mutation convert{{
                convertId(id: "{sys_inventoryItemId}")
                }}
            '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary.")
            
            return result['convertId']

    def _isInventoryOfValidVariant(
        self,
        inventoryName: str,
        variantName: Optional[str] = None
    ) -> Optional[bool]:
        """Checks if an inventory is of a valid variant"""

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            inventory = self.inventories(where=f'name eq "{inventoryName}"', fields=['variant.name'])
            
            if inventory is None or inventory.empty:
                ErrorHandler.error(self.techStack.config.raiseException, f"Unknown inventory '{inventoryName}'.")
                return

            # in case of inventory without variant there is a column 'variant' with None
            if variantName == None:
                return 'variant' in inventory
            else:
                return not 'variant' in inventory and inventory.iloc[0]['variant.name'] == variantName