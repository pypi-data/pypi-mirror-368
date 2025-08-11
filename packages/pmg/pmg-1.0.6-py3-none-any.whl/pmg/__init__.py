import builtins
import collections
import collections.abc
import csv
import datetime
import decimal
import fnmatch
import functools
import hashlib
import itertools
import json
import logging
import numbers
import os
import random
import re
import socket
import sys
import time
import traceback
import typing
import uuid
import zoneinfo

# Configuration helpers


def get_config(key, default_value=None):
    if default_value is None:
        assert (
            f"PMG_{key}" in os.environ
        ), f"Configuration key {key} (environment variable PMG_{key}) not found."
    return os.environ.get(f"PMG_{key}", default_value)


def get_config_keys(pattern):
    return {
        k[4:]: v
        for k, v in os.environ.items()
        if k.startswith("PMG_") and fnmatch.fnmatch(k[4:], pattern)
    }


# Global configuration variables

ASCII_SUB = "\x1a"
DEFAULT_CSV_DELIMITER = "\t"
DEFAULT_HASH_ALGO = hashlib.sha1
TRACE_LOG = get_config("TRACE_LOG", "0") == "1"

# Object Helpers


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def coalesce(*arg):
    for el in arg:
        if el is not None:
            return el
    return None


# ID Helpers


def newid():
    return str(uuid.uuid4())


def newrunid():
    return f"{utcnow().strftime('%y%m%d%H%M%S%f')}{''.join([random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ') for i in range(4)])}"


# Collection Helpers


def empty(obj):
    return obj is None or len(obj) == 0


def blank(obj):
    return obj is None or str(obj).strip() == ""


def allblank(obj):
    return all(map(blank, obj))


# Formatting helpers


def to_sql(obj):
    if obj is None:
        return "NULL"
    if isinstance(obj, str):
        return "'{}'".format(obj.replace("'", "''"))
    if isinstance(obj, bool):
        return "1" if obj else "0"
    # datetime.datetime inherits from datetime.date and will be caught
    if isinstance(obj, (datetime.date, datetime.time)):
        return f"'{obj.isoformat()}'"
    if isinstance(obj, numbers.Real):
        return str(obj)
    assert False, "We should not be here."


def to_csv(
    obj,
    delim="\t",
    delim_sub: str = None,
    float_decimals: int = 10,
    bool_true_value: str = None,
    bool_false_value: str = None,
):
    s = ""
    delim_sub = coalesce(delim_sub, ASCII_SUB)
    bool_true_value = coalesce(bool_true_value, "1")
    bool_false_value = coalesce(bool_false_value, "0")
    if obj is not None:
        # datetime.datetime inherits from datetime.date and will be caught
        if isinstance(obj, (datetime.date, datetime.time)):
            return obj.isoformat()
        if isinstance(obj, numbers.Real):
            s = str(round(obj, float_decimals))
        elif isinstance(obj, bool):
            s = bool_true_value if obj else bool_false_value
        else:
            s = str(obj)
    assert (
        delim_sub not in s
    ), "Cannot safely serialize data that contains ASCII_SUB character"
    return s.replace(delim, delim_sub)


def to_namedtuple(dictionary: dict, tuple_name: str = None):
    return collections.namedtuple(tuple_name or "Record", dictionary.keys())(
        **dictionary
    )


def make_iterable(obj):
    if isinstance(obj, str) or not isinstance(obj, collections.abc.Iterable):
        return [obj]
    return obj


# File Helpers

if os.name != "nt":
    import grp
    import pwd


def touch(fname, mode=0o666, dir_fd=None, **kwargs):
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(
            f.fileno() if os.utime in os.supports_fd else fname,
            dir_fd=None if os.supports_fd else dir_fd,
            **kwargs,
        )


def chownmod(path, owner=None, group=None, perms=None):
    assert os.name != "nt", "chownmod() is not available in Windows, sadly."
    if owner is not None or group is not None:
        uid = pwd.getpwnam(owner).pw_uid if owner is not None else -1
        gid = grp.getgrnam(group).gr_gid if group is not None else -1
        os.chown(path, uid, gid)
    if perms is not None:
        os.chmod(path, perms)


def getfiles(path):
    for root, _, files in os.walk(path):
        for fn in files:
            yield os.path.join(root, fn)


def iterfiles(path):
    for fn in os.listdir(path):
        fullpath = os.path.join(path, fn)
        if os.path.isdir(fullpath):
            continue
        yield fullpath


def iterdirs(path):
    for fn in os.listdir(path):
        fullpath = os.path.join(path, fn)
        if not os.path.isdir(fullpath):
            continue
        yield fullpath


