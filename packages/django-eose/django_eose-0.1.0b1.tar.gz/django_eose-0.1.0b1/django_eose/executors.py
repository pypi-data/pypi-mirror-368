from concurrent.futures import ThreadPoolExecutor
from multiprocessing import get_context, cpu_count
from typing import Iterable, Callable
import sys

def run_sync(iterable: Iterable, func: Callable, chunksize: int):
    for item in iterable:
        yield func(item)

def run_threads(iterable: Iterable, func: Callable, chunksize: int, max_workers: int | None = None):
    max_workers = max_workers or cpu_count()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for result in ex.map(func, iterable, chunksize=chunksize):
            yield result

def run_processes(iterable: Iterable, func: Callable, chunksize: int, max_workers: int | None = None):
    if sys.platform.startswith("linux"):
        # Use "fork" for better performance on Linux
        start_method = "fork"
    else:
        # Use "spawn" for Windows compatibility
        start_method = "spawn"

    ctx = get_context(start_method)
    max_workers = max_workers or cpu_count()
    with ctx.Pool(processes=max_workers) as pool:
        for result in pool.imap_unordered(func, iterable, chunksize=chunksize):
            yield result

def get_executor(mode: str):
    if mode == "processes":
        return run_processes
    if mode == "threads":
        return run_threads
    if mode == "sync":
        return run_sync
    raise ValueError(f"Executor inválido: {mode}")
