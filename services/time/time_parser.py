from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ai.schemas.time import TimeContext, TimeSlot


TIMEZONE = "Asia/Kolkata"


def _now() -> datetime:
    """
    Return current datetime in ORCA's configured timezone.
    """
    return datetime.now(ZoneInfo(TIMEZONE))


def resolve_date(date_expression: str | None) -> str:
    """
    Resolve simple date expressions.

    Supported:
    - today
    - tomorrow
    - day after tomorrow

    If no date is supplied, default to tomorrow.
    """

    now = _now()

    if not date_expression:
        date = now + timedelta(days=1)

    else:
        expression = date_expression.strip().lower()

        if expression == "today":
            date = now

        elif expression == "tomorrow":
            date = now + timedelta(days=1)

        elif expression == "day after tomorrow":
            date = now + timedelta(days=2)

        else:
            # Calendar-date parsing can be added later.
            # For now, preserve existing behaviour.
            date = now + timedelta(days=1)

    return date.strftime("%Y-%m-%d")


def build_specific_time(
    date_expression: str | None,
    time: str,
) -> TimeContext:
    """
    Build a TimeContext for an exact fishing time.

    Examples:

    date_expression="tomorrow", time="06:00"
        -> tomorrow at 06:00

    date_expression=None, time="17:30"
        -> defaults to tomorrow at 17:30
    """

    date = resolve_date(date_expression)

    return TimeContext(
        slots=[
            TimeSlot(
                date=date,
                start_time=time,
                end_time=None,
            )
        ],
        timezone=TIMEZONE,
    )


def build_generic_time(
    date_expression: str | None,
    period: str,
) -> TimeContext:
    """
    Build a single continuous time window for a broad period.

    ORCA uses one slot per broad period rather than splitting
    the period into multiple smaller slots.

    Supported periods:

    morning   -> 06:00 - 12:00
    afternoon -> 12:00 - 18:00
    evening   -> 17:00 - 21:00
    night     -> 21:00 - 06:00
    """

    date = resolve_date(date_expression)

    period = period.strip().lower()

    if period == "morning":
        start_time = "06:00"
        end_time = "12:00"

    elif period == "afternoon":
        start_time = "12:00"
        end_time = "18:00"

    elif period == "evening":
        start_time = "17:00"
        end_time = "21:00"

    elif period == "night":
        start_time = "21:00"
        end_time = "06:00"

    else:
        raise ValueError(f"Unknown time period: {period}")

    return TimeContext(
        slots=[
            TimeSlot(
                date=date,
                start_time=start_time,
                end_time=end_time,
            )
        ],
        timezone=TIMEZONE,
    )
