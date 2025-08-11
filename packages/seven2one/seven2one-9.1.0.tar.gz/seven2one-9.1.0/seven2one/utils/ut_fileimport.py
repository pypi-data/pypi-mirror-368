from typing import List, Optional, Union, Dict
import pandas
import pytz
import csv
from re import match
from loguru import logger
from datetime import datetime
from pathlib import Path

from seven2one.core_interface import ITechStack
from seven2one.dynamicobjects_interface import IDynamicObjects

class UtilsProperty():
    @staticmethod
    def _getDataTypes(properties: List[dict]) -> dict:
        """
        Sorts the property types and returns a dictionary of those properties 
        that are not of type STRING.
        """

        logger.debug(properties)
        propertyTypes = {'Boolean': [], 'Numeric': [],
                         'DateTime': [], 'String': [], 'Unknown': []}
        if 'dataType' not in properties[0]:
            return propertyTypes

        for property in properties:
            if property['dataType'] in ['DATE_TIME', 'DATE_TIME_OFFSET']:
                propertyTypes['DateTime'].append(property['name'])
            elif property['dataType'] == 'BOOLEAN':
                propertyTypes['Boolean'].append(property['name'])
            elif property['dataType'] in ['INT', 'LONG', 'DECIMAL']:
                propertyTypes['Numeric'].append(property['name'])

            elif property['dataType'] == 'STRING':
                propertyTypes['String'].append(property['name'])
            else:
                propertyTypes['Unknown'].append(property['name'])
        return propertyTypes

    @staticmethod
    def _getArrays(properties: List[dict]) -> list:
        """ Lists properties that are arrays (isArray) """

        p = [property['name']
             for property in properties if property['isArray'] == True]
        return p

    @staticmethod
    def _getNullables(properties: List[dict]) -> list:
        """ Lists properties that are nullable """

        p = [property['name']
             for property in properties if property['nullable'] == True]
        return p

    @staticmethod
    def _getReferences(properties: List[dict]) -> list:
        """ Lists properties that are nullable """

        p = [property['name']
             for property in properties if property['type'] == 'reference']
        return p

    @staticmethod
    def _transformBool(value: str):
        trueValues = ['ja', 'Ja', 'yes', 'Yes', 'True', 'true', 1]
        falseValues = ['nein', 'Nein', 'no', 'No', 'false', 'False', 0]
        if value in trueValues:
            return True
        elif value in falseValues:
            return False
        return None

    @staticmethod
    def _isInt(n: str):
        return bool(match(r'-?\d+$', n))

    @staticmethod
    def _isFloat(n: str) -> bool:
        return bool(match(r'-?\d+(\.\d+)$', n))

    @staticmethod
    def _transformNumeric(value: str) -> Union[int, float, None]:
        if UtilsProperty._isInt(value):
            return int(value)
        elif UtilsProperty._isFloat(value):
            return float(value)
        else:
            logger.warning(f"'{value}' is not of numeric data type!")
            return None

    @staticmethod
    def _checkIsList(pythonList: str) -> bool:
        if pythonList[0] != '[':
            return False
        elif pythonList[-1] != ']':
            return False
        else:
            return True

    @staticmethod
    def _transformList(pythonList: str, propertyType: str) -> list:
        """ Transforms a String into a Python list"""
        if not UtilsProperty._checkIsList(pythonList):
            # logger.warning(f"Value '{pythonList}' is not array type, try to transform...")
            pythonList = '[' + pythonList + ']'

        pythonListSplit = pythonList[1:-1].split(',')
        pythonListSplit = [element.strip() for element in pythonListSplit]

        _pythonList = []
        for element in pythonListSplit:
            if propertyType == 'Numeric':
                _pythonList.append(UtilsProperty._transformNumeric(element))
            elif propertyType == 'Boolean':
                _pythonList.append(UtilsProperty._transformBool(element))
            else:
                _pythonList.append(str(element))

        return _pythonList


