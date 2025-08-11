import os
import math
import pyperclip
from seven2one.core_interface import ITechStack
from seven2one.dynamicobjects_interface import IDynamicObjects
from seven2one.utils.ut_error_handler import ErrorHandler
from loguru import logger
from uuid import uuid4
from collections import namedtuple
from typing import Any, Dict, Optional, Tuple
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

class GraphQLUtil:
    
    errors = f'''errors {{
                    message
                    code
                }}'''
                
    @staticmethod
    def to_graphql(value) -> str:
        """
        Escapes a value for usage in GraphQL. Surrounding " will be added automatically.

        Parameters
            value
                The value which should be escaped for GraphQL.

        Returns
            Escaped value. Includes surrounding " for strings.

        Raises
            ValueError
                If value is NaN.

        Examples:
        * string ABC becomes string "ABC"
        * string A"BC becomes string "A\\"BC"
        * string "ABC" becomes string "\\"ABC\\""
        * int 123 becomes 123
        * float 12.34 becomes 12.34
        * None becomes string null
        * True becomes string true
        * False becomes string false
        * [1, 2, 3] becomes [1, 2, 3]
        """
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            if math.isnan(value):
                raise ValueError('Value is NaN.')
            return str(value)
        if isinstance(value, list):
            escaped_list = ', '.join(GraphQLUtil.to_graphql(item) for item in value)
            return f'[{escaped_list}]'
        escaped_value = str(value).replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped_value}"'

    @staticmethod
    def graphQL_list(item_list: list) -> str:
        """Converts a list to a graphQL list"""
        
        def is_number(n):
            try:
                float(n)
            except ValueError:
                return False
            return True

        result = '['
        for item in item_list:
            if is_number(item):
                result += f'{item},'
            else:
                result += f'"{item}",'
        result += ']'
        return result

    @staticmethod
    def query_fields(field_list: list, array_type_fields: Optional[list] = None,
                     array_page_size: Optional[int] = None, filter: Optional[dict] = None,
                     recursive=False) -> str:
        """
        Transforms a Python list of fields into graphQL String of fields
        including fields of referenced inventories        
        """
        
        def nested_item(item):
            item_length = len(item)
            nonlocal fields
            line = ''
            for i in range(item_length - 1):
                itemStr = ".".join(item[:i+1])
                if array_type_fields != None and itemStr in array_type_fields:
                    if filter is not None and item[i] in filter.keys():
                        line += f'{item[i]} (pageSize: {array_page_size}, where: {filter[item[i]]}) {{ '
                    else:
                        line += f'{item[i]} (pageSize: {array_page_size}) {{ '
                else:
                    line += f'{item[i]} {{ '
            line += f'{item[-1]} '
            for _ in range(item_length - 1):
                line += '}'
            line += ' \n'
            fields += line

        fields = ''
        split_list = [item.split('.') for item in field_list]
        logger.debug(f"intermediate step - splitted list: {split_list}")

        for item in split_list:
            if len(item) == 1:
                fields += f'{item[0]}  \n'
            else:
                if not recursive:
                    if item[-1] == '_displayValue':
                        nested_item(item)
                    if item[-1] == 'sys_inventoryItemId':
                        nested_item(item)
                else:
                    nested_item(item)
        return fields

    @staticmethod
    def handle_where_dyno(tech_stack: ITechStack, dynamic_object: IDynamicObjects, where, inventory_name: Optional[str] = None) -> Optional[Tuple[str, Optional[dict]]]:
        """Handles the where argument if any"""
        top_level_filter = ''
        if where is not None:
            resolved_filter = GraphQLUtil.resolve_where_dyno(tech_stack, dynamic_object, where, inventory_name)
            logger.debug(f"Resolved filter: {resolved_filter}")
            if 'topLevel' in resolved_filter.keys():
                top_level_filter = resolved_filter['topLevel']
                if top_level_filter is None:
                    return
        else:
            top_level_filter = ''
            resolved_filter = None
        if '[]' in top_level_filter:
            ErrorHandler.error(tech_stack.config.raiseException, "Filter is not resolvable.")
            return

        return top_level_filter, resolved_filter
    
    @staticmethod
    def resolve_where_automation(tech_stack: ITechStack, filter_arg) -> dict:
        """
        Resolved where used for automation: no dynamic objects are used

        How does this work:
        A list of lists is created, where 'or terms' are the elements of the parent list and 
        'and terms' are elements of a child list of an or (or single) element.
        For each 'and' in a child list, the string will be closed with an extra '}'

        Lists (as string) are treated seperately, but work the same as a single or an 'and' element.
        """
    
        result_dict = {}

        if isinstance(filter_arg, (list, tuple)):
            where_string = GraphQLUtil.filter_part_automation(filter_arg, result_dict, filter_arg, tech_stack)
        else:
            if ' or ' in filter_arg:
                ErrorHandler.error(tech_stack.config.raiseException, f"'or' is not supported in string type filters.")
            filter_arg = filter_arg.split(' and ')
            where_string = GraphQLUtil.filter_part_automation(filter_arg, result_dict, filter_arg, tech_stack)
            result_dict.setdefault('topLevel', 'where: ' + where_string)

        if where_string:
            result_dict.setdefault('topLevel', 'where: ' + where_string)

        logger.debug(f"ResultDict: {result_dict}")
        return result_dict
    
    #TODO: Here we might check filterPart result in the recursive call case. Null values are errors and it should be handled.
    @staticmethod
    def filter_part_automation(arg, result_dict: dict, original_filter_arg, tech_stack:ITechStack) -> str:
        if isinstance(arg, str):
            return GraphQLUtil.create_filter_part_automation(arg, tech_stack)
        elif isinstance(arg, list):
            where_string = '{and: ['
            for i, sub_arg in enumerate(arg):
                where_string += GraphQLUtil.filter_part_automation(sub_arg, result_dict, original_filter_arg, tech_stack)
                if i != len(arg) - 1:
                    where_string += ', '
            where_string += ']} '
            return where_string
        elif isinstance(arg, tuple):
            where_string = '{or: ['
            for i, sub_arg in enumerate(arg):
                where_string += GraphQLUtil.filter_part_automation(sub_arg, result_dict, original_filter_arg, tech_stack)
                if i != len(arg) - 1:
                    where_string += ', '
            where_string += ']} '
            return where_string
        elif isinstance(arg, bool):
            ErrorHandler.error(tech_stack.config.raiseException, f"Wrong syntax of filter '{original_filter_arg}'.")
        return ""
    
    @staticmethod
    def create_filter_part_automation(sub_element, tech_stack:ITechStack) -> str:
            SubElement = namedtuple('SubElement', ['property', 'operator', 'search_item'])
            if '[' in sub_element:
                x = sub_element.find('[')
                sub = sub_element[:x].split(' ')
                sub_last = sub_element[x:]
                if sub_last.count('"') == 0:
                    sub_last = sub_last[1:-1].split(',')
                    sub_last = [item.lstrip() for item in sub_last]
                    sub_last = [item.replace("'", "") for item in sub_last]
                    sub_last = GraphQLUtil.graphQL_list(sub_last)
                el = SubElement(property=sub[0], operator=sub[1], search_item=sub_last)
                where_string = f'{{ {el.property}: {{ {GraphQLUtil.map_operator(el.operator)}: {el.search_item} }} }}'
                return where_string
            else:
                if sub_element.count('"') == 2:
                    x = sub_element.find('"')
                    s_item = sub_element[x:]
                    sub = GraphQLUtil.split(sub_element[:x], tech_stack)
                elif sub_element.count('"') == 0:
                    sub = GraphQLUtil.split(sub_element, tech_stack)
                    s_item = sub[2]
                else:
                    sub = None
                    s_item = None
                    ErrorHandler.error(tech_stack.config.raiseException, f"Invalid filter criteria {sub_element}")

                if sub is None:
                    raise Exception(f"Invalid filter criteria {sub_element}")

                el = SubElement(property=sub[0], operator=sub[1], search_item=s_item)
                where_string = f'{{ {el.property}: {{ {GraphQLUtil.map_operator(el.operator)}: {el.search_item} }} }}'
                return where_string


    @staticmethod
    def resolve_where_dyno(tech_stack: ITechStack, dynamic_object: IDynamicObjects, filter_arg, inventory_name:Optional[str] = None) -> dict:
        """
        How does this work:
        A list of lists is created, where 'or terms' are the elements of the parent list and 
        'and terms' are elements of a child list of an or (or single) element.
        For each 'and' in a child list, the string will be closed with an extra '}'

        Lists (as string) are treated seperately, but work the same as a single or an 'and' element.
        """

        result_dict = {}

        if isinstance(filter_arg, (list, tuple)):
            where_string = GraphQLUtil.filter_part_dyno(filter_arg, result_dict, filter_arg, dynamic_object, tech_stack, inventory_name)
        else:
            if ' or ' in filter_arg:
                ErrorHandler.error(tech_stack.config.raiseException, f"'or' is not supported in string type filters.")
            filter_arg = filter_arg.split(' and ')
            where_string =GraphQLUtil.filter_part_dyno(filter_arg, result_dict, filter_arg, dynamic_object, tech_stack, inventory_name)
            result_dict.setdefault('topLevel', 'where: ' + where_string)

        if where_string:
            result_dict.setdefault('topLevel', 'where: ' + where_string)

        logger.debug(f"ResultDict: {result_dict}")
        return result_dict
    
    @staticmethod
    def map_operator(operator):
            operators = {
                '==': 'eq',
                'eq': 'eq',
                'in': 'in',
                '<': 'lt',
                '>': 'gt',
                '<=': 'lte',
                '>=': 'gte',
                'lt': 'lt',
                'gt': 'gt',
                'lte': 'lte',
                'gte': 'gte',
                'contains': 'contains', # not available in gql schema any more
                '!=': 'neq',
                'ne': 'neq',
                'neq': 'neq',
                'nin': 'nin',
                'not in': 'nin',
                'startsWith': 'startsWith',
                'startswith': 'startsWith',
                'endsWith': 'endsWith', # not available in gql schema any more
                'endswith': 'endsWith', # not available in gql schema any more
                '=': 'eq'
            }
            if operator in operators:
                return operators[operator]
            else:
                logger.error(f"Unknown operator '{operator}'")

    @staticmethod
    def split(item_to_split: str, tech_stack:ITechStack) -> list:
        splitted = item_to_split.split(' ')
        for item in reversed(splitted):
            if item == '':
                splitted.remove(item)

        if len(splitted) > 3:
            ErrorHandler.error(tech_stack.config.raiseException, f'''Invalid filter criteria {item_to_split}. Did you miss to put the search string in double quotes ("")?''')
        return splitted
    
    @staticmethod
    def second_level_filter_dyno(el: Any, result_dict: dict, dynamic_object: IDynamicObjects, tech_stack:ITechStack, inventory_name:Optional[str] = None) -> str:
        """Builds the filter part for second level"""
        
        sub_property = el.property.split('.')[0]
        sub_filter_property = el.property.split('.')[1]
        try:
            sub_inventory = tech_stack.metaData.structure[inventory_name]['properties'][sub_property]['inventoryName']
        except:
            ErrorHandler.error(tech_stack.config.raiseException, f"Unknown property '{sub_property}' in '{el.property}'.")
            return ''

        df = dynamic_object.items(sub_inventory, fields=['sys_inventoryItemId'], where=[f'{sub_filter_property} {el.operator} {el.search_item}'])
        if df is None:
            raise Exception(f"Unknown property '{sub_filter_property}' in '{el.property}'.")

        try:
            item_ids = list(df['sys_inventoryItemId'])
        except:
            logger.warning(
                f"'{sub_filter_property} {el.operator} {el.search_item}' does not lead to a result.")
            return ''
        if len(item_ids) == 0:
            logger.error(f"{el.property} is not a valid filter criteria.")
            return ''

        sub_filter_property_is_array = tech_stack.metaData.structure[inventory_name]['properties'][sub_property]['isArray']
        if sub_filter_property_is_array:
            if len(item_ids) == 1:
                where_string = f'{{sys_inventoryItemId: {{ eq: "{item_ids[0]}" }} }}'
            else:
                item_ids = GraphQLUtil.graphQL_list(item_ids)
                where_string = f'{{sys_inventoryItemId: {{ in: {item_ids} }} }}'
        else:
            if len(item_ids) == 1:
                where_string = f'{{{sub_property}: {{sys_inventoryItemId: {{ eq: "{item_ids[0]}" }} }} }}'
            else:
                item_ids = GraphQLUtil.graphQL_list(item_ids)
                where_string = f'{{{sub_property}: {{sys_inventoryItemId: {{ in: {item_ids} }} }} }}'

        if sub_filter_property_is_array:
            result_dict.setdefault(sub_property, where_string)
            logger.warning("Test")
            ErrorHandler.error(tech_stack.config.raiseException, f"Array properties are not yet supported in filters: '{sub_property}'")
            return result_dict.setdefault(sub_property, where_string)

        else:
            return where_string
            
    @staticmethod
    def create_filter_part_dyno(sub_element, result_dict, dynamic_object: IDynamicObjects, tech_stack:ITechStack, inventory_name:Optional[str] = None) -> str:
        SubElement = namedtuple('SubElement', ['property', 'operator', 'search_item'])
        if '[' in sub_element:
            x = sub_element.find('[')
            sub = sub_element[:x].split(' ')
            sub_last = sub_element[x:]
            if sub_last.count('"') == 0:
                sub_last = sub_last[1:-1].split(',')
                sub_last = [item.lstrip() for item in sub_last]
                sub_last = [item.replace("'", "") for item in sub_last]
                sub_last = GraphQLUtil.graphQL_list(sub_last)
            el = SubElement(property=sub[0], operator=sub[1], search_item=sub_last)
            if el.property.count('.') == 1:
                where_string = GraphQLUtil.second_level_filter_dyno(el, result_dict, dynamic_object, tech_stack, inventory_name)
            else:
                where_string = f'{{ {el.property}: {{ {GraphQLUtil.map_operator(el.operator)}: {el.search_item} }} }}'
            return where_string
        else:
            if sub_element.count('"') == 2:
                x = sub_element.find('"')
                s_item = sub_element[x:]
                sub = GraphQLUtil.split(sub_element[:x], tech_stack)
            elif sub_element.count('"') == 0:
                sub = GraphQLUtil.split(sub_element, tech_stack)
                s_item = sub[2]
            else:
                sub = None
                s_item = None
                ErrorHandler.error(tech_stack.config.raiseException, f"Invalid filter criteria {sub_element}")

            if sub is None:
                raise Exception(f"Invalid filter criteria {sub_element}")

            el = SubElement(property=sub[0], operator=sub[1], search_item=s_item)
            if el.property.count('.') == 1:
                where_string = GraphQLUtil.second_level_filter_dyno(el, result_dict, dynamic_object, tech_stack, inventory_name)
            else:
                where_string = f'{{ {el.property}: {{ {GraphQLUtil.map_operator(el.operator)}: {el.search_item} }} }}'
            return where_string
        
    #TODO: Here we might check filterPart result in the recursive call case. Null values are errors and it should be handled.
    @staticmethod
    def filter_part_dyno(arg, result_dict: dict, original_filter_arg, dynamic_object: IDynamicObjects, tech_stack:ITechStack, inventory_name:Optional[str] = None) -> str:
        if isinstance(arg, str):
            return GraphQLUtil.create_filter_part_dyno(arg, result_dict, dynamic_object, tech_stack, inventory_name)
        elif isinstance(arg, list):
            where_string = '{and: ['
            for i, sub_arg in enumerate(arg):
                where_string += GraphQLUtil.filter_part_dyno(sub_arg, result_dict, original_filter_arg, dynamic_object, tech_stack, inventory_name)
                if i != len(arg) - 1:
                    where_string += ', '
            where_string += ']} '
            return where_string
        elif isinstance(arg, tuple):
            where_string = '{or: ['
            for i, sub_arg in enumerate(arg):
                where_string += GraphQLUtil.filter_part_dyno(sub_arg, result_dict, original_filter_arg, dynamic_object, tech_stack, inventory_name)
                if i != len(arg) - 1:
                    where_string += ', '
            where_string += ']} '
            return where_string
        elif isinstance(arg, bool):
            ErrorHandler.error(tech_stack.config.raiseException, f"Wrong syntax of filter '{original_filter_arg}'.")
        return ""
    
    @staticmethod
    def arguments_to_str(arguments: dict) -> str:
            """
            Converts a dictionary of arguments to a string.
            """
            if not isinstance(arguments, dict):
                raise TypeError("Arguments must be a dictionary.")

            arguments_str = '[\n'

            for key,value in arguments.items():
                arguments_str +=  f'{{name: "{key}", value: "{value}"}}\n'

            arguments_str += ']'
            
            return arguments_str 
    
    @staticmethod
    def log_gql_errors(result: dict):
        """Log errors from GraphQL Query"""
        for i in result['errors']:
            logger.error(i['message'])
            return

    @staticmethod
    def validate_result_object(result) -> dict:
        # TODO:
        # trennen in die 2 Belange: check_for_errors und ensure_dict_result
        
        # TODO: REFACTORING NECESARY: makes no sense return "result" object, 
        # root problem: method GraphQLUtil.execute_GraphQL does not have explicit return type
        # could be None, or other
        if result == None:
            raise Exception("GraphQL error: No response received.")
        elif not isinstance(result, dict):
            raise Exception(f"Unknown GraphQL response: {result}")
        if "errors" in result and result["errors"]: #TODO: try catch here, if error result schema/content modified
            GraphQLUtil.log_gql_errors(result)
            raise Exception("GraphQL returned errors.")
        else: 
            return result
    
    @staticmethod
    def execute_GraphQL(
            techStack : ITechStack,
            endpoint: str,
            graphQLString,
            correlationId: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None):
        """Executes GraphQl, this code is used in every main function"""

        cid = correlationId or str(uuid4())
        context_logger = logger.bind(correlationId=str(cid))

        GraphQLUtil.copyGraphQLString(graphQLString, techStack.config.defaults.copyGraphQLString)
        context_logger.trace(f"GraphQLString: {graphQLString}")
        try:
            query = gql(graphQLString)
        except Exception as err:
            if techStack.config.raiseException:
                raise Exception(err)
            else:
                context_logger.error(err)
                return

        try:
            headers = {
                'Authorization': 'Bearer ' + techStack.get_access_token(),
                'X-Correlation-Id': cid,
            }
            transport = RequestsHTTPTransport(url=endpoint, headers=headers, verify=True, proxies=techStack.config.proxies)
            with Client(transport=transport, fetch_schema_from_transport=False) as session:
                result = session.execute(query, variable_values=params)
        except Exception as err:
            if techStack.config.raiseException:
                raise Exception(err)
            else:
                context_logger.error(err)
                return

        return result


    @staticmethod
    def copyGraphQLString(graphQLString: str, copyGraphQLString: bool = False) -> None:
        """Can be applied to any core function to get the GraphQL string which is stored in the clipboard"""
        if copyGraphQLString == True and os.name == 'nt':
            return pyperclip.copy(graphQLString)


    @staticmethod
    def list_graphQl_errors(result: dict, key: str) -> None:
        """Print errors from GraphQL Query to log"""

        for i in result[key]['errors']:
            logger.error(i['message'])
            
    
    @staticmethod
    def uniqueness_to_string(property_uniqueness: list):
        """
        Converts a list of unique keys into a string
        """

        _uniqueKeys = '[\n'
        for item in property_uniqueness:
            key = item['uniqueKey']
            _uniqueKeys += f'{{uniqueKey: "{key}" properties: ['
            for value in item['properties']:
                _uniqueKeys += f'"{value}",'

            _uniqueKeys += ']}\n'
        _uniqueKeys += ']'
        return _uniqueKeys


    @staticmethod
    def array_items_to_string(arrayItems: list, operation: str, cascadeDelete: bool) -> Optional[str]:
        """Converts a list of array items to a graphQL string"""

        cDelValue = 'true' if cascadeDelete == True else 'false'

        if operation == 'insert':
            _arrayItems = 'insert: [\n'
            for item in arrayItems:
                _arrayItems += f'{{value: "{item}"}}\n'
            _arrayItems += ']'
            return _arrayItems
        if operation == 'removeByIndex':
            _arrayItems = f'cascadeDelete: {cDelValue}\n'
            _arrayItems += 'removeByIndex: ['
            for item in arrayItems:
                _arrayItems += f'{item}, '
            _arrayItems += ']'
            return _arrayItems
        if operation == 'removeById':
            _arrayItems = f'cascadeDelete: {cDelValue}\n'
            _arrayItems += 'removeById: ['
            for item in arrayItems:
                _arrayItems += f'"{item}", '
            _arrayItems += ']'
            return _arrayItems
        if operation == 'removeAll':
            _arrayItems = f'cascadeDelete: {cDelValue}\n'
            _arrayItems += 'removeByIndex: ['
            for item in arrayItems:
                _arrayItems += f'{item}, '
            _arrayItems += ']'
            return _arrayItems
                
    @staticmethod
    def get_service_version(techStack: ITechStack, endpoint: str, service: str):
        """
        Returns name and version of the responsible micro service
        """

        key = f'{service}ServiceInfo'
        graphQLString = f'''query version {{ 
            {key} {{
                name
                informationalVersion
            }}
        }}'''
        result = GraphQLUtil.execute_GraphQL(techStack, endpoint, graphQLString)
        if (result == None or (not isinstance(result, dict))):
            raise Exception("Could not get version information.")
        
        return f'{result[key]["name"]}: {result[key]["informationalVersion"]}'

    
    @staticmethod
    def arg_none(arg, value, enum=False) -> str:
        """
        Creates a simple string (to be embedded in graphQlString) 
        for arguments that are None by default.
        """
        if value == None:
            return ''
        else:
            if enum == True:
                return f'{arg}: {value}'
            else:
                if type(value) == str:
                    return f'{arg}: "{value}"'
                elif type(value) == float:
                    return f'{arg}: {value}'
                elif type(value) == int:
                    return f'{arg}: {value}'
                elif type(value) == bool:
                    if value == True:
                        return f'{arg}: true'
                    else:
                        return f'{arg}: false'
                else:
                    return f'{arg}: "{str(value)}"'
