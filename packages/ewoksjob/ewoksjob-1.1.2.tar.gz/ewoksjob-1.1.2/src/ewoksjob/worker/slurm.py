"""Pool that redirects tasks to a Slurm cluster."""

import weakref
import logging
from functools import wraps
from typing import Callable, Any

try:
    from gevent import GreenletExit
except ImportError:
    GreenletExit = None
from celery.concurrency.gevent import TaskPool as _TaskPool

try:
    from pyslurmutils.concurrent.futures import SlurmRestExecutor
    from pyslurmutils.concurrent.futures import SlurmRestFuture
except ImportError:
    SlurmRestExecutor = None
    SlurmRestFuture = Any

from .executor import set_execute_getter, ExecuteType


__all__ = ("TaskPool",)

logger = logging.getLogger(__name__)


class TaskPool(_TaskPool):
    """SLURM Task Pool."""

    EXECUTOR_OPTIONS = dict()

    def __init__(self, *args, **kwargs):
        if SlurmRestExecutor is None:
            raise RuntimeError("requires pyslurmutils")
        super().__init__(*args, **kwargs)
        self._create_slurm_executor()

    def restart(self):
        self._remove_slurm_executor()
        self._create_slurm_executor()

    def on_stop(self):
        self._remove_slurm_executor()
        super().on_stop()

    def _create_slurm_executor(self):
        self._slurm_executor = SlurmRestExecutor(
            max_workers=self.limit, **self.EXECUTOR_OPTIONS
        )
        _set_slurm_executor(self._slurm_executor)

    def _remove_slurm_executor(self):
        self._slurm_executor.__exit__(None, None, None)
        self._slurm_executor = None


_SLURM_EXECUTOR = None


def _set_slurm_executor(slurm_executor):
    global _SLURM_EXECUTOR
    _SLURM_EXECUTOR = weakref.proxy(slurm_executor)
    set_execute_getter(_get_execute_method)


def _get_execute_method() -> ExecuteType:
    try:
        submit = _SLURM_EXECUTOR.submit
    except (AttributeError, ReferenceError):
        # TaskPool is not instantiated
        return
    return _slurm_execute_method(submit)


_SubmitType = Callable[[Callable, Any, Any], SlurmRestFuture]


def _slurm_execute_method(submit: _SubmitType) -> Callable[[_SubmitType], ExecuteType]:
    """Instead of executing the celery task, forward the ewoks task to Slurm."""

    @wraps(submit)
    def execute(ewoks_task: Callable, *args, **kwargs):
        future = submit(ewoks_task, *args, **kwargs)
        try:
            return future.result()
        except GreenletExit:
            _ensure_cancel_job(future)
            raise

    return execute


def _ensure_cancel_job(future: SlurmRestFuture) -> None:
    not_cancelled = True
    while not_cancelled:
        try:
            logger.info("Cancel Slurm job %s", future.job_id)
            future.abort()
        except GreenletExit:
            continue
        not_cancelled = False
