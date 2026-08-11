# hospApp/utils.py

import pytz
from datetime import datetime, time

IST = pytz.timezone('Asia/Kolkata')

def get_ist_range(from_date, to_date):
    """
    Converts date range to IST-aware datetime range.
    12:00 AM IST on from_date  →  11:59 PM IST on to_date
    This correctly handles UTC storage in SQL Server.
    """
    start = IST.localize(datetime.combine(from_date, time.min))  # 00:00 IST
    end   = IST.localize(datetime.combine(to_date,   time.max))  # 23:59:59 IST
    return start, end


def filter_by_date_range(queryset, date_field, from_date, to_date):
    """
    Filter queryset by IST date range on any datetime field.
    Works correctly with SQL Server UTC storage.
    """
    start, end = get_ist_range(from_date, to_date)
    return queryset.filter(**{
        f"{date_field}__range": [start, end]
    })