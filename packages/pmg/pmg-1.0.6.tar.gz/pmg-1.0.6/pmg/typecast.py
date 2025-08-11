import builtins
import datetime
import decimal
import math
import numbers

import pmg


class UnboxException(Exception):
    pass


def unbox_bool(value):
    if value is None:
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, (numbers.Number, decimal.Decimal)):
        return False if value == 0 else True
    if isinstance(value, str):
        return False if value.upper() in ["0", "FALSE", "N", ""] else True
    raise UnboxException(
        f"Cannot unbox value '{value}' from type {type(value)} to bool."
    )


def unbox_date(value):
    if value is None:
        return value
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        # Expect ISO-formatted date string
        return datetime.date(int(value[:4]), int(value[5:7]), int(value[8:10]))
    raise UnboxException(
        f"Cannot unbox value '{value}' from type {type(value)} to date."
    )


def unbox_datetime(value):
    if value is None:
        return value
    if isinstance(value, datetime.date):  # Date is a superclass for datetime
        return value
    if isinstance(value, str):
        # Expect ISO-formatted date string
        return pmg.parse_iso_datetime_utc(value).replace(tzinfo=None)
    raise UnboxException(
        f"Cannot unbox value '{value}' from type {type(value)} to datetime."
    )


def unbox_int(value):
    if value is None:
        return value
    if isinstance(value, numbers.Integral):
        return value
    if isinstance(value, (numbers.Real, decimal.Decimal)):
        return int(value)
    if isinstance(value, str):
        return int(float(value)) if "." in value else int(value)
    raise UnboxException(
        f"Cannot unbox value '{value}' from type {type(value)} to int."
    )


def unbox_float(value):
    if value is None or math.isnan(value):
        return None
    if isinstance(value, numbers.Integral):
        return float(value)
    if isinstance(value, (numbers.Real, decimal.Decimal)):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise UnboxException(
        f"Cannot unbox value '{value}' from type {type(value)} to float."
    )


def unbox_decimal(value):
    if value is None:
        return value
    if isinstance(value, decimal.Decimal):
        return value
    if isinstance(value, (numbers.Real, numbers.Integral, str)):
        return decimal.Decimal(value)
    raise UnboxException(
        f"Cannot unbox value '{value}' from type {type(value)} to decimal."
    )


def unbox_str(value):
    if value is None:
        return value
    if isinstance(value, str):
        return value
    raise UnboxException(
        f"Cannot unbox value '{value}' from type {type(value)} to str."
    )


FUNCTIONS = {
    "bool": unbox_bool,
    "float": unbox_float,
    "int": unbox_int,
    "Decimal": unbox_decimal,
    "date": unbox_date,
    "datetime": unbox_datetime,
    "str": unbox_str,
}


def box(o):
    try:
        # TODO: NaN values
        if isinstance(o, decimal.Decimal):
            return format(o, "f")
        if isinstance(o, (datetime.date, datetime.time)):
            return o.isoformat()
        return o
    except Exception as ex:
        return f"<Unencodable type {builtins.type(o)} ({type(ex)})>"


def unbox(value, ty):
    return FUNCTIONS[ty](value)
