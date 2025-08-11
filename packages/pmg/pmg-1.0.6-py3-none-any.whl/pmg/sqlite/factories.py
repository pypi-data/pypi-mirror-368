import collections
import functools


@functools.lru_cache(maxsize=64)
def make_namedtuple(cur_desc):
    return collections.namedtuple("Row", [col[0] for col in cur_desc])


def namedtuple_factory(cursor, row):
    """Returns sqlite rows as named tuples."""
    Row = make_namedtuple(cursor.description)
    return Row(*row)


def dict_factory(cursor, row):
    return dict(zip([col[0] for col in cursor.description], row))
