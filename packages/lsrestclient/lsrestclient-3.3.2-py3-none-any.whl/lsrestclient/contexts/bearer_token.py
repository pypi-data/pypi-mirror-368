import contextlib
import contextvars
from typing import Optional

bearer_token_value: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("bearer_token_value", default=None)


@contextlib.contextmanager
def bearer_token_provider(bearer_token: str):
    """
    :param bearer_token: The bearer token to set.
    :return: A context manager that sets the bearer token and resets it when the context is exited.
    """
    token = bearer_token_value.set(bearer_token)
    yield
    bearer_token_value.reset(token)


@contextlib.contextmanager
def bearer_token_context():
    """
    Context manager for handling bearer token.

    :return: The value of the bearer token.
    """
    bearer_token = bearer_token_value.get()
    yield bearer_token
