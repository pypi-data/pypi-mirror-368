# agentik/utils.py
import time
import functools
import logging
from typing import Callable, Any, Optional

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except Exception:  # fallback if colorama not installed
    class _F: RESET_ALL = ""; CYAN=""; GREEN=""
    Fore = _F(); Style = _F()

def get_logger(name: str = "agentik") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f"{getattr(Fore, 'CYAN', '')}[%(asctime)s]{getattr(Style, 'RESET_ALL', '')} %(levelname)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def retry(retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if i == retries - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

def track_time(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        res = func(*args, **kwargs)
        dur = time.time() - start
        print(f"{getattr(Fore, 'GREEN', '')}[Time]{getattr(Style, 'RESET_ALL', '')} {func.__name__} took {dur:.2f}s")
        return res
    return wrapper

def count_tokens(text: str, model: str = "openai/gpt-4o-mini") -> Optional[int]:
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        return None
