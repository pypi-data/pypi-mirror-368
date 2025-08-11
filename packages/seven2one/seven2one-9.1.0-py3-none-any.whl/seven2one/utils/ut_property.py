from typing import Optional, Union
from seven2one.utils.ut_graphql import GraphQLUtil
from loguru import logger


class PropertyUtil:
    @staticmethod
    def properties_to_string(properties: Union[list, dict]) -> Optional[str]:
        """ Converts a list of property dicts for many items into a string """
           
        if isinstance(properties, list):
            _properties = '[\n'
            for property in properties:
                _properties += '{\n'
                for key, value in property.items():
                    _properties += PropertyUtil.custom_properties(key, value)
                _properties += '}\n'
            _properties += ']'
            return _properties
        if isinstance(properties, dict):
            _properties = '{\n'
            for key, value in properties.items():
                _properties += PropertyUtil.custom_properties(key, value)
            _properties += '}\n'
            return _properties
        else:
            logger.error("Type of property items has to be either list or dict.")
            return

    @staticmethod
    def ts_properties_to_string(properties: list) -> Optional[str]:
        """ Converts a list of property dicts for many items into a string """
        
        time_unit, factor = 'timeUnit', 'factor'
        _properties = '[\n'
        for property in properties:
            _properties += '{\n'
            for key, value in property.items():
                if key == 'resolution':
                    try:
                        _properties += f'{key}: {{\n'
                        _properties += f'timeUnit: {value[time_unit]}\n'
                        _properties += f'factor: {value[factor]}\n'
                        _properties += f'}}\n'
                    except KeyError:
                        logger.error("Missing 'timeUnit' and/or 'factor' for Timeseries resolution")
                        return
                else:
                    _properties += PropertyUtil.custom_properties(key, value)
            _properties += '}\n'
        _properties += ']'
        return _properties

    @staticmethod
    def add_to_group_properties_to_string(group_item_id: str, properties: list) -> str:
        """ Converts a list of property dicts for many items into a string """
        
        _properties = '[\n'
        for property in properties:
            _properties += f'{{sys_groupInventoryItemId: "{group_item_id}"\n'
            for key, value in property.items():
                _properties += PropertyUtil.custom_properties(key, value)
            _properties += '}\n'
        _properties += ']'
        return _properties

    @staticmethod
    def uniqueness_to_string(property_uniqueness: list):
        """ Converts a list of unique keys into a string """
        
        _unique_keys = '[\n'
        for item in property_uniqueness:
            key = item['uniqueKey']
            _unique_keys += f'{{uniqueKey: "{key}" properties: ['
            for value in item['properties']:
                _unique_keys += f'"{value}",'
            _unique_keys += ']}\n'
        _unique_keys += ']'
        return _unique_keys

    @staticmethod
    def custom_properties(key: str, value: object) -> str:
        """ Used internally (in Utils) as helper function """
        
        if key == 'dataType':
            return f'{key}: {value}\n'
        return f'{key}: {GraphQLUtil.to_graphql(value)}\n'

    @staticmethod
    def properties(scheme, inventory_name: str, recursive: bool = True, sys_properties: bool = False, max_recursion_depth: int = 2) -> dict:
        """
        Creates a nested (or unnested) dict with properties and array 
        type fields for further usage out of the scheme
        """

        array_type_fields = []

        def combineWithDot(left:str, right:str) -> str:
            if left is not None and left != '':
                return left + '.' + right
            return right
    
        def get_inventory_object(scheme, inventory_name):
            for item in scheme['__schema']['types']:
                if item is not None and item['name'] == inventory_name:
                    return item['fields']

        def create_dict(inv, itemPath, dictionary, current_recursion_level=0):
            inventory_object = get_inventory_object(scheme, inv)
            if inventory_object is None:
                raise Exception(f"Inventory '{inv}' not found in scheme.")

            for item in inventory_object:
                itemName = item['name']
                itemTypeName = item['type']['name']
                itemKind = item['type']['kind']
                currentItemPath = combineWithDot(itemPath, itemName)
                if not sys_properties:
                    if itemName.startswith('sys_'):
                        if itemName == 'sys_inventoryItemId':
                            pass
                        else:
                            continue
                if itemKind == 'SCALAR':
                    dictionary.setdefault(itemName, itemTypeName)
                elif itemKind == 'LIST':
                    if itemName == 'sys_permissions':
                        pass
                    elif item['type']['ofType']['kind'] == 'OBJECT':
                        array_type_fields.append(currentItemPath)
                        if recursive == False or current_recursion_level > max_recursion_depth:
                            dictionary.setdefault(itemName, itemTypeName)
                        else:
                            dictionary.setdefault(itemName, create_dict(
                                item['type']['ofType']['name'], currentItemPath, {}, current_recursion_level + 1))
                    else:
                        dictionary.setdefault(itemName, itemTypeName)
                elif itemKind == 'OBJECT':
                    if recursive == False or current_recursion_level > max_recursion_depth:
                        dictionary.setdefault(itemName, itemTypeName)
                    else:
                        dictionary.setdefault(itemName, create_dict(
                            itemTypeName, currentItemPath, {}, current_recursion_level + 1))

            return dictionary

        properties = create_dict(inventory_name, "", {})
        
        property_dict = {
            'properties': properties, 
            'arrayTypeFields': array_type_fields
        }

        logger.debug(f"returned property dict: {property_dict}")

        return property_dict

    @staticmethod
    def property_list(property_dict: dict, recursive: bool = False) -> list:
        """Creates a flat list of properties"""
        
        def flatten_dict(d, path=''):
            new_path = '' if path == '' else f'{path}.'
            result = []
            for k, v in d.items():
                if isinstance(v, dict):
                    if recursive:
                        result.extend(flatten_dict(v, f'{new_path}{k}'))
                    else:
                        result.append(f'{new_path}{k}._displayValue' if '_displayValue' in v else f'{new_path}{k}.sys_inventoryItemId')
                else:
                    result.append(f'{new_path}{k}')
            return result

        property_list = flatten_dict(property_dict)
        logger.debug(f'returned property list: {property_list}')
        return property_list

    @staticmethod
    def property_types(property_dict: dict) -> dict:
        """Uses _properties() o create a flat dictionary of properties"""
        
        property_types = {}

        def inst_dict(sub_dict, path):
            for k, v in sub_dict.items():
                if isinstance(v, dict):
                    path = f'{path}.{k}'
                    inst_dict(sub_dict[k], path)
                else:
                    property_types.setdefault(f'{path}.{k}', v)

        for k, v in property_dict.items():
            if isinstance(v, dict):
                inst_dict(property_dict[k], k)
            else:
                property_types.setdefault(k, v)

        logger.debug(f"returned property types: {property_types}")
        return property_types