import time
from contextlib import contextmanager
from celery import shared_task
from django.core.cache import cache
from .crossbelt_sync_sorting_history import CrossbeltSyncSortingHistory


@contextmanager
def task_lock_by_cache(lock_id):
    lock_expire = 5*60  # lock 5 minutes
    timeout_at = time.monotonic() + lock_expire - 3
    status = cache.add(key=lock_id, value="locked", timeout=lock_expire)
    try:
        yield status
    finally:
        print(time.monotonic(), timeout_at, status)
        if time.monotonic() < timeout_at and status:
            cache.delete(lock_id)


@shared_task(name="crossbelt_sync_sorting_history")
def crossbelt_sync_sorting_history():
    """
        Sync data from crossbelt_sorting_history -> kafka -> wms central
    """
    # Ensuring a task is only executed one at a time with cache
    lock_id = "task.crossbelt_sync_sorting_history"
    count_sync = 0
    with task_lock_by_cache(lock_id) as acquired:
        if acquired:
            sync_task = CrossbeltSyncSortingHistory()
            count_sync = sync_task.run_sync()
        else:
            return "Task already running!"
    return "Sync {} finished!".format(count_sync)
