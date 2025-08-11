from typing import Callable

import grpc
from frogml.core.exceptions import FrogmlException


def grpc_try_catch_wrapper(exception_message: str):
    def decorator(function: Callable):
        def _inner_wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                if isinstance(e, grpc.RpcError):
                    # noinspection PyUnresolvedReferences
                    raise FrogmlException(
                        exception_message + f". Error is: {e}."
                    ) from e

                raise e

        return _inner_wrapper

    return decorator
