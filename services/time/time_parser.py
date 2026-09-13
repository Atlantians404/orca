from datetime import datetime, timedelta

from ai.schemas.time import TimeContext, TimeSlot


TIMEZONE = "Asia/Kolkata"


def resolve_date(date_expression: str | None) -> str:
    """
    Resolve simple date expressions.

    Currently supports:
    - today
    - tomorrow

    Defaults to tomorrow when no date is supplied.
    """

    now = datetime.now()

    if not date_expression:
        date = now + timedelta(days=1)

    elif date_expression.lower() == "today":
        date = now

    elif date_expression.lower() == "tomorrow":
        date = now + timedelta(days=1)

    else:
        # Expected to be expanded later for actual calendar dates.
        date = now + timedelta(days=1)

    return date.strftime("%Y-%m-%d")


def build_specific_time(
    date_expression: str | None,
    time: str,
) -> TimeContext:

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

    date = resolve_date(date_expression)

    period = period.lower()

    if period == "morning":
        slots = [
            TimeSlot(
                date=date,
                start_time="06:00",
                end_time="09:00",
            ),
            TimeSlot(
                date=date,
                start_time="09:00",
                end_time="12:00",
            ),
            TimeSlot(
                date=date,
                start_time="12:00",
                end_time="15:00",
            ),
        ]

    elif period == "afternoon":
        slots = [
            TimeSlot(
                date=date,
                start_time="12:00",
                end_time="15:00",
            ),
            TimeSlot(
                date=date,
                start_time="15:00",
                end_time="18:00",
            ),
            TimeSlot(
                date=date,
                start_time="18:00",
                end_time="21:00",
            ),
        ]

    elif period == "evening":
        slots = [
            TimeSlot(
                date=date,
                start_time="15:00",
                end_time="18:00",
            ),
            TimeSlot(
                date=date,
                start_time="18:00",
                end_time="21:00",
            ),
            TimeSlot(
                date=date,
                start_time="21:00",
                end_time="23:00",
            ),
        ]

    else:
        raise ValueError(f"Unknown time period: {period}")

    return TimeContext(
        slots=slots,
        timezone=TIMEZONE,
    )