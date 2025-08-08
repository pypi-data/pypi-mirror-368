import datetime
from typing import Union, Tuple, Generator, overload

DateType = Union[datetime.date, datetime.datetime]
StepType = Union[int, datetime.timedelta]


@overload
def iter_ranges(
    start: datetime.datetime, end: datetime.datetime, step: int = 1
) -> Generator[Tuple[datetime.datetime, datetime.datetime], None, None]: ...


@overload
def iter_ranges(
    start: datetime.date, end: datetime.date, step: int = 1
) -> Generator[Tuple[datetime.date, datetime.date], None, None]: ...


@overload
def iter_ranges(
    start: datetime.date, end: datetime.date, step: datetime.timedelta
) -> Generator[Tuple[datetime.date, datetime.date], None, None]: ...


@overload
def iter_ranges(
    start: datetime.datetime, end: datetime.datetime, step: datetime.timedelta
) -> Generator[Tuple[datetime.datetime, datetime.datetime], None, None]: ...


def iter_ranges(
    start: DateType, end: DateType, step: StepType = 1
) -> Generator[Tuple[DateType, DateType], None, None]:
    current = start
    if isinstance(step, int):
        delta = datetime.timedelta(days=step)
    else:
        delta = step

    while current < end:
        next_date = min(current + delta, end)
        yield current, next_date
        current = next_date
        if current == end:
            break
