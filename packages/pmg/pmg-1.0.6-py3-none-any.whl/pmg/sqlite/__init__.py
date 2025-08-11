import decimal
import inspect
import logging
import sqlite3

import pmg

from . import factories

DEFAULT_PRAGMAS = {"temp_store": 2, "foreign_keys": 1}

namedtuple_factory = factories.namedtuple_factory
log = logging.getLogger(__name__)


def open_db(path=None, pragmas=None, read_only=False, timeout=10, **kwargs):
    cn = None
    path = pmg.coalesce(path, ":memory:")
    if read_only:
        cn = sqlite3.connect(f"file:{path}?mode=ro", timeout=timeout, **kwargs)
    else:
        cn = sqlite3.connect(path, timeout=timeout, **kwargs)
        if pragmas and "mode=ro" not in path:
            cur = cn.cursor()
            for k, v in pragmas.items():
                cur.execute(f'pragma {k}="{v}";')
            cn.commit()
    return cn


def open_db_ro(path, timeout=10, **kwargs):
    return open_db(path, read_only=True, timeout=timeout, **kwargs)


def adapt_decimal(d):
    return str(d)


def backup_progress(status, remaining, total):
    log.debug(
        "SQLite backup copied %d of %d pages [status: %s].",
        total - remaining,
        total,
        status,
    )


def backup(target_path: str, source_db, pages=-1):
    with open_db(target_path) as dbTarget:
        source_db.backup(dbTarget, pages=pages, progress=backup_progress)
        dbTarget.commit()


def add_functions(cn, *functions):
    for func in functions:
        cn.create_function(func.__name__, len(inspect.getfullargspec(func)[0]), func)


sqlite3.register_adapter(decimal.Decimal, adapt_decimal)
