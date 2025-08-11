import random
import sqlite3
import sys

import hypothesis.strategies as st
from hypothesis import given

import pmg.db


@given(
    st.text(alphabet=st.characters(blacklist_characters=";="), min_size=1),
    st.text(alphabet=st.characters(blacklist_characters=";="), min_size=1),
    st.text(alphabet=st.characters(blacklist_characters=";="), min_size=1),
    st.text(alphabet=st.characters(blacklist_characters=";="), min_size=1),
)
def test_connection_string_to_dict(server, database, user, password):
    cn = pmg.db.connection_string_to_dict(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"Server={server};Database={database};"
        f"UID={user};PWD={password}"
    )
    assert cn["DRIVER"] == "{ODBC Driver 17 for SQL Server}"
    assert cn["SERVER"] == server
    assert cn["DATABASE"] == database
    assert cn["UID"] == user
    assert cn["PWD"] == password


def init_test_db(db):
    db.execute(
        "CREATE TABLE IF NOT EXISTS TestTable (IntValue INTEGER NOT NULL, TextValue TEXT NULL, FloatValue REAL NULL);"
    )
    db.executemany(
        "INSERT INTO TestTable VALUES (?, ?, ?)",
        (
            (
                random.randint(-sys.maxsize + 1, sys.maxsize),
                str(random.random()),
                random.random(),
            )
            for i in range(100)
        ),
    )
    db.commit()


def test_iter_cursor():
    with sqlite3.connect(":memory:") as db:
        init_test_db(db)
        cur = db.execute("SELECT * FROM TestTable")
        for r in pmg.db.iter_cursor_as_dict(cur):
            assert "TextValue" in r and "IntValue" in r and "FloatValue" in r
        cur = db.execute("SELECT * FROM TestTable")
        for r in cur:
            assert isinstance(r[0], int)
            assert isinstance(r[1], str)
            assert isinstance(r[2], float)
