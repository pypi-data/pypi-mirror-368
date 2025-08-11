"""Helper functions to work with DBAPI compliant databases and connection strings"""

from . import string_to_dict


def connection_string_to_dict(connection_string: str) -> dict:
    return string_to_dict(connection_string, ";", "=", lambda s: s.upper())


def execute(cn, sql, *args, **kwargs):
    cur = cn.cursor()
    cur.execute(sql, *args, **kwargs)
    return cur


def iter_cursor_as_dict(cur):
    columns = [column[0] for column in cur.description]
    for r in cur:
        yield dict(zip(columns, r))


def iter_cursor_sets(cur):
    "Iterate through all sets provided by a Python DB API 2.0 cursor"
    more = True
    if cur.description is not None:
        yield cur
    while more:
        more = cur.nextset()
        if cur.description is not None:
            yield cur
