import abc
import threading
import weakref
from typing import Self, Optional, Callable

import fsspec

from sibi_dst.utils import Logger


class ManagedResource(abc.ABC):
    """
    Boilerplate ABC for components that manage a logger and an fsspec filesystem
    with sync/async lifecycle helpers.
    """

    def __init__(
        self,
        *,
        verbose: bool = False,
        debug: bool = False,
        logger: Optional[Logger] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None,
        fs_factory: Optional[Callable[[], fsspec.AbstractFileSystem]] = None,
        **_: object,
    ) -> None:
        self.verbose = verbose
        self.debug = debug

        # --- Logger ownership ---
        if logger is None:
            self.logger = Logger.default_logger(logger_name=self.__class__.__name__)
            self._owns_logger = True
            self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)
        else:
            self.logger = logger
            self._owns_logger = False
            # Do NOT mutate external logger level

        # --- FS ownership ---
        self._owns_fs = fs is None
        if fs is not None:
            self.fs: Optional[fsspec.AbstractFileSystem] = fs
        elif fs_factory is not None:
            created = fs_factory()
            if not isinstance(created, fsspec.AbstractFileSystem):
                raise TypeError(
                    f"fs_factory() must return fsspec.AbstractFileSystem, got {type(created)!r}"
                )
            self.fs = created
        else:
            self.fs = None  # optional; subclasses may not need fs

        self._is_closed = False
        self._close_lock = threading.RLock()

        # register a best-effort finalizer
        self._finalizer = weakref.finalize(self, self._finalize_silent)

        # Early debug
        self.logger.debug("Component %s initialized.", self.__class__.__name__)

    # ---------- Introspection ----------
    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @property
    def closed(self) -> bool:  # alias
        return self._is_closed

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        logger_status = "own" if self._owns_logger else "external"
        fs_status = "none" if self.fs is None else ("own" if self._owns_fs else "external")
        return f"<{class_name} debug={self.debug} logger={logger_status} fs={fs_status}>"

    # ---------- Hooks for subclasses ----------
    def _cleanup(self) -> None:
        """Sync cleanup for resources created BY THE SUBCLASS."""
        return

    async def _acleanup(self) -> None:
        """Async cleanup for resources created BY THE SUBCLASS."""
        return

    # ---------- Owned resource shutdown ----------
    def _shutdown_logger(self) -> None:
        if not self._owns_logger:
            self.logger.debug("%s: skipping logger shutdown (not owned).", self.__class__.__name__)
            return
        self.logger.debug("%s: shutting down owned logger.", self.__class__.__name__)
        try:
            self.logger.shutdown()
        except Exception:  # keep shutdown robust
            pass

    def _shutdown_owned_resources(self) -> None:
        # fsspec FS usually has no close; if it does, call it.
        if self._owns_fs and self.fs is not None:
            self.logger.debug("%s: releasing owned fsspec filesystem.", self.__class__.__name__)
            close = getattr(self.fs, "close", None)
            try:
                if callable(close):
                    close()
            finally:
                self.fs = None
        else:
            self.logger.debug(
                "%s: skipping fs shutdown (not owned or none).", self.__class__.__name__
            )
        self._shutdown_logger()

    async def _ashutdown_owned_resources(self) -> None:
        # No async close in fsspec by default, keep parity with sync
        if self._owns_fs and self.fs is not None:
            self.logger.debug("%s: releasing owned fsspec filesystem (async).", self.__class__.__name__)
            close = getattr(self.fs, "close", None)
            try:
                if callable(close):
                    close()
            finally:
                self.fs = None
        self._shutdown_logger()

    # ---------- Public lifecycle ----------
    def close(self) -> None:
        with self._close_lock:
            if self._is_closed:
                return
            self.logger.debug("Closing component %s...", self.__class__.__name__)
            try:
                self._cleanup()
            except Exception:
                # log and propagate — callers need to know
                self.logger.error(
                    "Error during %s._cleanup()", self.__class__.__name__, exc_info=True
                )
                raise
            finally:
                self._is_closed = True
                self._shutdown_owned_resources()
                self.logger.debug("Component %s closed.", self.__class__.__name__)

    async def aclose(self) -> None:
        with self._close_lock:
            if self._is_closed:
                return
            self.logger.debug("Asynchronously closing component %s...", self.__class__.__name__)
        # run subclass async cleanup outside of lock
        try:
            await self._acleanup()
        except Exception:
            self.logger.error(
                "Error during %s._acleanup()", self.__class__.__name__, exc_info=True
            )
            raise
        finally:
            with self._close_lock:
                self._is_closed = True
            await self._ashutdown_owned_resources()
            self.logger.debug("Async component %s closed.", self.__class__.__name__)

    # ---------- Context managers ----------
    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False  # propagate exceptions

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        await self.aclose()
        return False

    # ---------- Finalizer ----------
    def _finalize_silent(self) -> None:
        # Best-effort, no logging (avoid noisy GC-time logs).
        try:
            if not self._is_closed:
                self.close()
        except Exception:
            # absolutely swallow — GC context
            pass

