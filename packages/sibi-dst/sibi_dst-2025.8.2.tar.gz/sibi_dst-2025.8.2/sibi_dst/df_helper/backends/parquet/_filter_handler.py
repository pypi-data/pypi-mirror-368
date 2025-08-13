import dask.dataframe as dd
import pandas as pd

from sibi_dst.utils import Logger


class ParquetFilterHandler(object):
    """
    Handles parquet filtering operations using dask dataframes.

    This class is designed to apply complex filtering logic on dask dataframes
    based on specified filter criteria. It includes support for operations such
    as exact matches, ranges, string pattern matches, and null checks. Additionally,
    it handles datetime-related field filtering including precise truncations and
    specific date/time attributes.

    :ivar logger: Logger object to handle logging within the class. Defaults to the class-level logger.
    :type logger: Logger
    """
    def __init__(self, logger=None, debug=False):
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)

    @staticmethod
    def apply_filters_dask(df, filters):
        """
        Applies a set of filters to a Dask DataFrame, enabling complex filtering operations
        such as comparisons, ranges, string match operations, and more. Handles special
        cases for datetime operations, including casting and extracting specific datetime
        components for filtering.

        :param df: Dask DataFrame to which the filters will be applied.
        :type df: dask.dataframe.DataFrame
        :param filters: Dictionary defining the filtering logic, where the keys specify
            the column name and filter operation, and the values specify the corresponding
            filter values to apply.
        :type filters: dict
        :return: A filtered Dask DataFrame based on the defined logic in the filters.
        :rtype: dask.dataframe.DataFrame
        :raises ValueError: If an unsupported operation is encountered in the filters.
        """
        dt_operators = ['date', 'time']
        date_operators = ['year', 'month', 'day', 'hour', 'minute', 'second', 'week_day']
        comparison_operators = [
            'gte',
            'lte',
            'gt',
            'lt',
            'exact',
            'in',
            'range',
            'contains',
            'icontains',
            'startswith',
            'endswith',
            'isnull'
        ]

        operation_map = {
            'exact': lambda col, val: col == val,
            'gt': lambda col, val: col > val,
            'gte': lambda col, val: col >= val,
            'lt': lambda col, val: col < val,
            'lte': lambda col, val: col <= val,
            'in': lambda col, val: col.isin(val),
            'range': lambda col, val: (col >= val[0]) & (col <= val[1]),
            'contains': lambda col, val: col.str.contains(val, regex=True),
            'icontains': lambda col, val: col.str.contains(val, case=False),
            'startswith': lambda col, val: col.str.startswith(val),
            'endswith': lambda col, val: col.str.endswith(val),
            'isnull': lambda col, val: col.isnull() if val else col.notnull(),
        }

        def parse_filter_value(casting, value):
            """
            Convert filter value to appropriate type based on the casting (e.g., date).
            """
            if casting == 'date':
                if isinstance(value, str):
                    return pd.Timestamp(value)  # Convert to datetime64[ns]
                if isinstance(value, list):
                    return [pd.Timestamp(v) for v in value]  # Convert list elements
            return value

        def get_temp_col(dask_df, field_name, casting):
            """
            Handle datetime conversion and field retrieval.
            """
            temp_col = dd.to_datetime(dask_df[field_name], errors='coerce') if casting in dt_operators else dask_df[
                field_name]
            if casting == 'date':
                temp_col = temp_col.dt.floor('D')  # Keep it as datetime64[ns] truncated to the day level
            elif casting in date_operators:
                temp_col = getattr(temp_col.dt, casting)
            return temp_col

        for key, value in filters.items():
            parts = key.split('__')
            field_name = parts[0]
            casting = None
            operation = 'exact'

            if len(parts) == 3:
                # Adjust logic based on the parts
                _, casting, operation = parts
            elif len(parts) == 2:
                # Could be either a casting or an operation
                if parts[1] in comparison_operators:
                    operation = parts[1]
                elif parts[1] in dt_operators + date_operators:
                    casting = parts[1]

            # Convert the filter value to the correct type
            parsed_value = parse_filter_value(casting, value)

            # Get the column to filter
            temp_col = get_temp_col(df, field_name, casting)

            if operation in operation_map:
                # Apply the filter operation
                condition = operation_map[operation](temp_col, parsed_value)
                df = df[condition]
            else:
                raise ValueError(f"Unsupported operation: {operation}")

        return df
