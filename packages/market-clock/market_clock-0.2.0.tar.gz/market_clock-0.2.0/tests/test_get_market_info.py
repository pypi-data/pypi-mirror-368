import datetime
from zoneinfo import ZoneInfo

from market_clock import get_market_info

ALL_MARKET_INFO = get_market_info.ALL_MARKET_INFO


def test_required_info() -> None:
    for market, info in ALL_MARKET_INFO.items():
        assert isinstance(info.timezone, ZoneInfo), (
            f"Timezone for {market} is not a ZoneInfo instance."
        )
        assert isinstance(info.trading_weekdays, set), (
            f"Trading weekdays for {market} is not a set."
        )

        assert all(
            isinstance(day, int) and 0 <= day <= 6 for day in info.trading_weekdays
        ), f"Trading weekdays for {market} must be integers from 0 to 6."

        assert isinstance(info.start_time, datetime.time), (
            f"Start time for {market} is not a datetime.time instance."
        )
        assert isinstance(info.end_time, datetime.time), (
            f"End time for {market} is not a datetime.time instance."
        )
        assert isinstance(info.holidays, set), f"Holidays for {market} is not a set."
        assert isinstance(info.half_days, set), f"Half days for {market} is not a set."

        for holiday in info.holidays:
            assert isinstance(holiday, datetime.date), (
                f"Holiday {holiday} for {market} is not a datetime.date instance."
            )

        for half_day in info.half_days:
            assert isinstance(half_day, datetime.date), (
                f"Half day {half_day} for {market} is not a datetime.date instance."
            )

        assert isinstance(info.is_have_lunch_break, bool), (
            f"Lunch break flag for {market} is not a boolean."
        )


def test_no_duplication_holiday_halfday() -> None:
    for market, info in ALL_MARKET_INFO.items():
        holidays = info.holidays
        half_days = info.half_days

        assert not holidays & half_days, f"{market} has overlapping holidays/half-days."


def test_outdated_holiday_halfday() -> None:
    for market, info in ALL_MARKET_INFO.items():
        timezone = info.timezone

        local_time = datetime.datetime.now(timezone)
        current_date = local_time.date()

        holidays = info.holidays
        half_days = info.half_days

        if not holidays and not half_days:
            pass

        else:
            assert current_date.year <= max(d.year for d in holidays | half_days), (
                f"Holiday and half day list not updated for {market} in year {current_date.year}."
            )


def test_start_half_end_time_order() -> None:
    for market, info in ALL_MARKET_INFO.items():
        start_time = info.start_time
        end_time = info.end_time
        half_day_end_time = info.half_day_end_time
        lunch_break_start = info.lunch_break_start
        lunch_break_end = info.lunch_break_end

        if info.is_have_lunch_break and info.half_days:
            assert half_day_end_time is not None
            assert lunch_break_start is not None
            assert lunch_break_end is not None

            # Assume in half day lunch break is cancelled
            assert (
                start_time
                <= half_day_end_time
                <= lunch_break_start
                <= lunch_break_end
                <= end_time
            ), (
                f"Time out of order for {market}. Check start, half day, lunch break, and end times."
            )

        elif info.is_have_lunch_break and not info.half_days:
            assert lunch_break_start is not None
            assert lunch_break_end is not None

            assert start_time <= lunch_break_start <= lunch_break_end <= end_time, (
                f"Time out of order for {market}. Check start, lunch break, and end times."
            )

        elif not info.is_have_lunch_break and info.half_days:
            assert half_day_end_time is not None

            assert start_time <= half_day_end_time <= end_time, (
                f"Time out of order for {market}. Check start, half day end, and end times."
            )
        else:
            assert start_time <= end_time, (
                f"Time out of order for {market}. Check start and end times."
            )


def test_lunch_break_is_specified() -> None:
    for market, info in ALL_MARKET_INFO.items():
        if info.is_have_lunch_break:
            assert isinstance(info.lunch_break_start, datetime.time), (
                f"No time specified for lunch break start for {market}."
            )
            assert isinstance(info.lunch_break_end, datetime.time), (
                f"No time specified for lunch break end for {market}."
            )


def test_half_day_end_is_specified() -> None:
    for market, info in ALL_MARKET_INFO.items():
        if info.half_days:
            assert isinstance(info.half_day_end_time, datetime.time), (
                f"No time specified for half day end for {market}."
            )