# import abc
# from typing import Self, Optional, Callable, Any
#
# import fsspec
#
# from sibi_dst.utils import Logger
#
#
# class ManagedResource(abc.ABC):
#     """
#     A unified boilerplate ABC for creating manageable components.
#
#     It provides integrated ownership and lifecycle management for a custom
#     logger and a fsspec filesystem client, with full async support.
#     """
#
#     def __init__(
#             self,
#             *,
#             verbose: bool = False,
#             debug: bool = False,
#             logger: Optional[Logger] = None,
#             fs: Optional[fsspec.AbstractFileSystem] = None,
#             fs_factory: Optional[Callable[[], Any]] = None,
#             **kwargs: Any,
#     ) -> None:
#         self.debug = debug
#         self.verbose = verbose
#
#         self._is_closed = False
#         self._owns_logger: bool
#         self.fs, self._owns_fs = (fs, False) if fs else (None, True)
#         if self._owns_fs and fs_factory:
#             self.fs = fs_factory
#         self.logger, self._owns_logger = (logger, False) if logger else (
#             Logger.default_logger(logger_name=f"{self.__class__.__name__}"), True)
#         self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)
#         self.logger.debug(f"Component: {self.__class__.__name__} initialized.")
#
#     @property
#     def is_closed(self) -> bool:
#         return self._is_closed
#
#     # Private methods for cleanup in the subclass
#     def _cleanup(self) -> None:
#         """Cleanup for resources created BY THE SUBCLASS."""
#         pass
#
#     async def _acleanup(self) -> None:
#         """Async cleanup for resources created BY THE SUBCLASS."""
#         pass
#
#     # --- Private Shutdown Helpers ---
#     def _shutdown_logger(self) -> None:
#         # Your provided logger shutdown logic
#         if not self._owns_logger:
#             self.logger.debug(f"{self.__class__.__name__} is skipping logger shutdown (not owned).")
#             return
#         self.logger.debug(f"{self.__class__.__name__} is shutting down self-managed logger.")
#         self.logger.shutdown()
#
#     def _shutdown_owned_resources(self) -> None:
#         if self._owns_fs and isinstance(self.fs, fsspec.AbstractFileSystem):
#             self.logger.debug(f"{self.__class__.__name__} is shutting down self-managed fsspec client synchronously.")
#             del self.fs
#         else:
#             self.logger.debug(
#                 f"{self.__class__.__name__} is skipping fsspec client shutdown (not owned or not an fsspec client).")
#         self._shutdown_logger()
#
#     async def _ashutdown_owned_resources(self) -> None:
#         """Internal method to shut down all owned resources ASYNCHRONOUSLY."""
#
#         if self._owns_fs and isinstance(self.fs, fsspec.AbstractFileSystem):
#             self.logger.debug(f"{self.__class__.__name__} is shutting down self-managed fsspec client asynchronously.")
#             del self.fs
#
#         self._shutdown_logger()
#
#     # Methods for Cleanup ---
#     def close(self) -> None:
#         if self._is_closed: return
#         self.logger.debug(f"Closing component...{self.__class__.__name__}")
#         try:
#             self._cleanup()
#         except Exception as e:
#             self.logger.error(f"Error during subclass {self.__class__.__name__} cleanup: {e}", exc_info=True)
#             raise
#         finally:
#             self._is_closed = True
#             self._shutdown_owned_resources()
#             self.logger.debug(f"Component {self.__class__.__name__} closed successfully.")
#
#     async def aclose(self) -> None:
#         if self._is_closed: return
#         self.logger.debug(f"Asynchronously closing component...{self.__class__.__name__}")
#         try:
#             await self._acleanup()
#         except Exception as e:
#             self.logger.error(f"Error during async subclass cleanup: {e}", exc_info=True)
#             raise
#         finally:
#             self._is_closed = True
#             await self._ashutdown_owned_resources()
#             self.logger.debug(f"Async Component {self.__class__.__name__} closed successfully.")
#
#     def __repr__(self) -> str:
#         """Return a string representation of the ManagedResource."""
#         # Dynamically get the name of the class or subclass
#         class_name = self.__class__.__name__
#
#         # Determine the status of the logger and filesystem
#         logger_status = "own" if self._owns_logger else "external"
#         fs_status = "own" if self._owns_fs else "external"
#         return (
#             f"<{class_name} debug={self.debug}, "
#             f"logger='{logger_status}', fs='{fs_status}'>"
#         )
#
#     # --- Context Management and Destruction ---
#     def __enter__(self) -> Self:
#         return self
#
#     def __exit__(self, *args) -> None:
#         self.close()
#
#     async def __aenter__(self) -> Self:
#         return self
#
#     async def __aexit__(self, *args) -> None:
#         await self.aclose()
#
#     def __del__(self) -> None:
#         if not self._is_closed:
#             self.logger.critical(f"CRITICAL: Component {self!r} was not closed properly.")