def hashfile(path, hash_algo=None):
    h = coalesce(hash_algo, DEFAULT_HASH_ALGO())
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def writetextfile(path, content):
    with open(path, "wt", encoding="utf-8", newline="") as g:
        g.write(content)


# String Helpers


def mass_replace(s, replace_vars):
    if s is None:
        return s
    if not isinstance(replace_vars, dict):
        raise Exception("replace_vars must be a dict.")
    for v in replace_vars.keys():
        s = s.replace(v, replace_vars[v])
    return s


def string_to_dict(
    records_string: str,
    record_delim: str = ",",
    pair_delim: str = "=",
    key_processing_function: typing.Callable = None,
) -> dict:
    return {
        coalesce(key_processing_function, identity)(kvp[0]): kvp[1]
        for kvp in (kvp.split(pair_delim) for kvp in records_string.split(record_delim))
    }


def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix) :]


def remove_suffix(text, suffix):
    return text[-(text.endswith(suffix) and len(suffix)) :]


def maxlen(obj, max_len, ellipsis=None):
    if len(obj) <= max_len:
        return obj
    if ellipsis is None:
        return obj[:max_len]
    return f"{obj[:max_len]}{ellipsis}"


def hide_str_excess(text, max_len):
    return maxlen(text, max_len, "...")


def hashstr(s, hash_algo=None):
    h = coalesce(hash_algo, DEFAULT_HASH_ALGO())
    if isinstance(s, bytes):
        h.update(s)
    else:
        h.update(s.encode("utf-8"))
    return h.hexdigest()


def camel_case_split(identifier):
    matches = re.finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier
    )
    return [m.group(0) for m in matches]


def quote(s, quote_char):
    assert (
        quote_char not in s
    ), f"String '{s}' already contains quote ({quote_char}), escaping is needed."
    return f"{quote_char}{s}{quote_char}"


def unquote(s, quote_char):
    if (
        len(s) >= 2 * len(quote_char)
        and s[: len(quote_char)] == quote_char
        and s[-len(quote_char) :] == quote_char
    ):
        return s[len(quote_char) : -len(quote_char)]
    return s


def strif(cond, s):
    return s if cond else ""


# Date/Time Helpers


def timezone(tz_name):
    return zoneinfo.ZoneInfo(tz_name)


def today(date_format: str = None) -> str:
    """Return today's date as an ISO formatted string or with the provided format."""
    if date_format is None:
        return datetime.datetime.today().date().isoformat()
    return datetime.datetime.today().date().strftime(date_format)


def now(date_format: str = None, tz_name: str = None) -> str:
    dt = None
    if tz_name is None:
        dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.now(timezone(tz_name))
    if date_format is None:
        return dt.isoformat()
    return dt.strftime(date_format)


def utcnow():
    if sys.version_info >= (3, 10):
        return datetime.datetime.now(datetime.UTC)
    return datetime.datetime.now(datetime.timezone.utc).replace(
        tzinfo=datetime.timezone.utc
    )


def localnow(tz_name):
    return datetime.datetime.now(tz=timezone(tz_name))


def is_datetime_naive(dt):
    return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None


def is_datetime_utc(dt):
    return not is_datetime_naive(dt) and (
        dt.tzinfo == datetime.timezone.utc
        or dt.tzinfo.utcoffset(dt).total_seconds() == 0
    )


def make_datetime_naive(dt):
    return datetime.datetime(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond
    )


def parse_iso_date(dt):
    return datetime.date(int(dt[:4]), int(dt[5:7]), int(dt[8:]))


def parse_iso_datetime(dt):
    assert (
        dt[4] == "-"
        and dt[7] == "-"
        and (dt[10] == "T" or dt[10] == " ")
        and dt[13] == ":"
        and dt[16] == ":"
    ), "Unexpected ISO date/time format"
    if dt[-6] in "+-":
        dt = dt[:-6]
    if len(dt) > 19 and dt[19] == ".":
        return datetime.datetime(
            int(dt[0:4]),
            int(dt[5:7]),
            int(dt[8:10]),
            int(dt[11:13]),
            int(dt[14:16]),
            int(dt[17:19]),
            int(dt[20:]),
        )
    return datetime.datetime(
        int(dt[0:4]),
        int(dt[5:7]),
        int(dt[8:10]),
        int(dt[11:13]),
        int(dt[14:16]),
        int(dt[17:19]),
    )


