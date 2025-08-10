import datetime
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Type, Any, Dict, Optional, Union, List, ClassVar

import dask.dataframe as dd
import pandas as pd
from tqdm import tqdm

from . import ManagedResource
from .parquet_saver import ParquetSaver


class DataWrapper(ManagedResource):
    DEFAULT_PRIORITY_MAP: ClassVar[Dict[str, int]] = {
        "overwrite": 1,
        "missing_in_history": 2,
        "existing_but_stale": 3,
        "missing_outside_history": 4,
        "file_is_recent": 0,
    }
    DEFAULT_MAX_AGE_MINUTES: int = 1440
    DEFAULT_HISTORY_DAYS_THRESHOLD: int = 30

    def __init__(
        self,
        dataclass: Type,
        date_field: str,
        data_path: str,
        parquet_filename: str,
        class_params: Optional[Dict] = None,
        load_params: Optional[Dict] = None,
        show_progress: bool = False,
        timeout: float = 30,
        max_threads: int = 3,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.dataclass = dataclass
        self.date_field = date_field
        self.data_path = self._ensure_forward_slash(data_path)
        self.parquet_filename = parquet_filename
        if self.fs is None:
            raise ValueError("DataWrapper requires a File system (fs) to be provided.")
        self.show_progress = show_progress
        self.timeout = timeout
        self.max_threads = max_threads
        self.class_params = class_params or {
            "debug": self.debug,
            "logger": self.logger,
            "fs": self.fs,
            "verbose": self.verbose,
        }
        self.load_params = load_params or {}

        self._lock = threading.Lock()
        self.processed_dates: List[datetime.date] = []
        self.benchmarks: Dict[datetime.date, Dict[str, float]] = {}
        self.mmanifest = kwargs.get("mmanifest", None)
        self.update_planner = kwargs.get("update_planner", None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mmanifest:
            self.mmanifest.save()
        super().__exit__(exc_type, exc_val, exc_tb)
        return False

    @staticmethod
    def _convert_to_date(date: Union[datetime.date, str]) -> datetime.date:
        if isinstance(date, datetime.date):
            return date
        try:
            return pd.to_datetime(date).date()
        except ValueError as e:
            raise ValueError(f"Error converting {date} to datetime: {e}")

    @staticmethod
    def _ensure_forward_slash(path: str) -> str:
        return path.rstrip("/") + "/"

    def process(
        self,
        max_retries: int = 3,
        backoff_base: float = 2.0,
        backoff_jitter: float = 0.1,
        backoff_max: float = 60.0,
    ):
        """
        Execute the update plan with concurrency, retries and exponential backoff.

        Args:
            max_retries: attempts per date.
            backoff_base: base for exponential backoff (delay = base**attempt).
            backoff_jitter: multiplicative jitter factor in [0, backoff_jitter].
            backoff_max: maximum backoff seconds per attempt (before jitter).
        """
        overall_start = time.perf_counter()
        tasks = list(self.update_planner.get_tasks_by_priority())
        if not tasks:
            self.logger.info("No updates required based on the current plan.")
            return

        if self.update_planner.show_progress:
            self.update_planner.show_update_plan()

        for priority, dates in tasks:
            self._execute_task_batch(priority, dates, max_retries, backoff_base, backoff_jitter, backoff_max)

        total_time = time.perf_counter() - overall_start
        if self.processed_dates:
            count = len(self.processed_dates)
            self.logger.info(f"Processed {count} dates in {total_time:.1f}s (avg {total_time / count:.1f}s/date)")
            if self.update_planner.show_progress:
                self.show_benchmark_summary()

    def _execute_task_batch(
        self,
        priority: int,
        dates: List[datetime.date],
        max_retries: int,
        backoff_base: float,
        backoff_jitter: float,
        backoff_max: float,
    ):
        desc = f"Processing {self.dataclass.__name__}, priority: {priority}"
        max_thr = min(len(dates), self.max_threads)
        self.logger.info(f"Executing {len(dates)} tasks with priority {priority} using {max_thr} threads.")

        with ThreadPoolExecutor(max_workers=max_thr) as executor:
            futures = {
                executor.submit(
                    self._process_date_with_retry, date, max_retries, backoff_base, backoff_jitter, backoff_max
                ): date
                for date in dates
            }
            iterator = as_completed(futures)
            if self.show_progress:
                iterator = tqdm(iterator, total=len(futures), desc=desc)

            for future in iterator:
                try:
                    future.result(timeout=self.timeout)
                except Exception as e:
                    self.logger.error(f"Permanent failure for {futures[future]}: {e}")

    def _process_date_with_retry(
        self,
        date: datetime.date,
        max_retries: int,
        backoff_base: float,
        backoff_jitter: float,
        backoff_max: float,
    ):
        for attempt in range(max_retries):
            try:
                self._process_single_date(date)
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    base_delay = min(backoff_base ** attempt, backoff_max)
                    delay = base_delay * (1 + random.uniform(0.0, max(0.0, backoff_jitter)))
                    self.logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {date}: {e} (sleep {delay:.2f}s)"
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed processing {date} after {max_retries} attempts.")

    def _process_single_date(self, date: datetime.date):
        path = f"{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/"
        self.logger.debug(f"Processing date {date.isoformat()} for {path}")
        if path in self.update_planner.skipped and self.update_planner.ignore_missing:
            self.logger.debug(f"Skipping {date} as it exists in the skipped list")
            return
        full_path = f"{path}{self.parquet_filename}"

        overall_start = time.perf_counter()
        try:
            load_start = time.perf_counter()
            date_filter = {f"{self.date_field}__date": {date.isoformat()}}
            self.logger.debug(f"Loading data for {date} with filter: {date_filter}")

            local_load_params = self.load_params.copy()
            local_load_params.update(date_filter)

            with self.dataclass(**self.class_params) as local_class_instance:
                df = local_class_instance.load(**local_load_params)  # expected to be Dask
                load_time = time.perf_counter() - load_start

                if hasattr(local_class_instance, "total_records"):
                    total_records = int(local_class_instance.total_records)
                    self.logger.debug(f"Total records loaded: {total_records}")

                    if total_records == 0:
                        if self.mmanifest:
                            self.mmanifest.record(full_path=path)
                        self.logger.info(f"No data found for {full_path}. Logged to missing manifest.")
                        return

                    if total_records < 0:
                        self.logger.warning(f"Negative record count ({total_records}) for {full_path}.")
                        return

                save_start = time.perf_counter()
                parquet_params = {
                    "df_result": df,
                    "parquet_storage_path": path,
                    "fs": self.fs,
                    "logger": self.logger,
                    "debug": self.debug,
                }
                with ParquetSaver(**parquet_params) as ps:
                    ps.save_to_parquet(self.parquet_filename, overwrite=True)
                save_time = time.perf_counter() - save_start

                total_time = time.perf_counter() - overall_start
                self.benchmarks[date] = {
                    "load_duration": load_time,
                    "save_duration": save_time,
                    "total_duration": total_time,
                }
                self._log_success(date, total_time, full_path)

        except Exception as e:
            self._log_failure(date, e)
            raise

    def _log_success(self, date: datetime.date, duration: float, path: str):
        self.logger.info(f"Completed {date} in {duration:.1f}s | Saved to {path}")
        self.processed_dates.append(date)

    def _log_failure(self, date: datetime.date, error: Exception):
        self.logger.error(f"Failed processing {date}: {error}")

    def show_benchmark_summary(self):
        if not self.benchmarks:
            self.logger.info("No benchmarking data to show")
            return
        df_bench = pd.DataFrame.from_records([{"date": d, **m} for d, m in self.benchmarks.items()])
        df_bench = df_bench.set_index("date").sort_index(ascending=not self.update_planner.reverse_order)
        self.logger.info(f"Benchmark Summary:\n {self.dataclass.__name__}\n" + df_bench.to_string())

# import datetime
# import threading
# import time
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from typing import Type, Any, Dict, Optional, Union, List, ClassVar
#
# import pandas as pd
# from tqdm import tqdm
#
# from . import ManagedResource
# from .parquet_saver import ParquetSaver
#
#
# class DataWrapper(ManagedResource):
#     DEFAULT_PRIORITY_MAP: ClassVar[Dict[str, int]] = {
#         "overwrite": 1,
#         "missing_in_history": 2,
#         "existing_but_stale": 3,
#         "missing_outside_history": 4,
#         "file_is_recent": 0
#     }
#     DEFAULT_MAX_AGE_MINUTES: int = 1440
#     DEFAULT_HISTORY_DAYS_THRESHOLD: int = 30
#
#     def __init__(
#             self,
#             dataclass: Type,
#             date_field: str,
#             data_path: str,
#             parquet_filename: str,
#             class_params: Optional[Dict] = None,
#             load_params: Optional[Dict] = None,
#             show_progress: bool = False,
#             timeout: float = 30,
#             max_threads: int = 3,
#             **kwargs: Any,
#     ):
#         super().__init__(**kwargs)
#         self.dataclass = dataclass
#         self.date_field = date_field
#         self.data_path = self._ensure_forward_slash(data_path)
#         self.parquet_filename = parquet_filename
#         if self.fs is None:
#             raise ValueError("Datawrapper requires a File system (fs) to be provided .")
#         self.show_progress = show_progress
#         self.timeout = timeout
#         self.max_threads = max_threads
#         self.class_params = class_params or {
#             'debug': self.debug,
#             'logger': self.logger,
#             'fs': self.fs,
#             'verbose': self.verbose,
#         }
#         self.load_params = load_params or {}
#
#         self._lock = threading.Lock()
#         self.processed_dates: List[datetime.date] = []
#         self.benchmarks: Dict[datetime.date, Dict[str, float]] = {}
#         self.mmanifest = kwargs.get("mmanifest", None)
#         self.update_planner = kwargs.get("update_planner", None)
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """Context manager exit"""
#         if self.mmanifest:
#             self.mmanifest.save()
#         super().__exit__(exc_type, exc_val, exc_tb)
#         return False
#
#     @staticmethod
#     def _convert_to_date(date: Union[datetime.date, str]) -> datetime.date:
#         if isinstance(date, datetime.date):
#             return date
#         try:
#             return pd.to_datetime(date).date()
#         except ValueError as e:
#             raise ValueError(f"Error converting {date} to datetime: {e}")
#
#     @staticmethod
#     def _ensure_forward_slash(path: str) -> str:
#         return path.rstrip('/') + '/'
#
#     def process(self, max_retries: int = 3):
#         """Process updates with priority-based execution, retries, benchmarking and progress updates"""
#         overall_start = time.perf_counter()
#         tasks = list(self.update_planner.get_tasks_by_priority())
#         if not tasks:
#             self.logger.info("No updates required based on the current plan.")
#             return
#
#         if self.update_planner.show_progress:
#             self.update_planner.show_update_plan()
#
#         for priority, dates in tasks:
#             self._execute_task_batch(priority, dates, max_retries)
#
#         total_time = time.perf_counter() - overall_start
#         if self.processed_dates:
#             count = len(self.processed_dates)
#             self.logger.info(f"Processed {count} dates in {total_time:.1f}s (avg {total_time / count:.1f}s/date)")
#             if self.update_planner.show_progress:
#                 self.show_benchmark_summary()
#
#     def _execute_task_batch(self, priority: int, dates: List[datetime.date], max_retries: int):
#         """Executes a single batch of tasks (dates) using a thread pool."""
#         desc = f"Processing {self.dataclass.__name__}, priority: {priority}"
#         max_thr = min(len(dates), self.max_threads)
#         self.logger.info(f"Executing {len(dates)} tasks with priority {priority} using {max_thr} threads.")
#
#         with ThreadPoolExecutor(max_workers=max_thr) as executor:
#             futures = {executor.submit(self._process_date_with_retry, date, max_retries): date for date in dates}
#             iterator = as_completed(futures)
#             if self.show_progress:
#                 iterator = tqdm(iterator, total=len(futures), desc=desc)
#
#             for future in iterator:
#                 try:
#                     future.result(timeout=self.timeout)
#                 except Exception as e:
#                     self.logger.error(f"Permanent failure for {futures[future]}: {e}")
#
#     def _process_date_with_retry(self, date: datetime.date, max_retries: int):
#         """Wrapper to apply retry logic to single date processing."""
#         for attempt in range(max_retries):
#             try:
#                 self._process_single_date(date)
#                 return
#             except Exception as e:
#                 if attempt < max_retries - 1:
#                     self.logger.warning(f"Retry {attempt + 1}/{max_retries} for {date}: {e}")
#                     time.sleep(2 ** attempt)  # Exponential backoff
#                 else:
#                     self.logger.error(f"Failed processing {date} after {max_retries} attempts.")
#                     # raise
#
#     def _process_single_date(self, date: datetime.date):
#         """Core date processing logic with load/save timing and thread reporting"""
#         path = f"{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/"
#         self.logger.debug(f"Processing date {date.isoformat()} for {path}")
#         if path in self.update_planner.skipped and self.update_planner.ignore_missing:
#             self.logger.debug(f"Skipping {date} as it exists in the skipped list")
#             return
#         full_path = f"{path}{self.parquet_filename}"
#
#         # thread_name = threading.current_thread().name
#         # self.logger.debug(f"[{thread_name}] Executing date: {date} -> saving to: {full_path}")
#
#         overall_start = time.perf_counter()
#         try:
#             load_start = time.perf_counter()
#             date_filter = {f"{self.date_field}__date": {date.isoformat()}}
#             self.logger.debug(f"Loading data for {date} with filter: {date_filter}")
#             # Load data using the dataclass with the provided date filter
#             # Create a copy to avoid mutating the shared instance dictionary
#             local_load_params = self.load_params.copy()
#             local_load_params.update(date_filter)
#             with self.dataclass(**self.class_params) as local_class_instance:
#                 df = local_class_instance.load(**local_load_params)
#                 load_time = time.perf_counter() - load_start
#
#                 if hasattr(local_class_instance, "total_records"):
#                     self.logger.debug(
#                         f"Total records loaded by {local_class_instance.__class__.__name__}: {local_class_instance.total_records}")
#                     if int(local_class_instance.total_records) == 0:  # If no records were loaded but not due to an error
#                         if self.mmanifest:
#                             self.mmanifest.record(
#                             full_path=path
#                         )
#                         self.logger.info(f"No data found for {full_path}. Logged to missing manifest.")
#                     elif int(local_class_instance.total_records) < 0:
#                         self.logger.warning(
#                             f"Negative record count ({local_class_instance.total_records}) for {full_path}. "
#                             "This may indicate an error in the data loading process."
#                         )
#                     else:
#                         save_start = time.perf_counter()
#                         parquet_params ={
#                             "df_result": df,
#                             "parquet_storage_path": path,
#                             "fs": self.fs,
#                             "logger": self.logger,
#                             "debug": self.debug,
#                         }
#                         with ParquetSaver(**parquet_params) as ps:
#                             ps.save_to_parquet(self.parquet_filename, overwrite=True)
#                         save_time = time.perf_counter() - save_start
#
#                         total_time = time.perf_counter() - overall_start
#                         self.benchmarks[date] = {
#                             "load_duration": load_time,
#                             "save_duration": save_time,
#                             "total_duration": total_time
#                         }
#                         self._log_success(date, total_time, full_path)
#         except Exception as e:
#             self._log_failure(date, e)
#             raise
#
#     def _log_success(self, date: datetime.date, duration: float, path: str):
#         msg = f"Completed {date} in {duration:.1f}s | Saved to {path}"
#         self.logger.info(msg)
#         self.processed_dates.append(date)
#
#     def _log_failure(self, date: datetime.date, error: Exception):
#         msg = f"Failed processing {date}: {error}"
#         self.logger.error(msg)
#
#     def show_benchmark_summary(self):
#         """Display a summary of load/save timings per date"""
#         if not self.benchmarks:
#             self.logger.info("No benchmarking data to show")
#             return
#         df_bench = pd.DataFrame.from_records([{"date": d, **m} for d, m in self.benchmarks.items()])
#         df_bench = df_bench.set_index("date").sort_index(ascending=not self.update_planner.reverse_order)
#         self.logger.info(f"Benchmark Summary:\n {self.dataclass.__name__}\n" + df_bench.to_string())
