from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Dict

from sibi_dst.utils import ManagedResource


@dataclass(slots=True)
class _RetryCfg:
    attempts: int = 3
    backoff_base: float = 2.0
    backoff_max: float = 60.0
    jitter: float = 0.15


_ORCHESTRATOR_KEYS = {
    "retry_attempts",
    "backoff_base",
    "backoff_max",
    "backoff_jitter",
    "update_timeout_seconds",  # accepted but unused in pure-threads version
    "max_workers",
    "priority_fn",
    "artifact_class_kwargs",
}


def _default_artifact_kwargs(resource: ManagedResource) -> Dict[str, Any]:
    return {
        "logger": resource.logger,
        "debug": resource.debug,
        "fs": resource.fs,
        "verbose": resource.verbose,
    }


class ArtifactUpdaterMultiWrapperThreaded(ManagedResource):
    """
    Backward-compatible threaded orchestrator.
    """

    def __init__(
        self,
        wrapped_classes: Dict[str, Sequence[Type]],
        *,
        max_workers: int = 4,
        retry_attempts: int = 3,
        backoff_base: float = 2.0,
        backoff_max: float = 60.0,
        backoff_jitter: float = 0.15,
        priority_fn: Optional[Callable[[Type], int]] = None,
        artifact_class_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.wrapped_classes = wrapped_classes
        self.max_workers = int(max_workers)
        self.priority_fn = priority_fn
        self._retry = _RetryCfg(
            attempts=int(retry_attempts),
            backoff_base=float(backoff_base),
            backoff_max=float(backoff_max),
            jitter=float(backoff_jitter),
        )
        self.artifact_class_kwargs = {
            **_default_artifact_kwargs(self),
            **(artifact_class_kwargs or {}),
        }
        self.completion_secs: Dict[str, float] = {}
        self.failed: List[str] = []

    def _classes_for(self, period: str) -> List[Type]:
        try:
            classes = list(self.wrapped_classes[period])
        except KeyError:
            raise ValueError(f"Unsupported period '{period}'.")
        if not classes:
            raise ValueError(f"No artifact classes configured for period '{period}'.")
        if self.priority_fn:
            try:
                classes.sort(key=self.priority_fn)
            except Exception as e:
                self.logger.warning(f"priority_fn failed; using listed order: {e}")
        return classes

    @staticmethod
    def _split_kwargs(raw: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        orch: Dict[str, Any] = {}
        art: Dict[str, Any] = {}
        for k, v in raw.items():
            if k in _ORCHESTRATOR_KEYS:
                orch[k] = v
            else:
                art[k] = v
        return orch, art

    def _run_one(self, cls: Type, period: str, artifact_kwargs: Dict[str, Any]) -> str:
        name = cls.__name__
        start = time.monotonic()
        for attempt in range(1, self._retry.attempts + 1):
            try:
                with ExitStack() as stack:
                    inst = cls(**self.artifact_class_kwargs)
                    inst = stack.enter_context(inst)
                    inst.update_parquet(period=period, **artifact_kwargs)
                self.completion_secs[name] = time.monotonic() - start
                return name
            except Exception as e:
                if attempt < self._retry.attempts:
                    delay = min(self._retry.backoff_base ** (attempt - 1), self._retry.backoff_max)
                    delay *= 1 + random.uniform(0, self._retry.jitter)
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"{name} failed after {self._retry.attempts} attempts: {e}") from e

    def update_data(self, period: str, **kwargs: Any) -> None:
        # Split kwargs to preserve backward compatibility
        _, artifact_kwargs = self._split_kwargs(kwargs)

        self.completion_secs.clear()
        self.failed.clear()

        classes = self._classes_for(period)
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            fut2name = {pool.submit(self._run_one, cls, period, dict(artifact_kwargs)): cls.__name__ for cls in classes}
            for fut in as_completed(fut2name):
                name = fut2name[fut]
                try:
                    fut.result()
                    self.logger.info(f"✅ {name} ({period}) in {self.completion_secs[name]:.2f}s")
                except Exception as e:
                    self.failed.append(name)
                    self.logger.error(f"✖️  {name} permanently failed: {e}")

        self.logger.info(
            f"Artifacts processed: total={len(classes)}, "
            f"completed={len(self.completion_secs)}, failed={len(self.failed)}"
        )

    def get_update_status(self) -> Dict[str, Any]:
        done = set(self.completion_secs)
        fail = set(self.failed)
        all_names = {c.__name__ for v in self.wrapped_classes.values() for c in v}
        return {
            "total": len(all_names),
            "completed": sorted(done),
            "failed": sorted(fail),
            "pending": sorted(all_names - done - fail),
            "completion_times": dict(self.completion_secs),
        }

import asyncio
import random
from contextlib import ExitStack
from typing import Any, Callable, Dict, List, Optional, Sequence, Type

class ArtifactUpdaterMultiWrapperAsync(ManagedResource):
    """
    Backward-compatible async orchestrator.

    Public API preserved:
      • __init__(wrapped_classes, *, max_workers=..., retry_attempts=..., backoff_*=..., update_timeout_seconds=..., priority_fn=..., artifact_class_kwargs=..., **kwargs)
      • update_data(period, **kwargs)  -> forwards only artifact-friendly kwargs to update_parquet
    """

    def __init__(
        self,
        wrapped_classes: Dict[str, Sequence[Type]],
        *,
        max_workers: int = 3,
        retry_attempts: int = 3,
        update_timeout_seconds: int = 600,
        backoff_base: float = 2.0,
        backoff_max: float = 60.0,
        backoff_jitter: float = 0.15,
        priority_fn: Optional[Callable[[Type], int]] = None,
        artifact_class_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.wrapped_classes = wrapped_classes
        self.max_workers = int(max_workers)
        self.update_timeout_seconds = int(update_timeout_seconds)
        self.priority_fn = priority_fn

        self._retry = _RetryCfg(
            attempts=int(retry_attempts),
            backoff_base=float(backoff_base),
            backoff_max=float(backoff_max),
            jitter=float(backoff_jitter),
        )

        self.artifact_class_kwargs = {
            **_default_artifact_kwargs(self),
            **(artifact_class_kwargs or {}),
        }

        self.completion_secs: Dict[str, float] = {}
        self.failed: List[str] = []

    # ---- internals -----------------------------------------------------------

    def _classes_for(self, period: str) -> List[Type]:
        try:
            classes = list(self.wrapped_classes[period])
        except KeyError:
            raise ValueError(f"Unsupported period '{period}'.")
        if not classes:
            raise ValueError(f"No artifact classes configured for period '{period}'.")
        if self.priority_fn:
            try:
                classes.sort(key=self.priority_fn)
            except Exception as e:
                self.logger.warning(f"priority_fn failed; using listed order: {e}")
        return classes

    @staticmethod
    def _split_kwargs(raw: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Split kwargs into (orchestrator-only, artifact-forwarded).
        Keeps backward compatibility: callers can pass all knobs in one dict.
        """
        orch: Dict[str, Any] = {}
        art: Dict[str, Any] = {}
        for k, v in raw.items():
            if k in _ORCHESTRATOR_KEYS:
                orch[k] = v
            else:
                art[k] = v
        return orch, art

    async def _run_one(self, cls: Type, period: str, sem: asyncio.Semaphore, artifact_kwargs: Dict[str, Any]) -> None:
        name = cls.__name__
        async with sem:
            start = asyncio.get_running_loop().time()
            for attempt in range(1, self._retry.attempts + 1):
                try:
                    # Run sync context + method in thread
                    def _sync_block() -> None:
                        with ExitStack() as stack:
                            inst = cls(**self.artifact_class_kwargs)
                            inst = stack.enter_context(inst)
                            inst.update_parquet(period=period, **artifact_kwargs)

                    await asyncio.wait_for(
                        asyncio.to_thread(_sync_block),
                        timeout=self.update_timeout_seconds,
                    )
                    dt_secs = asyncio.get_running_loop().time() - start
                    self.completion_secs[name] = dt_secs
                    self.logger.info(f"✅ {name} ({period}) in {dt_secs:.2f}s")
                    return

                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout in {name} attempt {attempt}/{self._retry.attempts}")
                except Exception as e:
                    self.logger.error(
                        f"{name} attempt {attempt}/{self._retry.attempts} failed: {e}",
                        exc_info=self.debug,
                    )

                if attempt < self._retry.attempts:
                    delay = min(self._retry.backoff_base ** (attempt - 1), self._retry.backoff_max)
                    delay *= 1 + random.uniform(0, self._retry.jitter)
                    await asyncio.sleep(delay)

            self.failed.append(name)
            self.logger.error(f"✖️  {name} permanently failed")

    # ---- public API ----------------------------------------------------------

    async def update_data(self, period: str, **kwargs: Any) -> None:
        """
        Backward-compatible:
          - Accepts orchestrator knobs in kwargs (we consume them).
          - Forwards only artifact-friendly kwargs to update_parquet.
        """
        # split kwargs; ignore any runtime attempts to mutate orchestrator config mid-call
        _, artifact_kwargs = self._split_kwargs(kwargs)

        self.completion_secs.clear()
        self.failed.clear()

        classes = self._classes_for(period)
        sem = asyncio.Semaphore(self.max_workers)
        tasks = [asyncio.create_task(self._run_one(cls, period, sem, dict(artifact_kwargs))) for cls in classes]

        for t in asyncio.as_completed(tasks):
            try:
                await t
            except asyncio.CancelledError:
                for rest in tasks:
                    rest.cancel()
                raise

        self.logger.info(
            f"Artifacts processed: total={len(classes)}, "
            f"completed={len(self.completion_secs)}, failed={len(self.failed)}"
        )

    # Optional helper
    def get_update_status(self) -> Dict[str, Any]:
        done = set(self.completion_secs)
        fail = set(self.failed)
        all_names = {c.__name__ for v in self.wrapped_classes.values() for c in v}
        return {
            "total": len(all_names),
            "completed": sorted(done),
            "failed": sorted(fail),
            "pending": sorted(all_names - done - fail),
            "completion_times": dict(self.completion_secs),
        }