"""Tests for the pmg module"""

import datetime

import hypothesis.strategies as st
import pytest
from hypothesis import example, given

import pmg


def test_get_next_weekday():
    today = datetime.datetime.today().date()
    tomorrow = today + datetime.timedelta(days=1)
    max_result = today + datetime.timedelta(days=7)
    for i in range(7):
        dt = pmg.get_next_weekday(i)
        assert dt.weekday() == i
        assert dt >= today and dt < max_result
        dt = pmg.get_next_weekday(i, from_date=tomorrow)
        assert dt.weekday() == i
        assert dt > today and dt <= max_result


@given(st.integers(min_value=0, max_value=6), st.dates())
def test_get_next_weekday_2(i, dt):
    res = pmg.get_next_weekday(i, dt)
    assert res >= dt and res < dt + datetime.timedelta(days=7)
    assert res.weekday() == i


@given(st.datetimes())
def test_parse_iso_datetime(dt):
    assert pmg.parse_iso_datetime(dt.isoformat()) == dt


@given(st.datetimes())
def test_parse_iso_datetime_utc(dt):
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    assert pmg.parse_iso_datetime_utc(dt.isoformat()) == dt


@given(st.datetimes(timezones=st.timezones()))
@example(pmg.utcnow())
def test_parse_iso_datetimes(dt):
    dt = dt.astimezone(datetime.timezone.utc)
    assert pmg.parse_iso_datetime_utc(dt.isoformat()) == dt


@given(st.dates())
def test_parse_iso_date(dt):
    assert pmg.parse_iso_date(dt.isoformat()) == dt


@given(st.datetimes(timezones=st.none()))
def test_is_datetime_naive(dt):
    assert pmg.is_datetime_naive(dt)


@given(st.datetimes(timezones=st.timezones()))
def test_is_datetime_not_naive(dt):
    assert not pmg.is_datetime_naive(dt)


@given(st.datetimes(timezones=st.timezones()))
def test_make_datetime_naive(dt):
    d = pmg.make_datetime_naive(dt)
    assert pmg.is_datetime_naive(d)
    assert (
        d.year == dt.year
        and d.month == dt.month
        and d.day == dt.day
        and d.hour == dt.hour
        and d.minute == dt.minute
        and d.second == dt.second
    )


@given(st.text(), st.integers(min_value=0))
def test_hide_str_excess(text, max_len):
    result = pmg.hide_str_excess(text, max_len)
    assert len(result) <= max_len + 3
    if len(result) <= max_len:
        assert result == text
    else:
        assert result[-3:] == "..."


@given(
    st.datetimes(timezones=st.timezones()),
    st.integers(min_value=-86400 * 365 * 20, max_value=86400 * 365 * 20),
)
def test_get_seconds_until(dt, i):
    assert pmg.get_seconds_until(dt, dt) == 0
    dt2 = dt + datetime.timedelta(seconds=i)
    assert pmg.get_seconds_until(dt2, dt) == i
    assert pmg.get_seconds_until(dt, dt2) == -i


def inner_quote_test(s, q):
    if q not in s:
        assert pmg.quote(s, q) == f"{q}{s}{q}"
        assert pmg.unquote(pmg.quote(s, q), q) == s
        assert pmg.unquote(s, q) == s
    else:
        with pytest.raises(AssertionError):
            assert pmg.quote(s, q) == f"{q}{s}{q}"


@given(st.text(), st.text())
@example("This won't fly", "'")
@example('"This will not fly, either."', '"')
def test_quote(s, q):
    inner_quote_test(s, q)


@given(st.text())
@example("This won't fly")
def test_quote_single(s):
    inner_quote_test(s, "'")


@given(st.text())
@example('"This will not fly, either."')
def test_quote_double(s):
    inner_quote_test(s, '"')


def test_localnow():
    dt = pmg.localnow("America/Chicago")
    utc = dt.astimezone(datetime.timezone.utc)
    assert not pmg.is_datetime_naive(dt)
    assert dt.tzinfo.utcoffset(dt).total_seconds() in [-5 * 3600, -6 * 3600]
    assert pmg.make_datetime_naive(dt) != pmg.make_datetime_naive(utc)

    dt = pmg.localnow("Europe/Zurich")
    utc = dt.astimezone(datetime.timezone.utc)
    assert not pmg.is_datetime_naive(dt)
    assert dt.tzinfo.utcoffset(dt).total_seconds() in [1 * 3600, 2 * 3600]
    assert pmg.make_datetime_naive(dt) != pmg.make_datetime_naive(utc)

    dt = pmg.localnow("Europe/London")
    utc = dt.astimezone(datetime.timezone.utc)
    assert not pmg.is_datetime_naive(dt)
    assert dt.tzinfo.utcoffset(dt).total_seconds() in [0, 3600]


@given(st.text(), st.text())
@example("ABCDEF", "AB")
@example("ABCDEF", "BA")
def test_remove_prefix(text, prefix):
    if text.startswith(prefix):
        assert pmg.remove_prefix(text, prefix) == text[len(prefix) :]
    else:
        assert pmg.remove_prefix(text, prefix) == text


@given(st.text(), st.text())
@example("ABCDEF", "EF")
@example("ABCDEF", "BA")
def test_remove_suffix(text, suffix):
    if text.endswith(suffix):
        assert pmg.remove_suffix(text, suffix) == text[-len(suffix) :]
    else:
        assert pmg.remove_suffix(text, suffix) == text
