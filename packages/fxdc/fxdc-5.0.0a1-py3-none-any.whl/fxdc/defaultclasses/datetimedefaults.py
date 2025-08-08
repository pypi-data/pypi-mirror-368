from datetime import date, datetime, time, timedelta

from ..config import Config


def date_to_data(date_: date) -> str:
    return str(date_)


def date_from_data(
    data: str, *, years: int = 0, months: int = 0, days: int = 0
) -> date:
    if data:
        years = int(data.split("-")[0])
        months = int(data.split("-")[1])
        days = int(data.split("-")[2])
    return date(years, months, days)


def datetime_to_data(datetime_: datetime) -> str:
    return str(datetime_)


def datetime_from_data(
    data: str,
    *,
    years: int = 0,
    months: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
) -> datetime:
    if data:
        years = int(data.split("-")[0])
        months = int(data.split("-")[1])
        days = int(data.split("-")[2].split(" ")[0])
        hours = int(data.split(" ")[1].split(":")[0])
        minutes = int(data.split(" ")[1].split(":")[1])
        seconds = int(data.split(" ")[1].split(":")[2].split(".")[0])
        microseconds = (
            int(data.split(" ")[1].split(":")[2].split(".")[1])
            if "." in data.split(" ")[1].split(":")[2]
            else 0
        )
    return datetime(years, months, days, hours, minutes, seconds, microseconds)


def time_to_data(time_: time) -> str:
    return str(time_)


def time_from_data(
    data: str,
    *,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
) -> time:
    if data:
        hours = int(data.split(":")[0])
        minutes = int(data.split(":")[1])
        seconds = int(data.split(":")[2].split(".")[0])
        microseconds = (
            int(data.split(":")[2].split(".")[1])
            if "." in data.split(":")[2]
            else 0
        )
    return time(hours, minutes, seconds, microseconds)


def timedelta_to_data(timedelta_: timedelta) -> str:
    return str(timedelta_)


def timedelta_from_data(
    data: str,
    *,
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    milliseconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0,
) -> timedelta:
    if data:
        if "days" in data:
            days = int(data.split("days,")[0])
            data = data.split("days,")[1]
        elif "day" in data:
            days = int(data.split("day,")[0])
            data = data.split("day,")[1]
        else:
            days = 0
        hours, minutes, seconds = data.split(":")
        hours = int(hours)
        minutes = int(minutes)
        if "." in seconds:
            seconds, microseconds = seconds.split(".")
        else:
            microseconds = 0
        seconds = int(seconds)
        microseconds = int(microseconds)
    return timedelta(
        days, seconds, microseconds, milliseconds, minutes, hours, weeks
    )


def load() -> None:
    Config.add_class(
        class_=timedelta,
        name="TimeDelta",
        to_data=timedelta_to_data,
        from_data=timedelta_from_data,
    )
    Config.add_class(
        name="Date", class_=date, to_data=date_to_data, from_data=date_from_data
    )
    Config.add_class(
        name="DateTime",
        class_=datetime,
        to_data=datetime_to_data,
        from_data=datetime_from_data,
    )
    Config.add_class(
        name="Time", class_=time, to_data=time_to_data, from_data=time_from_data
    )
