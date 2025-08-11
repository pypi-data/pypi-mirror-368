from typing import Optional, Union
from seven2one.core_interface import ITechStack
from seven2one.utils.ut_error_handler import ErrorHandler


class OrderUtil():
    
    @staticmethod
    def order_items(techStack: ITechStack, orderBy: Union[dict, list, str, None], asc: Union[list, str, bool, None] = None) -> Optional[str]:
        def _orderDictToString(orderBy: dict) -> Optional[str]:
            order = 'order: ['
            for key, value in orderBy.items():
                if value not in ['ASC', 'DESC']:
                    ErrorHandler.error(techStack.config.raiseException, f"Invalid value '{value}' for property '{key}'. Use 'ASC' or 'DESC' instead.")
                    return
                order += f'{{{key}: {value}}}'
            order += ']'
            return order

        mapping = {False: 'DESC', True: 'ASC', None: 'ASC'}
        order = None
        if orderBy != None:
            _orderBy = {}
            if type(orderBy) == dict:
                order = _orderDictToString(orderBy)
            if type(orderBy) == list:
                if type(asc) == bool:
                    _orderBy = {property: mapping[asc] for property in orderBy}
                elif type(asc) == list:
                    _asc = [mapping[item] for item in asc]
                    _orderBy = dict(zip(orderBy, _asc))
                elif asc == None:
                    _orderBy = {property: 'ASC' for property in orderBy}
                else:
                    ErrorHandler.error(techStack.config.raiseException, f"Invalid type '{asc}' for order direction. Use bool or list of bools.")
                order = _orderDictToString(_orderBy)
            if type(orderBy) == str:
                if type(asc) == bool:
                    _orderBy = {orderBy: mapping[asc]}
                elif type(asc) == list:
                    _orderBy = {orderBy: mapping[asc[0]]}
                elif asc == None:
                    _orderBy = {orderBy: 'ASC'}
                else:
                    ErrorHandler.error(techStack.config.raiseException, f"Invalid type '{asc}' for order direction. Use bool instead.")
                order = _orderDictToString(_orderBy)
        else:
            order = ''

        return order