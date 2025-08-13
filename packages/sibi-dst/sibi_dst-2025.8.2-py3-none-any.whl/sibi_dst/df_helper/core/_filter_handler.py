import datetime

import dask.dataframe as dd
import pandas as pd
from sqlalchemy import func, cast
from sqlalchemy.sql.sqltypes import Date, Time

from sibi_dst.utils import Logger


class FilterHandler:
    """
    Handles the application of filters to data sources with support for SQLAlchemy and Dask backends.

    The FilterHandler class abstracts the process of applying filters to various backends, specifically
    SQLAlchemy queries and Dask DataFrames. It supports multiple filtering operations, including
    exact matches, comparisons, and string-related operations such as contains and regex. The handler
    automatically determines and applies backend-specific processing, enabling seamless integration with
    different data models or backends.

    :ivar backend: The backend in use ('sqlalchemy' or 'dask').
    :type backend: str
    :ivar logger: An optional logger instance for debugging and logging purposes.
    :type logger: Logger
    :ivar backend_methods: A dictionary mapping backend-specific methods for column retrieval and operation application.
    :type backend_methods: dict
    """
    def __init__(self, backend, logger=None, debug=False):
        """
        Initialize the FilterHandler.

        Args:
            backend: The backend to use ('sqlalchemy' or 'dask').
            logger: Optional logger for debugging purposes.
        """
        self.backend = backend
        self.logger = logger or Logger.default_logger(
            logger_name=self.__class__.__name__)  # No-op logger if none provided
        self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)
        self.backend_methods = self._get_backend_methods(backend)

    def apply_filters(self, query_or_df, model=None, filters=None):
        """
        Apply filters to the data source based on the backend.

        Args:
            query_or_df: SQLAlchemy query or Dask DataFrame.
            model: SQLAlchemy model (required for SQLAlchemy backend).
            filters: Dictionary of filters.

        Returns:
            Filtered query or DataFrame.
        """
        filters = filters or {}
        for key, value in filters.items():
            field_name, casting, operation = self._parse_filter_key(key)
            parsed_value = self._parse_filter_value(casting, value)
            # print(field_name, casting, operation, parsed_value)
            # Get the column and apply backend-specific transformations
            if self.backend == "sqlalchemy":
                column = self.backend_methods["get_column"](field_name, model, casting)
                condition = self.backend_methods["apply_operation"](column, operation, parsed_value)
                query_or_df = self.backend_methods["apply_condition"](query_or_df, condition)

            elif self.backend == "dask":
                column = self.backend_methods["get_column"](query_or_df, field_name, casting)
                condition = self.backend_methods["apply_operation"](column, operation, parsed_value)
                query_or_df = self.backend_methods["apply_condition"](query_or_df, condition)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")

        return query_or_df

    @staticmethod
    def _parse_filter_key(key):
        parts = key.split("__")
        field_name = parts[0]
        casting = None
        operation = "exact"

        if len(parts) == 3:
            _, casting, operation = parts
        elif len(parts) == 2:
            if parts[1] in FilterHandler._comparison_operators():
                operation = parts[1]
            elif parts[1] in FilterHandler._dt_operators() + FilterHandler._date_operators():
                casting = parts[1]

        return field_name, casting, operation

    def _parse_filter_value(self, casting, value):
        """
        Convert filter value to appropriate type based on the casting (e.g., date).
        """
        if casting == "date":
            if isinstance(value, str):
                parsed = pd.Timestamp(value)  # Convert to datetime64[ns]
                return parsed
            if isinstance(value, list):
                parsed = [pd.Timestamp(v) for v in value]
                return parsed
        elif casting == "time" and isinstance(value, str):
            parsed = datetime.time.fromisoformat(value)
            self.logger.debug(f"Parsed value (time): {parsed}")
            return parsed
        return value

    @staticmethod
    def _get_backend_methods(backend):
        if backend == "sqlalchemy":
            return {
                "get_column": FilterHandler._get_sqlalchemy_column,
                "apply_operation": FilterHandler._apply_operation_sqlalchemy,
                "apply_condition": lambda query, condition: query.filter(condition),
            }
        elif backend == "dask":
            return {
                "get_column": FilterHandler._get_dask_column,
                "apply_operation": FilterHandler._apply_operation_dask,
                "apply_condition": lambda df, condition: df[condition],
            }
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    @staticmethod
    def _get_sqlalchemy_column(field_name, model, casting):
        """
        Retrieve and cast a column for SQLAlchemy based on the field name and casting.

        Args:
            field_name: The name of the field/column in the model.
            model: The SQLAlchemy model.
            casting: The casting type ('date', 'time', etc.).

        Returns:
            The SQLAlchemy column object, optionally cast or transformed.
        """
        column = getattr(model, field_name, None)
        if not column:
            raise AttributeError(f"Field '{field_name}' not found in model '{model.__name__}'")

        if casting == "date":
            # Cast the column to Date for whole-date comparisons
            column = cast(column, Date)
        elif casting == "time":
            # Cast the column to Time for time-specific comparisons
            column = cast(column, Time)
        elif casting in FilterHandler._date_operators():
            # Extract date part (e.g., year, month) using SQLAlchemy functions
            column = func.extract(casting, column)

        return column

    @staticmethod
    def _get_dask_column(df, field_name, casting):
        """
        Retrieve and optionally cast a column for Dask based on the field name and casting.

        Args:
            df: The Dask DataFrame.
            field_name: The name of the field/column in the DataFrame.
            casting: The casting type ('date', 'time', etc.).

        Returns:
            The Dask Series object, optionally cast or transformed.
        """
        column = dd.to_datetime(df[field_name], errors="coerce") if casting in FilterHandler._dt_operators() else df[
            field_name]

        if casting == "date":
            column = column.dt.floor("D")  # Ensure truncation to the date level
        elif casting in FilterHandler._date_operators():
            column = getattr(column.dt, casting)

        return column

    @staticmethod
    def _apply_operation_sqlalchemy(column, operation, value):
        operation_map = FilterHandler._operation_map_sqlalchemy()
        if operation not in operation_map:
            raise ValueError(f"Unsupported operation: {operation}")
        return operation_map[operation](column, value)

    @staticmethod
    def _apply_operation_dask(column, operation, value):
        operation_map = FilterHandler._operation_map_dask()
        if operation not in operation_map:
            raise ValueError(f"Unsupported operation: {operation}")
        return operation_map[operation](column, value)

    @staticmethod
    def _operation_map_sqlalchemy():
        return {
            "exact": lambda col, val: col == val,
            "gt": lambda col, val: col > val,
            "gte": lambda col, val: col >= val,
            "lt": lambda col, val: col < val,
            "lte": lambda col, val: col <= val,
            "in": lambda col, val: col.in_(val),
            "range": lambda col, val: col.between(val[0], val[1]),
            "contains": lambda col, val: col.like(f"%{val}%"),
            "startswith": lambda col, val: col.like(f"{val}%"),
            "endswith": lambda col, val: col.like(f"%{val}"),
            "isnull": lambda col, val: col.is_(None) if val else col.isnot(None),
            "not_exact": lambda col, val: col != val,
            "not_contains": lambda col, val: ~col.like(f"%{val}%"),
            "not_in": lambda col, val: ~col.in_(val),  # Custom operation
            "regex": lambda col, val: col.op("~")(val),  # Custom operation
            "icontains": lambda col, val: col.ilike(f"%{val}%"),  # Custom operation
            "istartswith": lambda col, val: col.ilike(f"{val}%"),  # Custom operation
            "iendswith": lambda col, val: col.ilike(f"%{val}"),  # Custom operation
            "iexact": lambda col, val: col.ilike(val),  # Added iexact
            "iregex": lambda col, val: col.op("~*")(val),  # Added iregex
        }

    @staticmethod
    def _operation_map_dask():
        return {
            "exact": lambda col, val: col == val,
            "gt": lambda col, val: col > val,
            "gte": lambda col, val: col >= val,
            "lt": lambda col, val: col < val,
            "lte": lambda col, val: col <= val,
            "in": lambda col, val: col.isin(val),
            "range": lambda col, val: (col >= val[0]) & (col <= val[1]),
            "contains": lambda col, val: col.str.contains(val, regex=True),
            "startswith": lambda col, val: col.str.startswith(val),
            "endswith": lambda col, val: col.str.endswith(val),
            "isnull": lambda col, val: col.isnull() if val else col.notnull(),
            "not_exact": lambda col, val: col != val,
            "not_contains": lambda col, val: ~col.str.contains(val, regex=True),
            "not_in": lambda col, val: ~col.isin(val),  # Custom operation
            "regex": lambda col, val: col.str.contains(val, regex=True),  # Custom operation
            "icontains": lambda col, val: col.str.contains(val, case=False, regex=True),  # Custom operation
            "istartswith": lambda col, val: col.str.startswith(val, case=False),  # Custom operation
            "iendswith": lambda col, val: col.str.endswith(val, case=False),  # Custom operation
            "iexact": lambda col, val: col.str.contains(f"^{val}$", case=False, regex=True),  # Added iexact
            "iregex": lambda col, val: col.str.contains(val, case=False, regex=True),  # Added iregex
        }

    @staticmethod
    def _dt_operators():
        return ["date", "time"]

    @staticmethod
    def _date_operators():
        return ["year", "month", "day", "hour", "minute", "second", "week_day"]

    @staticmethod
    def _comparison_operators():
        return [
            "gte", "lte", "gt", "lt", "exact", "in", "range",
            "contains", "startswith", "endswith", "isnull",
            "not_exact", "not_contains", "not_in",
            "regex", "icontains", "istartswith", "iendswith",
            "iexact", "iregex"
        ]