def parse_iso_datetime_utc(dt):
    assert (
        dt[4] == "-"
        and dt[7] == "-"
        and (dt[10] == "T" or dt[10] == " ")
        and dt[13] == ":"
        and dt[16] == ":"
    ), "Unexpected ISO date/time format"
    if dt[-6] in "+-":
        assert dt[-5:] == "00:00", "Timezone must be UTC / offset 0:00"
        dt = dt[:-6]
    if len(dt) > 19 and dt[19] == ".":
        return datetime.datetime(
            int(dt[0:4]),
            int(dt[5:7]),
            int(dt[8:10]),
            int(dt[11:13]),
            int(dt[14:16]),
            int(dt[17:19]),
            int(dt[20:]),
            tzinfo=datetime.timezone.utc,
        )
    return datetime.datetime(
        int(dt[0:4]),
        int(dt[5:7]),
        int(dt[8:10]),
        int(dt[11:13]),
        int(dt[14:16]),
        int(dt[17:19]),
        tzinfo=datetime.timezone.utc,
    )


def get_next_weekday(weekday, from_date=None):
    """Get the next date of a particular weekday from the from_date (default: today).
    from_date is included as a valid return date (e.g., if you ask for the next Monday and today is Monday,
    you get today's date. If you dislike this, give from_date as tomorrow.)
    """
    if isinstance(from_date, datetime.datetime):
        from_date = from_date.date()
    else:
        from_date = coalesce(from_date, datetime.datetime.now().date())
    return from_date + datetime.timedelta((weekday - from_date.weekday()) % 7)


def get_seconds_until(target_dt, from_dt=None):
    return (target_dt - coalesce(from_dt, utcnow())).total_seconds()


# System Helpers


def get_exc_info():
    return "\n".join(traceback.format_exception(*sys.exc_info()))


# CSV Helpers
def csv_to_namedtuples(path, record_type: type = None, **kwargs):
    Record = None
    record_type = coalesce(record_type, collections.namedtuple)
    if "delimiter" not in kwargs:
        kwargs.update({"delimiter": DEFAULT_CSV_DELIMITER})
    with open(path, "rt") as f:
        reader = csv.reader(f, **kwargs)
        for i, r in enumerate(reader):
            if i == 0:
                Record = record_type("Record", r)
                continue
            yield Record(*r)


# JSON Helpers


class FriendlyJsonEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if isinstance(o, decimal.Decimal):
                return format(o, "f")
            if isinstance(o, (datetime.date, datetime.time)):
                return o.isoformat()
            if isinstance(o, bytes):
                try:
                    return o.decode("utf-8")
                except UnicodeError:
                    return f"<Binary ({len(o)} bytes)>"
            if isinstance(o, set):
                return tuple(o)
            return super(FriendlyJsonEncoder, self).default(o)
        except Exception as ex:
            return f"<Unencodable type {builtins.type(o)} ({type(ex)})>"


def to_json(obj, **kwargs):
    return json.dumps(obj, cls=FriendlyJsonEncoder, **kwargs)


def pretty_json(js):
    return json.dumps(js, indent=4)


# Logging Helpers

LOG_CONTEXT = {"host": socket.gethostname()}


class JsonFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record):
        super().format(record)
        js = {}
        for k, v in record.__dict__.items():
            if (
                k
                not in "msg args levelno filename exc_info created msecs relativeCreated thread threadName processName process"
            ):
                if v:
                    js[k] = v
            js["created"] = datetime.datetime.fromtimestamp(record.created)
            js.update(LOG_CONTEXT)
        return json.dumps(js, cls=FriendlyJsonEncoder)


def configure_logging():
    handler = logging.StreamHandler()
    formatter = JsonFormatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(os.environ.get("PMG_LOGLEVEL", "INFO"))
    root.addHandler(handler)


def logwrap(logger, swallow_exception=False):
    def innerlogwrap(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            correlation_id = newid()
            start_time = time.process_time()
            LOG_CONTEXT["correlation_id"] = correlation_id
            if TRACE_LOG:
                logger.debug(
                    f"> Begin function {func.__name__}()",
                    extra={"function": {"name": func.__name__, "args": args, **kwargs}},
                )
            try:
                res = func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Exception in function {func.__name__}()",
                    extra={"function": {"name": func.__name__, "args": args, **kwargs}},
                    exc_info=e,
                )
                if not swallow_exception:
                    raise
            if TRACE_LOG:
                logger.debug(
                    f"> End function {func.__name__}() after {time.process_time() - start_time:,.3f} seconds"
                )
            return res

        return wrapper

    return innerlogwrap


def is_weekend(dt):
    return dt.weekday() in [5, 6]


def identity(s):
    assert s == s, "Invalid value for identity function"
    return s


def skip(iterable, entries_to_skip):
    return itertools.islice(iterable, entries_to_skip, None)


class UserError(Exception):
    pass
