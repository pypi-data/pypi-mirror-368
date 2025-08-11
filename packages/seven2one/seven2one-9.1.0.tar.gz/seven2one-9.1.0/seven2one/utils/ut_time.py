from re import match
from datetime import datetime
from typing import Optional
import pytz
import pandas as pd

class TimeUtils():

    @staticmethod
    def _inputTimestamp(timestamp, timeZone):
        
        if type(timestamp) == datetime:
            timestamp = pytz.timezone(timeZone).localize(timestamp).isoformat()
        elif type(timestamp) == pd.Timestamp:
            timestamp = pytz.timezone(timeZone).localize(timestamp).isoformat()
        elif type(timestamp) == str:
            dateFormat = TimeUtils._dateFormat(timestamp)
            if dateFormat == None:
                raise Exception(f"Unsupported date format in timestamp: '{timestamp}'")
            if "%z" in dateFormat:
                timestamp = datetime.strptime(timestamp, dateFormat)
                timestamp = timestamp.astimezone(pytz.timezone(timeZone)).isoformat()
            else:
                timestamp = datetime.strptime(timestamp, dateFormat)
                timestamp = pytz.timezone(timeZone).localize(timestamp).isoformat()
                #if we need to specify dst time, while not having an offset, then we need another way to determine DST!
        return timestamp

    @staticmethod
    def _dateFormat(timestamp: str) -> Optional[str]:

        # German
        if match(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}.\d{1,6} [-+]\d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M:%S.%f %z'
        if match(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2} [-+]\d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M:%S %z'
        if match(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%d.%m.%Y %H:%M:%S.%f'
        if match(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M:%S'
        if match(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M'
        if match(r'\d{2}\.\d{2}\.\d{4}', timestamp):
            return '%d.%m.%Y'

        # ISO
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}[-+]\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f%z'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[-+]\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S%z'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f%z'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', timestamp):
            return '%Y-%m-%dT%H:%M:%S%z'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M'

        # English I
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,6} [-+]\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S.%f %z'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [-+]\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S %z'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y-%m-%d %H:%M:%S.%f'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M'
        if match(r'\d{4}-\d{2}-\d{2}', timestamp):
            return '%Y-%m-%d'

        # English II
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}.\d{1,6} [-+]\d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M:%S.%f %z'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} [-+]\d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M:%S %z'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y/%m/%d %H:%M:%S.%f'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M:%S'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M'
        if match(r'\d{4}/\d{2}/\d{2}', timestamp):
            return '%Y/%m/%d'

        # English III
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2} [-+]\d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M:%S %z'
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2} [-+]\d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M %z'
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M:%S'
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M'
        if match(r'\d{1,2}/\d{1,2}/\d{4}', timestamp):
            return '%m/%d/%Y'

        return None
