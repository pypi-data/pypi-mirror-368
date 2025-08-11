from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Literal
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class MarketInfo:
    timezone: ZoneInfo
    trading_weekdays: set[Literal[0, 1, 2, 3, 4, 5, 6]]
    start_time: time
    end_time: time
    half_day_end_time: time | None
    holidays: set[date]
    half_days: set[date]
    is_have_lunch_break: bool
    lunch_break_start: time | None
    lunch_break_end: time | None


ALL_MARKET_INFO: dict[str, MarketInfo] = {
    # https://www.jpx.co.jp/english/corporate/about-jpx/calendar/
    # https://www.jpx.co.jp/english/equities/products/preferred-stocks/trading/index.html
    "TSE": MarketInfo(
        timezone=ZoneInfo("Asia/Tokyo"),
        trading_weekdays={0, 1, 2, 3, 4},
        start_time=time(9, 0),
        end_time=time(15, 30),
        half_day_end_time=None,
        holidays={
            date(2025, 1, 1),
            date(2025, 1, 2),
            date(2025, 1, 3),
            date(2025, 1, 13),
            date(2025, 2, 11),
            date(2025, 2, 23),
            date(2025, 2, 24),
            date(2025, 3, 20),
            date(2025, 4, 29),
            date(2025, 5, 3),
            date(2025, 5, 4),
            date(2025, 5, 5),
            date(2025, 5, 6),
            date(2025, 7, 21),
            date(2025, 8, 11),
            date(2025, 9, 15),
            date(2025, 9, 23),
            date(2025, 10, 13),
            date(2025, 11, 3),
            date(2025, 11, 23),
            date(2025, 11, 24),
            date(2025, 12, 31),
            date(2026, 1, 1),
            date(2026, 1, 2),
            date(2026, 1, 12),
            date(2026, 2, 11),
            date(2026, 2, 23),
            date(2026, 3, 20),
            date(2026, 4, 29),
            date(2026, 5, 3),
            date(2026, 5, 4),
            date(2026, 5, 5),
            date(2026, 5, 6),
            date(2026, 7, 20),
            date(2026, 8, 11),
            date(2026, 9, 21),
            date(2026, 9, 22),
            date(2026, 9, 23),
            date(2026, 10, 12),
            date(2026, 11, 3),
            date(2026, 11, 23),
            date(2026, 12, 31),
        },
        half_days=set(),
        is_have_lunch_break=True,
        lunch_break_start=time(11, 30),
        lunch_break_end=time(12, 30),
    ),
    # https://english.sse.com.cn/start/trading/schedule/
    "SSE": MarketInfo(
        timezone=ZoneInfo("Asia/Shanghai"),
        trading_weekdays={0, 1, 2, 3, 4},
        start_time=time(9, 15),
        end_time=time(15, 0),
        half_day_end_time=None,
        holidays={
            date(2025, 1, 1),  # New Year's Day
            date(2025, 1, 28),  # Chinese New Year
            date(2025, 1, 29),
            date(2025, 1, 30),
            date(2025, 1, 31),
            date(2025, 2, 3),
            date(2025, 2, 4),
            date(2025, 4, 4),  # Qingming Festival
            date(2025, 5, 1),  # Labor Day
            date(2025, 5, 2),
            date(2025, 5, 5),
            date(2025, 6, 2),  # Dragon Boat Festival
            date(2025, 10, 1),  # National Day
            date(2025, 10, 2),
            date(2025, 10, 3),
            date(2025, 10, 6),
            date(2025, 10, 7),
            date(2025, 10, 8),
        },
        half_days=set(),
        is_have_lunch_break=True,
        lunch_break_start=time(11, 30),
        lunch_break_end=time(13, 0),
    ),
    # https://www.hkex.com.hk/Services/Trading-hours-and-Severe-Weather-Arrangements/Trading-Hours/Securities-Market
    "HKEX": MarketInfo(
        timezone=ZoneInfo("Asia/Hong_Kong"),
        trading_weekdays={0, 1, 2, 3, 4},
        start_time=time(9, 30),
        end_time=time(16, 0),
        half_day_end_time=time(12, 0),
        holidays={
            date(2025, 1, 1),
            date(2025, 1, 29),
            date(2025, 1, 30),
            date(2025, 1, 31),
            date(2025, 4, 4),
            date(2025, 4, 18),
            date(2025, 4, 21),
            date(2025, 5, 1),
            date(2025, 5, 5),
            date(2025, 7, 1),
            date(2025, 10, 1),
            date(2025, 10, 7),
            date(2025, 10, 29),
            date(2025, 12, 25),
            date(2025, 12, 26),
        },
        half_days={
            date(2025, 1, 28),
            date(2025, 12, 24),
            date(2025, 12, 31),
        },
        is_have_lunch_break=True,
        lunch_break_start=time(12, 0),
        lunch_break_end=time(13, 0),
    ),
    "BSE": MarketInfo(
        # https://www.bseindia.com/static/markets/marketinfo/listholi.aspx
        timezone=ZoneInfo("Asia/Kolkata"),
        trading_weekdays={0, 1, 2, 3, 4},
        start_time=time(9, 15),
        end_time=time(15, 30),
        half_day_end_time=None,
        holidays={
            date(2025, 2, 26),
            date(2025, 3, 14),
            date(2025, 3, 31),
            date(2025, 4, 10),
            date(2025, 4, 14),
            date(2025, 4, 18),
            date(2025, 5, 1),
            date(2025, 8, 15),
            date(2025, 8, 27),
            date(2025, 10, 2),
            date(2025, 10, 21),  # Diwali-Laxmi Pujan (Muhurat Trading)
            date(2025, 10, 22),
            date(2025, 11, 5),
            date(2025, 12, 25),
        },
        half_days=set(),
        is_have_lunch_break=False,
        lunch_break_start=None,
        lunch_break_end=None,
    ),
    # https://www.londonstockexchange.com/equities-trading/business-days
    "LSE": MarketInfo(
        timezone=ZoneInfo("Europe/London"),
        trading_weekdays={0, 1, 2, 3, 4},
        start_time=time(8, 0),
        end_time=time(16, 30),
        half_day_end_time=time(12, 30),
        holidays={
            date(2025, 4, 18),
            date(2025, 4, 21),
            date(2025, 5, 5),
            date(2025, 5, 26),
            date(2025, 8, 25),
            date(2025, 12, 25),
            date(2025, 12, 26),
            date(2026, 1, 1),
            date(2026, 4, 3),
            date(2026, 4, 6),
            date(2026, 5, 4),
            date(2026, 5, 25),
            date(2026, 8, 31),
            date(2026, 12, 25),
            date(2026, 12, 28),
            date(2027, 1, 1),
        },
        half_days={
            date(2025, 12, 24),
            date(2025, 12, 31),
            date(2026, 12, 24),
            date(2026, 12, 31),
        },
        is_have_lunch_break=False,
        lunch_break_start=None,
        lunch_break_end=None,
    ),
    # https://www.nyse.com/markets/hours-calendars
    "NYSE": MarketInfo(
        timezone=ZoneInfo("America/New_York"),
        trading_weekdays={0, 1, 2, 3, 4},
        start_time=time(9, 30),
        end_time=time(16, 0),
        half_day_end_time=time(13, 00),
        holidays={
            date(2025, 1, 1),
            date(2025, 1, 20),
            date(2025, 2, 17),
            date(2025, 4, 18),
            date(2025, 5, 26),
            date(2025, 6, 19),
            date(2025, 7, 4),
            date(2025, 9, 1),
            date(2025, 11, 27),
            date(2025, 12, 25),
            date(2026, 1, 1),
            date(2026, 1, 19),
            date(2026, 2, 16),
            date(2026, 4, 3),
            date(2026, 5, 25),
            date(2026, 6, 19),
            date(2026, 7, 3),
            date(2026, 9, 7),
            date(2026, 11, 26),
            date(2026, 12, 25),
            date(2027, 1, 1),
            date(2027, 1, 18),
            date(2027, 2, 15),
            date(2027, 3, 26),
            date(2027, 5, 31),
            date(2027, 6, 18),
            date(2027, 7, 5),
            date(2027, 9, 6),
            date(2027, 11, 25),
            date(2027, 12, 24),
        },
        half_days={
            date(2025, 7, 3),
            date(2025, 11, 28),
            date(2025, 12, 24),
            date(2026, 11, 27),
            date(2026, 12, 24),
            date(2027, 11, 26),
        },
        is_have_lunch_break=False,
        lunch_break_start=None,
        lunch_break_end=None,
    ),
    # https://www.nasdaq.com/market-activity/stock-market-holiday-schedule
    "NASDAQ": MarketInfo(
        timezone=ZoneInfo("America/New_York"),
        trading_weekdays={0, 1, 2, 3, 4},
        start_time=time(9, 30),
        end_time=time(16, 0),
        half_day_end_time=time(13, 00),
        holidays={
            date(2025, 1, 1),
            date(2025, 1, 20),
            date(2025, 2, 17),
            date(2025, 4, 18),
            date(2025, 5, 26),
            date(2025, 6, 19),
            date(2025, 7, 4),
            date(2025, 9, 1),
            date(2025, 11, 27),
            date(2025, 12, 25),
        },
        half_days={
            date(2025, 7, 3),
            date(2025, 11, 28),
            date(2025, 12, 24),
        },
        is_have_lunch_break=False,
        lunch_break_start=None,
        lunch_break_end=None,
    ),
}