class FileUtils(UtilsProperty):

    @staticmethod
    def _createItems(
            content: list,
            dataType: dict,
            isArray: list,
            nullable: list,
            referenceMapping: Optional[dict] = None,
            type: Optional[str] = None,
            uniqueProperty: Optional[str] = None,
            parentItemMapping: Optional[dict] = None):
        """
        Creates the dictionary that is imported by 'addItems()'

        Parameters:
        ----------
        content: list
            The CSV content as list
        dataType:dict
            Property data types returned by UtilsProperty._getPropertyTypes()
        isArray: list
            Provides information, if the column is of array type. Returned by 
            UtilsProperty._getArrays()
        nullable: list
            Provides information, if the column is nullable or not. Returned by
            UtilsProperty._getNullables()
        referenceMapping: dict = None
            Provides mapping of unique properties with sys_inventoryItemIds. Returned by
            FileUtils._createReferenceMapping()
        type: str = None
            If type is None, a 'basic' item is assumed. Another valid type is 'timeSeries'.
        """

        def _createItem(header):
            if i == 0:
                return
            if len(row) < 1:
                return
            else:
                item: Dict[str, Union[str, int, float, list, dict, None, dict]] = {}
                if type == None:
                    item = {}
                if type == 'timeSeries':
                    item = {'resolution': {}}
                for j, value in enumerate(row):

                    if not value:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(value) > 0:
                            logger.warning(
                                f"Line {i}, field '{header[j]}': Value missing for non nullable property.")
                            return
                        else:
                            pass
                    else:
                        if parentItemMapping != None:
                            if header[j] == uniqueProperty:
                                if parentItemMapping[value] != None:
                                    item.setdefault(
                                        'sys_parentInventoryItemId', parentItemMapping[value])
                        if referenceMapping != None and header[j] in referenceMapping:
                            parentHeader = header[j].split('.')[0]
                            if parentHeader in isArray:
                                nameList = UtilsProperty._transformList(
                                    value, 'String')
                                try:
                                    idList = [referenceMapping[header[j]][item]
                                              for item in nameList]
                                except KeyError as key:
                                    logger.warning(
                                        f"Line {i}, field '{header[j]}': {key} is not a valid reference.")
                                    return
                                item.setdefault(parentHeader, idList)
                            else:
                                try:
                                    item.setdefault(
                                        parentHeader, referenceMapping[header[j]][value])
                                except KeyError as key:
                                    logger.warning(
                                        f"Line {i}, field '{header[j]}': {key} is not a valid reference.")
                                    return
                        else:
                            if header[j] == 'sys_inventoryItemId':
                                if uniqueProperty == 'sys_inventoryItemId':
                                    continue
                            if header[j] in dataType['Boolean']:
                                if header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(value, 'Boolean'))
                                else:
                                    item.setdefault(header[j], UtilsProperty._transformBool(value))
                            elif header[j] in dataType['Numeric']:
                                if header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(value, 'Numeric'))
                                else:
                                    item.setdefault(header[j], UtilsProperty._transformNumeric(value))
                            elif header[j] in dataType['DateTime']:
                                if header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(value, 'DateTime'))
                                else:
                                    item.setdefault(header[j], value)
                            else:
                                if type == 'timeSeries' and header[j] == 'timeUnit':
                                    if isinstance(item['resolution'], dict): #TODO: The previous code is the line below. Asssuming it is an dict which can also be false.
                                        item['resolution'].setdefault('timeUnit', value)
                                elif type == 'timeSeries' and header[j] == 'factor':
                                    if isinstance(item['resolution'], dict): #TODO: The previous code is the line below. Asssuming it is an dict which can also be false.
                                        item['resolution'].setdefault('factor', value)
                                elif header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(value, 'String'))
                                else:
                                    item.setdefault(header[j], value)
                return item

        itemList = []
        validityItemList = []
        header = content[0]
        for i, row in enumerate(content):
            item = _createItem(header)
            if item != None:
                if 'sys_parentInventoryItemId' in item:
                    validityItemList.append(item)
                else:
                    itemList.append(item)
        if all((uniqueProperty, parentItemMapping)) == False:
            return itemList
        else:
            return (validityItemList, itemList)

    @staticmethod
    def _createInstanceItems(content: list, dataType: dict, isArray: list, nullable: list, idMapping: Optional[dict] = None,
                             transpose: bool = False) -> list:

        if transpose == True:
            content = list(map(list, zip(*content)))

        for column in content:
            if column[0] in ['unit', 'timeUnit', 'factor']:
                del column

        itemList = []
        header = content[0]
        for i, row in enumerate(content):
            itemOkay = True  # is changed to false, if certain criteria are not met -> warning message, next item
            if i == 0:
                continue
            if len(row) < 1:
                continue
            else:
                if idMapping != None:
                    try:
                        groupInventoryItemId = idMapping[content[i][0]]
                    except:
                        logger.warning(
                            f"ImportKeyProperty '{content[i][0]}' not found.")
                        continue
                else:
                    groupInventoryItemId = content[i][0]
                item = {'sys_groupInventoryItemId': groupInventoryItemId}
                for j, field in enumerate(row):
                    if j == 0:
                        continue

                    if not field:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(field) > 0:
                            logger.warning(
                                f"Value missing for non nullable {header[j]}. Item from line {i} not imported.")
                            itemOkay = False
                            break
                        else:
                            pass
                    else:
                        if header[j] in dataType['Boolean']:
                            if header[j] in isArray:
                                item.setdefault(
                                    header[j], UtilsProperty._transformList(field, 'Boolean'))
                            else:
                                item.setdefault(
                                    header[j], UtilsProperty._transformBool(field))
                        elif header[j] in dataType['Numeric']:
                            if header[j] in isArray:
                                item.setdefault(
                                    header[j], UtilsProperty._transformList(field, 'Numeric'))
                            else:
                                item.setdefault(
                                    header[j], UtilsProperty._transformNumeric(field))
                        elif header[j] in dataType['DateTime']:
                            if header[j] in isArray:
                                item.setdefault(
                                    header[j], UtilsProperty._transformList(field, 'DateTime'))
                            else:
                                # item.setdefault(header[j], UtilsProperty._convertTimestamp(field, timeZone))
                                item.setdefault(header[j], field)
                        else:
                            if header[j] in isArray:
                                item.setdefault(
                                    header[j], UtilsProperty._transformList(field, 'String'))
                            else:
                                item.setdefault(header[j], field)
                if itemOkay and len(item) > 0:
                    itemList.append(item)

        return itemList

    @staticmethod
    def _createTimeSeriesItems(content: list, dataType: dict, isArray: list, nullable: list):
        itemList = []
        header = content[0]
        for i, row in enumerate(content):
            itemOkay = True  # is changed to false, if certain criteria are not met -> warning message, next item
            if i == 0:
                continue
            if len(row) < 1:
                continue
            else:
                item: Dict[str, Union[str, int, float, list, dict, None, dict]] = {}
                item = {'resolution': {}}
                for j, field in enumerate(row):
                    if not field:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(field) > 0:
                            logger.warning(
                                f"Value missing for non nullable {header[j]}. Item from line {i} not imported.")
                            itemOkay = False
                            break
                        else:
                            pass
                    else:
                        if header[j] in dataType['Boolean']:
                            if header[j] in isArray:
                                item.setdefault(
                                    header[j], UtilsProperty._transformList(field, 'Boolean'))
                            else:
                                item.setdefault(
                                    header[j], UtilsProperty._transformBool(field))
                        elif header[j] in dataType['Numeric']:
                            if header[j] in isArray:
                                item.setdefault(
                                    header[j], UtilsProperty._transformList(field, 'Numeric'))
                            else:
                                item.setdefault(
                                    header[j], UtilsProperty._transformNumeric(field))
                        elif header[j] in dataType['DateTime']:
                            if header[j] in isArray:
                                item.setdefault(
                                    header[j], UtilsProperty._transformList(field, 'DateTime'))
                            else:
                                # item.setdefault(header[j], UtilsProperty._convertTimestamp(field, timeZone))
                                item.setdefault(header[j], field)
                        else:
                            if header[j] == 'timeUnit':
                                if isinstance(item['resolution'], dict): #TODO: The previous code is the line below. Asssuming it is an dict which can also be false.
                                    item['resolution'].setdefault('timeUnit', field)
                            elif header[j] == 'factor':
                                if isinstance(item['resolution'], dict): #TODO: The previous code is the line below. Asssuming it is an dict which can also be false.
                                    item['resolution'].setdefault('factor', field)
                            else:
                                if header[j] in isArray:
                                    item.setdefault(
                                        header[j], UtilsProperty._transformList(field, 'String'))
                                else:
                                    item.setdefault(header[j], field)
                if itemOkay and len(item) > 0:
                    itemList.append(item)

        return itemList

    @staticmethod
    def _comparePropertiesBasic(properties: list, header: list):
        """ Compares header with requested properties from a basic inventory. """

        propertiesList = set(properties)
        headerList = set(header)
        return headerList.difference(propertiesList)

    @staticmethod
    def _comparePropertiesTimeSeries(properties: list, header: list):
        """ Compares header with requested properties from a time series inventory. """

        propertiesList = set(properties)
        headerList = set(header)
        tsProperties = set(['timeUnit', 'factor', 'unit'])
        headerList = headerList - tsProperties
        return headerList.difference(propertiesList)

    @staticmethod
    def _analyzeProperties(inventoryName: str, properties: pandas.DataFrame) -> tuple:
        """ Analyzes inventory properties and returns dictionaries to each property attribute """

        #TODO: Check if this is correct. The result of properties.to_dict is a list of dictionaries. So i changed the signatures of the UtilsProperty methods to List[dict] and checked the impl.
        propertiesDict = properties.to_dict('records')
        dataType = UtilsProperty._getDataTypes(propertiesDict)
        isArray = UtilsProperty._getArrays(propertiesDict)
        nullable = UtilsProperty._getNullables(propertiesDict)
        isReference = UtilsProperty._getReferences(propertiesDict)

        logger.debug(f'Data types: {dataType}')
        logger.debug(f'Array properties: {isArray}')
        logger.debug(f'Nullable properties: {nullable}')
        logger.debug(f'Reference properties: {isReference}')

        return dataType, isArray, nullable, isReference

    @staticmethod
    def _convertTimestamp(timestamp, timeZone, dateTimeFormat, timeDelta):

        timestamp = datetime.strptime(timestamp, dateTimeFormat)
        if timeDelta != None:
            timestamp += timeDelta
        timestamp = pytz.timezone(timeZone).localize(timestamp).isoformat()
        return timestamp

    @staticmethod
    def _dateFormat(timestamp: str) -> Optional[str]:

        # German
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%d.%m.%Y %H:%M:%S.%f'
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M:%S'
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M'
        if match(r'\d{2}.\d{2}.\d{4}', timestamp):
            return '%d.%m.%Y'

        # ISO
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f+00:00'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S+00:00'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%fZ'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', timestamp):
            return '%Y-%m-%dT%H:%M:%SZ'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M'

        # English I
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S.%f+00:00'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S+00:00'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y-%m-%d %H:%M:%S.%f'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M'
        if match(r'\d{4}-\d{2}-\d{2}', timestamp):
            return '%Y-%m-%d'

        # English II
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y/%m/%d %H:%M:%S.%f'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M:%S'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M'
        if match(r'\d{4}/\d{2}/\d{2}', timestamp):
            return '%Y/%m/%d'

        # English III
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M:%S'
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M'
        if match(r'\d{1,2}/\d{1,2}/\d{4}', timestamp):
            return '%m/%d/%Y'

        return None

    @staticmethod
    def _createInstanceItemContent(content):
        itemContent = []
        for row in content:
            if row[0] not in ['unit', 'timeUnit', 'factor']:
                itemContent.append(row)

        return itemContent

    @staticmethod
    def _checkFilePath(filePath, raiseException):
        """Checks and handles the file path"""
        filePath = Path(filePath)
        if str(filePath).lower().endswith('csv'):
            if not filePath.exists():
                msg = f"File path {filePath} does not exist"
                if raiseException:
                    raise Exception(msg)
                else:
                    logger.error(msg)
                    return
            return [filePath]

        else:
            if not filePath.exists():
                msg = f"File path {filePath} does not exist"
                if raiseException:
                    raise Exception(msg)
                else:
                    logger.error(msg)
                    return
            files = [file for file in filePath.iterdir() if str(
                file).lower().endswith('csv')]
            msg = f"No csv files found in {filePath}"
            if len(files) == 0:
                if raiseException:
                    raise Exception(msg)
                else:
                    logger.error(msg)
                    return
            logger.debug(f"FileUtils._checkFilePath: {files}")
            return files

    @staticmethod
    def _readCsvFile(file, delimiter, encoding : Optional[str] = 'utf-8-sig') -> list:
        with open(file, 'r', encoding=encoding, newline='') as f:
            csv_file = csv.reader(f, delimiter=delimiter)
            content = [row for row in csv_file]
            logger.debug(f"CSV file '{file.name}' read.")
        return content

    @staticmethod
    def _checkReferences(fields: list):
        """
        Checks, if reference fields have multilevel and returns a list of one-level
        fields and error an list
        """
        references = []
        errors = []
        for field in fields:
            if field.count('.') == 0:
                continue
            elif field.count('.') == 1:
                references.append(field)
            elif field.count('.') > 1:
                errors.append(field)
            else:
                pass

        return references, errors

    @staticmethod
    def _createReferenceMapping(techStack: ITechStack, dynamicObjects: IDynamicObjects, inventoryName: str, referenceFields: list, isArray: list, content: list) -> dict:
        """
        Creates a dictionary of mapping inventoryItemIds with the import items of reference.
        """
        references = {}
        contentFrames = pandas.DataFrame(content[1:], columns=content[0])
        for field in referenceFields:
            parentField = field.split('.')[0]
            childField = field.split('.')[1]
            sysId = False
            if childField == 'sys_inventoryItemId':
                sysId = True
            if parentField in isArray:
                listOfLists = []
                for item in contentFrames[field]:
                    if len(item) == 0:
                        continue
                    listOfLists.append(
                        UtilsProperty._transformList(item, 'String'))
                nameList = list(set().union(*listOfLists))
            else:
                nameList = list(set(contentFrames[field]))

            logger.debug(f"nameList: {nameList}")

            if sysId == False:
                inventory = techStack.metaData.structure[inventoryName]['properties'][parentField]['inventoryName']
                df = dynamicObjects.items(inventory, fields=['sys_inventoryItemId', childField], where=f'{childField} in {nameList}')
                if (df is None or df.empty):
                    raise Exception(f"Reference field '{field}' not found in inventory '{inventory}'")
                
                mapping = {item[1][childField]: item[1]
                           ['sys_inventoryItemId'] for item in df.iterrows()}
            else:
                mapping = {item: item for item in nameList}

            references.setdefault(field, mapping)

        return references

    @staticmethod
    def _createParentMapping(techStack: ITechStack, dynamicObjects: IDynamicObjects, inventoryName: str, content: list, uniqueProperty: str) -> dict:
        """
        Checks a list of fields unique fields whether they exist or not. Returns a dict of 
        value:sys_inventoryItemId. Is used to import validity Items. a value is None, if a
        sys_parentinventoryItemId does not exist.
        """
        contentFrames = pandas.DataFrame(content[1:], columns=content[0])
        uniqueValues = list(contentFrames[uniqueProperty])
        logger.debug(f"Unique value list: {uniqueValues[:4]}...")

        if uniqueProperty == 'sys_inventoryItemId':
            return {item: item for item in uniqueValues}

        where = f'{uniqueProperty} in {uniqueValues}'
        df = dynamicObjects.items(
            inventoryName,
            fields=[uniqueProperty, 'sys_inventoryItemId'],
            where=where
        )
        if (df is None or df.empty):
            raise Exception(f"Reference field '{uniqueProperty}' not found in inventory '{inventoryName}'")
        
        logger.debug(f"Dataframe for mapping: {df.head()}")

        if not df.empty:
            mapping = {item[1][uniqueProperty]: item[1]
                       ['sys_inventoryItemId'] for item in df.iterrows()}
            remainingUniqueValues = list(
                set(uniqueValues).difference(set(df[uniqueProperty])))
            logger.debug(
                f"Remaining unqique values: {remainingUniqueValues[:4]}...")
            if len(remainingUniqueValues) > 0:
                for item in remainingUniqueValues:
                    mapping.setdefault(item, None)
        else:
            mapping = {item: None for item in uniqueValues}

        logger.debug(f"Parent mapping: {mapping}")

        return mapping
