import calendar
from collections import namedtuple
from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta
from robot_base import log_decorator


@log_decorator
def get_current_time(**kwargs):
    return datetime.now()


@log_decorator
def add_or_subtract_date(original_date, operate_type, delta, time_unit, **kwargs):
    if isinstance(original_date, str):
        original_date = parser.parse(original_date)
    delta = int(delta)
    if time_unit == "year":
        relative_delta = relativedelta(years=delta)
    elif time_unit == "month":
        relative_delta = relativedelta(months=delta)
    elif time_unit == "week":
        relative_delta = relativedelta(weeks=delta)
    elif time_unit == "day":
        relative_delta = relativedelta(days=delta)
    elif time_unit == "hour":
        relative_delta = relativedelta(hours=delta)
    elif time_unit == "minute":
        relative_delta = relativedelta(minutes=delta)
    elif time_unit == "second":
        relative_delta = relativedelta(seconds=delta)
    else:
        raise Exception("不支持的时间单位")
    if operate_type == "add":
        return original_date + relative_delta
    elif operate_type == "subtract":
        return original_date - relative_delta
    else:
        raise Exception("不支持的操作类型")


@log_decorator
def get_duration(start_time, end_time, time_unit, **kwargs):
    if isinstance(start_time, str):
        start_time = parser.parse(start_time)
    if isinstance(end_time, str):
        end_time = parser.parse(end_time)
    time_delta = relativedelta(start_time, end_time)
    if time_unit == "year":
        return time_delta.years
    elif time_unit == "month":
        return time_delta.months
    elif time_unit == "week":
        return time_delta.weeks
    elif time_unit == "day":
        return time_delta.days
    elif time_unit == "hour":
        return time_delta.hours
    elif time_unit == "minute":
        return time_delta.minutes
    elif time_unit == "second":
        return time_delta.seconds


@log_decorator
def text_to_date(text, use_format, format_text, **kwargs):
    if use_format:
        return datetime.strptime(text, format_text)
    return parser.parse(text)


@log_decorator
def date_to_text(date, format_text, **kwargs):
    return date.strftime(format_text)


@log_decorator
def get_date_detail(original_date, **kwargs):
    if isinstance(original_date, str):
        original_date = parser.parse(original_date)
    DateParts = namedtuple(
        "DateParts",
        [
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "week",
            "last_day_of_month",
            "week_of_year",
            "day_of_year",
        ],
    )
    week_number = original_date.isocalendar()[1]
    day_of_year = original_date.timetuple().tm_yday
    last_day_of_month = calendar.monthrange(original_date.year, original_date.month)[1]
    return DateParts(
        original_date.year,
        original_date.month,
        original_date.day,
        original_date.hour,
        original_date.minute,
        original_date.second,
        original_date.weekday(),
        last_day_of_month,
        week_number,
        day_of_year,
    )


@log_decorator
def date_to_timestamp(original_date, time_unit, **kwargs):
    if isinstance(original_date, str):
        original_date = parser.parse(original_date)

    if time_unit == "second":
        return int(original_date.timestamp())
    elif time_unit == "millisecond":
        return int(original_date.timestamp() * 1000)
    elif time_unit == "microsecond":
        return int(original_date.timestamp() * 1000000)
    else:
        raise Exception("不支持的时间单位")


@log_decorator
def timestamp_to_date(timestamp, time_unit, **kwargs):
    if time_unit == "second":
        return datetime.fromtimestamp(timestamp)
    elif time_unit == "millisecond":
        return datetime.fromtimestamp(timestamp / 1000)
    elif time_unit == "microsecond":
        return datetime.fromtimestamp(timestamp / 1000000)
    else:
        raise Exception("不支持的时间单位")
