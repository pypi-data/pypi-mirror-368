import pytz
from tzlocal import get_localzone_name


class TimeZoneUtil:
    @staticmethod
    def get_time_zone(time_zone):
        """
        Returns the timezone string based on the input.

        If the input is None or 'local', it attempts to get the local timezone.
        If the local timezone cannot be determined, it falls back to the default local timezone.
        Otherwise, it returns the timezone string for the given timezone.

        Args:
            timeZone (str): The timezone to be converted to a string. If None or 'local', the local timezone is used.

        Returns:
            str: The string representation of the timezone.
        """
        
        if time_zone is None or time_zone == 'local':
            local_time_zone = get_localzone_name()
            try:
                return str(pytz.timezone(local_time_zone))
            except:
                return local_time_zone
        else:
            return str(pytz.timezone(time_zone))