from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import ClassVar, Dict, Optional, Any, Iterable, Tuple

import pandas as pd
import dask.dataframe as dd
import clickhouse_connect

from . import ManagedResource


class ClickHouseWriter(ManagedResource):
    """
    Write a Dask DataFrame to ClickHouse with:
      - Safe Dask checks (no df.empty)
      - Nullable dtype mapping
      - Optional overwrite (drop + recreate)
      - Partitioned, batched inserts
      - Per-thread clients to avoid session conflicts
    """

    # Default dtype mapping (pandas/dask → ClickHouse)
    DTYPE_MAP: ClassVar[Dict[str, str]] = {
        "int64": "Int64",
        "Int64": "Int64",  # pandas nullable Int64
        "int32": "Int32",
        "Int32": "Int32",
        "float64": "Float64",
        "Float64": "Float64",
        "float32": "Float32",
        "bool": "UInt8",
        "boolean": "UInt8",
        "object": "String",
        "string": "String",
        "category": "String",
        "datetime64[ns]": "DateTime",
        "datetime64[ns, UTC]": "DateTime",
    }

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 8123,
        database: str = "sibi_data",
        user: str = "default",
        password: str = "",
        table: str = "test_sibi_table",
        order_by: str = "id",
        engine: Optional[str] = None,  # e.g. "ENGINE MergeTree ORDER BY (`id`)"
        max_workers: int = 4,
        insert_chunksize: int = 50_000,
        overwrite: bool = False,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.host = host
        self.port = int(port)
        self.database = database
        self.user = user
        self.password = password
        self.table = table
        self.order_by = order_by
        self.engine = engine  # if None → default MergeTree ORDER BY
        self.max_workers = int(max_workers)
        self.insert_chunksize = int(insert_chunksize)
        self.overwrite = bool(overwrite)

        # one client per thread to avoid session contention
        self._tlocal = threading.local()

    # ------------- public -------------

    def save_to_clickhouse(self, df: dd.DataFrame, *, overwrite: Optional[bool] = None) -> None:
        """
        Persist a Dask DataFrame into ClickHouse.

        Args:
            df: Dask DataFrame
            overwrite: Optional override for dropping/recreating table
        """
        if not isinstance(df, dd.DataFrame):
            raise TypeError("ClickHouseWriter.save_to_clickhouse expects a dask.dataframe.DataFrame.")

        # small, cheap check: head(1) to detect empty
        head = df.head(1, npartitions=-1, compute=True)
        if head.empty:
            self.logger.info("Dask DataFrame appears empty (head(1) returned 0 rows). Nothing to write.")
            return

        # lazily fill missing values per-partition (no global compute)
        df = df.map_partitions(self._fill_missing_partition, meta=df)

        # (re)create table
        ow = self.overwrite if overwrite is None else bool(overwrite)
        dtypes = df._meta_nonempty.dtypes  # metadata-only types (no compute)
        schema_sql = self._generate_clickhouse_schema(dtypes)
        engine_sql = self._default_engine_sql() if not self.engine else self.engine

        if ow:
            self._command(f"DROP TABLE IF EXISTS {self._ident(self.table)}")
            self.logger.info(f"Dropped table {self.table} (overwrite=True)")

        create_sql = f"CREATE TABLE IF NOT EXISTS {self._ident(self.table)} ({schema_sql}) {engine_sql};"
        self._command(create_sql)
        self.logger.info(f"Ensured table {self.table} exists")

        # write partitions concurrently
        parts = list(df.to_delayed())
        if not parts:
            self.logger.info("No partitions to write.")
            return

        self.logger.info(f"Writing {len(parts)} partitions to ClickHouse (max_workers={self.max_workers})")
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self._write_one_partition, part, idx): idx for idx, part in enumerate(parts)}
            for fut in as_completed(futures):
                idx = futures[fut]
                try:
                    fut.result()
                except Exception as e:
                    self.logger.error(f"Partition {idx} failed: {e}", exc_info=self.debug)
                    raise

        self.logger.info(f"Completed writing {len(parts)} partitions to {self.table}")

    # ------------- schema & types -------------

    def _generate_clickhouse_schema(self, dask_dtypes: pd.Series) -> str:
        cols: Iterable[Tuple[str, Any]] = dask_dtypes.items()
        pieces = []
        for col, dtype in cols:
            ch_type = self._map_dtype(dtype)
            # Use Nullable for non-numeric/string columns that may carry NaN/None,
            # and for datetimes to be safe with missing values.
            if self._should_mark_nullable(dtype):
                ch_type = f"Nullable({ch_type})"
            pieces.append(f"{self._ident(col)} {ch_type}")
        return ", ".join(pieces)

    def _map_dtype(self, dtype: Any) -> str:
        # Handle pandas extension dtypes explicitly
        if isinstance(dtype, pd.Int64Dtype):
            return "Int64"
        if isinstance(dtype, pd.Int32Dtype):
            return "Int32"
        if isinstance(dtype, pd.BooleanDtype):
            return "UInt8"
        if isinstance(dtype, pd.Float64Dtype):
            return "Float64"
        if isinstance(dtype, pd.StringDtype):
            return "String"
        if "datetime64" in str(dtype):
            return "DateTime"

        return self.DTYPE_MAP.get(str(dtype), "String")

    def _should_mark_nullable(self, dtype: Any) -> bool:
        s = str(dtype)
        if isinstance(dtype, (pd.StringDtype, pd.BooleanDtype, pd.Int64Dtype, pd.Int32Dtype, pd.Float64Dtype)):
            return True
        if "datetime64" in s:
            return True
        # object/category almost always nullable
        if s in ("object", "category", "string"):
            return True
        return False

    def _default_engine_sql(self) -> str:
        # minimal MergeTree clause; quote order_by safely
        ob = self.order_by if self.order_by.startswith("(") else f"(`{self.order_by}`)"
        return f"ENGINE = MergeTree ORDER BY {ob}"

    # ------------- partition write -------------

    def _write_one_partition(self, part, index: int) -> None:
        # Compute partition → pandas
        pdf: pd.DataFrame = part.compute()
        if pdf.empty:
            self.logger.debug(f"Partition {index} empty; skipping")
            return

        # Ensure column ordering is stable
        cols = list(pdf.columns)

        # Split into batches (to avoid giant single insert)
        for start in range(0, len(pdf), self.insert_chunksize):
            batch = pdf.iloc[start:start + self.insert_chunksize]
            if batch.empty:
                continue
            self._insert_df(cols, batch)

        self.logger.debug(f"Partition {index} inserted ({len(pdf)} rows)")

    def _insert_df(self, cols: Iterable[str], df: pd.DataFrame) -> None:
        client = self._get_client()
        # clickhouse-connect supports insert_df
        client.insert_df(self.table, df[cols], settings={"async_insert": 1, "wait_end_of_query": 1})

    # ------------- missing values (lazy) -------------

    def _fill_missing_partition(self, pdf: pd.DataFrame) -> pd.DataFrame:
        # Fill by dtype family; leave real NaT for datetimes so Nullable(DateTime) accepts NULL
        for col in pdf.columns:
            s = pdf[col]
            if pd.api.types.is_integer_dtype(s.dtype):
                # pandas nullable IntX supports NA → fill where needed
                if pd.api.types.is_extension_array_dtype(s.dtype):
                    pdf[col] = s.fillna(pd.NA)
                else:
                    pdf[col] = s.fillna(0)
            elif pd.api.types.is_bool_dtype(s.dtype):
                # boolean pandas extension supports NA, ClickHouse uses UInt8; keep NA → Nullable
                pdf[col] = s.fillna(pd.NA)
            elif pd.api.types.is_float_dtype(s.dtype):
                pdf[col] = s.fillna(0.0)
            elif pd.api.types.is_datetime64_any_dtype(s.dtype):
                # keep NaT; ClickHouse Nullable(DateTime) will take NULL
                pass
            else:
                pdf[col] = s.fillna("")
        return pdf

    # ------------- low-level helpers -------------

    def _get_client(self):
        cli = getattr(self._tlocal, "client", None)
        if cli is not None:
            return cli
        cli = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            database=self.database,
            username=self.user,  # clickhouse-connect uses 'username'
            password=self.password,
        )
        self._tlocal.client = cli
        return cli

    def _command(self, sql: str) -> None:
        client = self._get_client()
        client.command(sql)

    @staticmethod
    def _ident(name: str) -> str:
        # minimal identifier quoting
        if name.startswith("`") and name.endswith("`"):
            return name
        return f"`{name}`"

    # ------------- context cleanup -------------

    def _cleanup(self):
        # close client in this thread (the manager calls _cleanup in the owning thread)
        cli = getattr(self._tlocal, "client", None)
        try:
            if cli is not None:
                cli.close()
        except Exception:
            pass
        finally:
            if hasattr(self._tlocal, "client"):
                delattr(self._tlocal, "client")

