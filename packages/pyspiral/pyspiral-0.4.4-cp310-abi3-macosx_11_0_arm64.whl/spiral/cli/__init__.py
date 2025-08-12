import asyncio
import functools
import inspect
from typing import IO

import rich
import typer
from click import ClickException
from grpclib import GRPCError
from httpx import HTTPStatusError


class AsyncTyper(typer.Typer):
    """Wrapper to allow async functions to be used as commands.

    We also pre-bake some configuration.

    Per https://github.com/tiangolo/typer/issues/88#issuecomment-1732469681
    """

    def __init__(self, **kwargs):
        super().__init__(
            no_args_is_help=True,
            pretty_exceptions_enable=False,
            **kwargs,
        )

    def callback(self, *args, **kwargs):
        decorator = super().callback(*args, **kwargs)
        for wrapper in (_wrap_exceptions, _maybe_run_async):
            decorator = functools.partial(wrapper, decorator)
        return decorator

    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)
        for wrapper in (_wrap_exceptions, _maybe_run_async):
            decorator = functools.partial(wrapper, decorator)
        return decorator


class _ClickGRPCException(ClickException):
    def __init__(self, err: GRPCError):
        super().__init__(err.message or "GRPCError message was None.")
        self.err = err
        self.exit_code = 1

    def format_message(self) -> str:
        if self.err.details:
            return f"{self.message}: {self.err.details}"
        return self.message

    def show(self, file: IO[str] | None = None) -> None:
        rich.print(f"Error: {self.format_message()}", file=file)


def _maybe_run_async(decorator, f):
    if inspect.iscoroutinefunction(f):

        @functools.wraps(f)
        def runner(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))

        decorator(runner)
    else:
        decorator(f)
    return f


def _wrap_exceptions(decorator, f):
    @functools.wraps(f)
    def runner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HTTPStatusError as e:
            raise ClickException(str(e))
        except GRPCError as e:
            raise _ClickGRPCException(e)

    return decorator(runner)
