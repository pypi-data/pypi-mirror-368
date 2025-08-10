from __future__ import annotations

import logging
import os
from textwrap import dedent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import ParamSpec
    from typing_extensions import TypeVar

    P = ParamSpec("P")
    R = TypeVar("R")


logging.basicConfig(
    level=logging.ERROR,
    format="[%(asctime)s] [%(levelname)-7s] [%(name)s] %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("depsdev")


def to_sync() -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to convert async methods to sync methods.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        import functools

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                import asyncio

                from rich import print_json

                print_json(data=asyncio.run(func(*args, **kwargs)))  # type: ignore[arg-type]
            except Exception:
                logger.exception("An error occurred while executing the command.")
                raise SystemExit(1) from None

            raise SystemExit(0)

        return wrapper

    return decorator


def main() -> None:
    """
    Main entry point for the CLI.
    """

    try:
        import typer
    except ImportError:
        msg = (
            "The 'cli' optional dependency is not installed. "
            "Please install it with 'pip install depsdev[cli]'."
        )
        logger.error(msg)  # noqa: TRY400
        raise SystemExit(1) from None

    alpha = os.environ.get("DEPSDEV_V3_ALPHA", "false").lower() in ("true", "1", "yes")

    app = typer.Typer(
        name="depsdev",
        no_args_is_help=True,
        rich_markup_mode="rich",
        help=dedent(
            """\
            A CLI tool to interact with the https://docs.deps.dev/api/

            ## Package names

            In general, the API refers to packages by the names used within their ecosystem, including details such as capitalization.

            Exceptions:

            - Maven names are of the form <group ID>:<artifact ID>, for example org.apache.logging.log4j:log4j-core.
            - PyPI names are normalized as per PEP 503.
            - NuGet names are normalized through lowercasing according to the Package Content API request parameter specification. Versions are normalized according to NuGet 3.4+ rules.

            ## Purl parameters

            Some methods accept purls, or package URLs, which have their own rules about how components should be encoded. https://github.com/package-url/purl-spec

            For example, the npm package @colors/colors has the purl pkg:npm/@colors/colors.

            To enable the alpha features, set the environment variable DEPSDEV_V3_ALPHA to true.
            """,  # noqa: E501
        ),
    )

    from depsdev.v3 import DepsDevClientV3
    from depsdev.v3alpha import DepsDevClientV3Alpha

    client_v3_alpha = DepsDevClientV3Alpha()
    client_v3 = DepsDevClientV3()

    client = client_v3 if not alpha else client_v3_alpha

    app.command(rich_help_panel="v3")(to_sync()(client.get_package))
    app.command(rich_help_panel="v3")(to_sync()(client.get_version))
    app.command(rich_help_panel="v3")(to_sync()(client.get_requirements))
    app.command(rich_help_panel="v3")(to_sync()(client.get_dependencies))
    app.command(rich_help_panel="v3")(to_sync()(client.get_project))
    app.command(rich_help_panel="v3")(to_sync()(client.get_project_package_versions))
    app.command(rich_help_panel="v3")(to_sync()(client.get_advisory))
    app.command(rich_help_panel="v3")(to_sync()(client.query))

    if alpha:
        # app.command(rich_help_panel="v3alpha")(to_sync()(client_v3_alpha.get_version_batch))
        app.command(rich_help_panel="v3alpha")(to_sync()(client_v3_alpha.get_dependents))
        app.command(rich_help_panel="v3alpha")(to_sync()(client_v3_alpha.get_capabilities))
        app.command(rich_help_panel="v3alpha")(to_sync()(client_v3_alpha.get_project_batch))
        app.command(rich_help_panel="v3alpha")(
            to_sync()(client_v3_alpha.get_similarly_named_packages)
        )
        app.command(rich_help_panel="v3alpha")(to_sync()(client_v3_alpha.purl_lookup))
        app.command(rich_help_panel="v3alpha")(to_sync()(client_v3_alpha.purl_lookup_batch))
        app.command(rich_help_panel="v3alpha")(to_sync()(client_v3_alpha.query_container_images))

    return app()


if __name__ == "__main__":
    main()