# from concurrent.futures import ThreadPoolExecutor
# from typing import ClassVar, Dict
#
# import clickhouse_connect
# import pandas as pd
# from clickhouse_driver import Client
# import dask.dataframe as dd
#
# from . import ManagedResource
#
#
# class ClickHouseWriter(ManagedResource):
#     """
#     Provides functionality to write a Dask DataFrame to a ClickHouse database using
#     a specified schema. This class handles the creation of tables, schema generation,
#     data transformation, and data insertion. It ensures compatibility between Dask
#     data types and ClickHouse types.
#
#     :ivar clickhouse_host: Host address of the ClickHouse database.
#     :type clickhouse_host: str
#     :ivar clickhouse_port: Port of the ClickHouse database.
#     :type clickhouse_port: int
#     :ivar clickhouse_dbname: Name of the database to connect to in ClickHouse.
#     :type clickhouse_dbname: str
#     :ivar clickhouse_user: Username for database authentication.
#     :type clickhouse_user: str
#     :ivar clickhouse_password: Password for database authentication.
#     :type clickhouse_password: str
#     :ivar clickhouse_table: Name of the table to store the data in.
#     :type clickhouse_table: str
#     :ivar logger: Logger instance for logging messages.
#     :type logger: logging.Logger
#     :ivar client: Instance of the ClickHouse database client.
#     :type client: clickhouse_connect.Client or None
#     :ivar df: Dask DataFrame to be written into ClickHouse.
#     :type df: dask.dataframe.DataFrame
#     :ivar order_by: Field or column name to use for table ordering.
#     :type order_by: str
#     """
#     dtype_to_clickhouse:  ClassVar[Dict[str, str]] = {
#         'int64': 'Int64',
#         'int32': 'Int32',
#         'float64': 'Float64',
#         'float32': 'Float32',
#         'bool': 'UInt8',
#         'datetime64[ns]': 'DateTime',
#         'object': 'String',
#         'category': 'String',
#     }
#     df: dd.DataFrame
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.clickhouse_host = kwargs.setdefault('host', "localhost")
#         self.clickhouse_port = kwargs.setdefault('port', 8123)
#         self.clickhouse_dbname = kwargs.setdefault('database', 'sibi_data')
#         self.clickhouse_user = kwargs.setdefault('user', 'default')
#         self.clickhouse_password = kwargs.setdefault('password', '')
#         self.clickhouse_table = kwargs.setdefault('table', 'test_sibi_table')
#
#         #self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
#         self.client = None
#         self.order_by = kwargs.setdefault('order_by', 'id')
#
#     def save_to_clickhouse(self, df, **kwargs):
#         self.df = df.copy()
#         self.order_by = kwargs.setdefault('order_by', self.order_by)
#         if len(self.df.head().index) == 0:
#             self.logger.debug("Dataframe is empty")
#             return
#         self._handle_missing_values()
#         self._connect()
#         self._drop_table()
#         self._create_table_from_dask()
#         self._write_data()
#
#     def _connect(self):
#         try:
#             self.client = clickhouse_connect.get_client(
#                 host=self.clickhouse_host,
#                 port=self.clickhouse_port,
#                 database=self.clickhouse_dbname,
#                 user=self.clickhouse_user,
#                 password=self.clickhouse_password
#             )
#             self.logger.debug("Connected to ClickHouse")
#         except Exception as e:
#             self.logger.error(e)
#             raise
#
#     @staticmethod
#     def _generate_clickhouse_schema(dask_dtypes, dtype_map):
#         schema = []
#         for col, dtype in dask_dtypes.items():
#             # Handle pandas nullable types explicitly
#             if isinstance(dtype, pd.Int64Dtype):  # pandas nullable Int64
#                 clickhouse_type = 'Int64'
#             elif isinstance(dtype, pd.Float64Dtype):  # pandas nullable Float64
#                 clickhouse_type = 'Float64'
#             elif isinstance(dtype, pd.BooleanDtype):  # pandas nullable Boolean
#                 clickhouse_type = 'UInt8'
#             elif isinstance(dtype, pd.DatetimeTZDtype) or 'datetime' in str(dtype):  # Nullable datetime
#                 clickhouse_type = 'Nullable(DateTime)'
#             elif isinstance(dtype, pd.StringDtype):  # pandas nullable String
#                 clickhouse_type = 'String'
#             else:
#                 # Default mapping using the provided dtype_map
#                 clickhouse_type = dtype_map.get(str(dtype), 'String')
#             schema.append(f"`{col}` {clickhouse_type}")
#         return ', '.join(schema)
#
#     def _drop_table(self):
#         if self.client:
#             self.client.command('DROP TABLE IF EXISTS {}'.format(self.clickhouse_table))
#             self.logger.debug(f"Dropped table {self.clickhouse_table}")
#
#     def _create_table_from_dask(self, engine=None):
#         if engine is None:
#             engine = f"ENGINE = MergeTree() order by {self.order_by}"
#         dtypes = self.df.dtypes
#         clickhouse_schema = self._generate_clickhouse_schema(dtypes, self.dtype_to_clickhouse)
#         create_table_sql = f"CREATE TABLE IF NOT EXISTS {self.clickhouse_table} ({clickhouse_schema}) {engine};"
#         self.logger.debug(f"Creating table SQL:{create_table_sql}")
#         if self.client:
#             self.client.command(create_table_sql)
#             self.logger.debug("Created table '{}'".format(self.clickhouse_table))
#
#     def _handle_missing_values(self):
#         """
#         Handle missing values in the Dask DataFrame before writing to ClickHouse.
#         """
#         self.logger.debug("Checking for missing values...")
#         missing_counts = self.df.isnull().sum().compute()
#         self.logger.debug(f"Missing values per column:\n{missing_counts}")
#
#         # Replace missing values based on column types
#         def replace_missing_values(df):
#             for col in df.columns:
#                 if pd.api.types.is_integer_dtype(df[col]):
#                     df[col] = df[col].fillna(0)  # Replace NA with 0 for integers
#                 elif pd.api.types.is_float_dtype(df[col]):
#                     df[col] = df[col].fillna(0.0)  # Replace NA with 0.0 for floats
#                 elif pd.api.types.is_bool_dtype(df[col]):
#                     df[col] = df[col].fillna(False)  # Replace NA with False for booleans
#                 else:
#                     df[col] = df[col].fillna('')  # Replace NA with empty string for other types
#             return df
#
#         # Apply replacement
#         self.df = replace_missing_values(self.df)
#         self.logger.debug("Missing values replaced.")
#
#     def _write_data(self):
#         """
#         Writes the Dask DataFrame to a ClickHouse table partition by partition.
#         """
#         if len(self.df.index) == 0:
#             self.logger.debug("No data found. Nothing written.")
#             return
#
#         for i, partition in enumerate(self.df.to_delayed()):
#             try:
#                 # Compute the current partition into a pandas DataFrame
#                 df = partition.compute()
#
#                 if df.empty:
#                     self.logger.debug(f"Partition {i} is empty. Skipping...")
#                     continue
#
#                 self.logger.debug(f"Writing partition {i} with {len(df)} rows to ClickHouse.")
#
#                 # Write the partition to the ClickHouse table
#                 self.client.insert_df(self.clickhouse_table, df)
#             except Exception as e:
#                 self.logger.error(f"Error writing partition {i}: {e}")
#
#     def _write_data_multi_not_working_yet(self):
#         """
#         Writes the Dask DataFrame to a ClickHouse table partition by partition.
#         Ensures a separate client instance is used per thread to avoid session conflicts.
#         """
#         if len(self.df.index) == 0:
#             self.logger.debug("No data found. Nothing written.")
#             return
#
#         def create_client():
#             client = Client(
#                 host=self.clickhouse_host,
#                 port=self.clickhouse_port,
#                 database=self.clickhouse_dbname,
#                 user=self.clickhouse_user,
#                 password=self.clickhouse_password
#             )
#             """
#             Create a new instance of the ClickHouse client for each thread.
#             This avoids session conflicts during concurrent writes.
#             """
#             return client
#
#         def write_partition(partition, index):
#             """
#             Write a single partition to ClickHouse using a separate client instance.
#             """
#             try:
#                 self.logger.debug(f"Starting to process partition {index}")
#                 client = create_client()  # Create a new client for the thread
#
#                 # Compute the Dask partition into a Pandas DataFrame
#                 df = partition.compute()
#                 if df.empty:
#                     self.logger.debug(f"Partition {index} is empty. Skipping...")
#                     return
#
#                 # Convert DataFrame to list of tuples
#                 data = [tuple(row) for row in df.to_numpy()]
#                 columns = df.columns.tolist()
#
#                 # Perform the insert
#                 self.logger.debug(f"Writing partition {index} with {len(df)} rows to ClickHouse.")
#                 client.execute(f"INSERT INTO {self.clickhouse_table} ({', '.join(columns)}) VALUES", data)
#
#             except Exception as e:
#                 self.logger.error(f"Error writing partition {index}: {e}")
#             finally:
#                 if 'client' in locals() and hasattr(client, 'close'):
#                     client.close()
#                     self.logger.debug(f"Closed client for partition {index}")
#
#         try:
#             # Get delayed partitions and enumerate them
#             partitions = self.df.to_delayed()
#             with ThreadPoolExecutor() as executor:
#                 executor.map(write_partition, partitions, range(len(partitions)))
#         except Exception as e:
#             self.logger.error(f"Error during multi-partition write: {e}")
