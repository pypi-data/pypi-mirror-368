import asyncio
from typing import Any, Callable, Iterable

import tiktoken


def remove_blank_lines(text: str) -> str:
    return '\n'.join(line for line in text.splitlines() if line.strip())


def first_element(iterable: Iterable) -> Any:
    return next(iter(iterable))


def num_tokens_from_text(content: str, encoding_name: str = 'o200k_base') -> int:
    return len(tiktoken.get_encoding(encoding_name).encode(content))


def call_async_func(func: Callable, *args, **kwargs) -> Any:
    """
    Call an async function in a synchronous context.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        raise RuntimeError("Cannot call async function from a running event loop")
    return loop.run_until_complete(func(*args, **kwargs))


def ensure_folder(folder_path: str) -> None:
    """
    Ensure that a folder exists, creating it if necessary.
    """
    import os

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
