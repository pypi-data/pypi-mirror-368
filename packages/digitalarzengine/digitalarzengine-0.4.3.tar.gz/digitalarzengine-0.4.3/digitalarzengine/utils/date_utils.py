
from datetime import datetime, timedelta

class DateUtils:
    @staticmethod
    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @classmethod
    def get_date_list_by_doy(cls, doy: int, start_year: int = 2001, end_year: int = 2025):
        dates = []
        for year in range(start_year, end_year + 1):
            adjusted_doy = doy
            if cls.is_leap_year(year) and doy > 59:
                adjusted_doy += 1  # add 1 to account for Feb 29
            try:
                date_obj = datetime(year, 1, 1) + timedelta(days=adjusted_doy - 1)
                dates.append(date_obj.strftime('%Y-%m-%d'))
            except ValueError:
                # In case of invalid DOY (e.g., 367)
                continue
        return dates

