# TODO copied from database-mysql Do we need it twice? We prefer to have one
#  copy to_sql_interface.py

from abc import ABC, abstractmethod
from typing import Any


# TODO: should we use SqlLiteral instead of ToSQLInterface and all its
#  subclasses?
class ToSQLInterface(ABC):
    """
    An interface for objects that represent structures to be
    inserted into a database.

    Subclasses must implement the `to_sql` method, which should return a string
    representing the SQL representation of the structure.

    Example:
    --------
    class Point(ToSQLInterface):
        def __init__(self, longitude, latitude):
            self.longitude = longitude
            self.latitude = latitude

        def to_sql(self):
            return f"POINT({self.longitude}, {self.latitude})"
    """

    @abstractmethod
    def to_sql(self) -> str:
        pass


class Now(ToSQLInterface):
    """
    Represents the current time in SQL.
    """

    def to_sql(self):
        return "NOW()"


class CurrentDate(ToSQLInterface):
    """Represents the current date in SQL."""

    def to_sql(self):
        return "CURDATE()"


class TimeStampDiff(ToSQLInterface):
    """
    Represents the current time in SQL.
    """

    def __init__(self, unit, start, end):
        allowed_units = ("YEAR", "QUARTER", "MONTH", "WEEK", "DAY", "HOUR", "MINUTE", "SECOND", "FRAC_SECOND")
        if unit not in allowed_units:
            raise ValueError(f"unit must be one of {allowed_units}")
        self.unit = unit
        self.start = start
        self.end = end

    def to_sql(self):
        return f"TIMESTAMPDIFF({self.unit}, {self.start}, {self.end})"


class Count(ToSQLInterface):
    """Represents a COUNT() function in SQL."""

    def __init__(self, column_name="*"):
        self.column_name = column_name

    def to_sql(self):
        return f"COUNT({self.column_name})"


class TimeUnit(ToSQLInterface):
    """Represents a time unit function in SQL."""

    def __init__(self, column_name: str, unit: str):
        allowed_units = ("YEAR", "QUARTER", "MONTH", "WEEK", "DAY", "HOUR", "MINUTE", "SECOND", "FRAC_SECOND")
        if unit not in allowed_units:
            raise ValueError(f"unit must be one of {allowed_units}")
        self.column_name = column_name
        self.unit = unit

    def to_sql(self):
        return f"{self.unit}({self.column_name})"


class Function(ToSQLInterface):
    """Represents a function with a single arg in SQL.
    (SUM, MIN, MAX, AVG, etc.)"""

    def __init__(self, function_name: str, column_name: str):
        self.function_name = function_name
        self.column_name = column_name

    def to_sql(self):
        return f"{self.function_name}({self.column_name})"


class Concat(ToSQLInterface):
    """Represents a CONCAT() function in SQL.
    Example:
       Input: Concat(TimeUnit(column_name="birthday_date", unit="YEAR"), "-", TimeUnit(column_name="birthday_date", unit="MONTH"), "-", 1)  # noqa E501
                -> CONCAT(YEAR(birthday_date), '-', MONTH(birthday_date), '-', 1)"""

    def __init__(self, *column_names: ToSQLInterface | Any):
        self.column_names = column_names

    def to_sql(self):
        column_names = [column_name.to_sql() if isinstance(column_name, ToSQLInterface) else
                        (f"'{column_name}'" if isinstance(column_name, str) else str(column_name))
                        for column_name in self.column_names]
        return f"CONCAT({','.join(column_names)})"
