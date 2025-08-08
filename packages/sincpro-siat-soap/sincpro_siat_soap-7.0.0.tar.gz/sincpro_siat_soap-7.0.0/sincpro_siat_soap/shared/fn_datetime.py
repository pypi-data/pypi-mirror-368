from datetime import datetime
from typing import Union

import pytz


def now_bolivia() -> datetime:
    now = datetime.now(pytz.UTC)
    bo = pytz.timezone("America/La_Paz")
    bolivia_now = now.astimezone(bo)
    return bolivia_now


def from_naive_utc_to_bo_datetime(utc_datetime: datetime) -> datetime:
    """
    Convert a naive UTC datetime to a Bolivia datetime
    """
    aware_utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
    bo = pytz.timezone("America/La_Paz")
    bo_datetime = aware_utc_datetime.astimezone(bo)
    return bo_datetime


def from_bolivia_tz_to_naive_utc(bo_datetime: datetime) -> datetime:
    """
    Convert a Bolivia datetime to a naive UTC datetime
    """
    utc_datetime = bo_datetime.astimezone(pytz.utc)
    return utc_datetime.replace(tzinfo=None)


def datetime_for_CUF(invoice_datetime: Union[str, datetime]) -> str:
    cuf_date_time_format = "%Y%m%d%H%M%S%f"

    if isinstance(invoice_datetime, datetime):
        return invoice_datetime.strftime(cuf_date_time_format)[:17]

    if isinstance(invoice_datetime, str):
        datetime_py_obj = datetime.fromisoformat(invoice_datetime)
        return datetime_py_obj.strftime(cuf_date_time_format)[:17]


def datetime_for_send_invoice(invoice_datetime: Union[str, datetime]) -> str:
    FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
    if isinstance(invoice_datetime, datetime):
        return invoice_datetime.strftime(FORMAT)[:23]

    if isinstance(invoice_datetime, str):
        datetime_py_obj = datetime.fromisoformat(invoice_datetime)
        return datetime_py_obj.strftime(FORMAT)[:23]
