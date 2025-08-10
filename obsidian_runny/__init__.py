from collections import UserString
import inspect
import logging


from dataclasses import dataclass, fields, Field
from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path
from typing import Final, get_type_hints

# typer does not support | syntax, so we use Optional
import typer
from typing_extensions import Annotated, Any, Optional


from obsidian_runny.annotations import KEY_TUPLE, V, DictArgsLike
from obsidian_runny.config import LogLevel
from obsidian_runny.mappings.iteration.keygrabs import get_keys
from obsidian_runny.mappings.param_dict import ParamDict
from obsidian_runny.uri_handling import run_obsidian_uri_command


app = typer.Typer()
log: logging.Logger | logging.LoggerAdapter


class _URIAction(StrEnum):
    """Covers built-in Obsidian URI actions.

    It is `_underscore_protected` since plugins *may*
    add new new actions:

    * The first-party Daily plugin is an example
    * Third-party plugins may also add new ones

    """

    OPEN = "open"
    """Open an existing note."""

    NEW = "new"
    """New command."""

    SEARCH = "search"
    """Search notes."""

    DAILY = "daily"
    """Requires the Daily plugin to be enabled."""


# Will always have a value (we'll default it to "WARNING") below
LogLevelOption = Annotated[str,
    typer.Option("--log-level", help="The logging level to use", parser=LogLevel)]


def option(annotation, flag: str, help: str | None = None, **kwargs):
    """Wraps the base `annotation` in `Optional` + a typer.Option.

    Arguments:
        annotation: a type or type alias.
        flag: a `--flag` to use.
        help: A help string.
        kwargs: Additional values to pass to `typer.Option`
    Returns:
        An typer-annotated type alias.
    """
    return Annotated[
        Optional[annotation],
        typer.Option(flag, help=help, **kwargs)
    ]


NoteNameOption = option(
    str, "--name", help="The name of the note to create")
NotePathOption = option(
    str, "--path", help="The vault-relative path of the note (overrides --name)")
NoteFileOption = option(
    Path, "--file", help="The absolute OS path of the note (overrides --path)")

VaultOption = option(
    str, "--vault", help="The name or vault ID")
QueryOption = option(
    str, "--query", help="A search query to run.")
PrependOption = option(
    str, "--prepend", help="Value to prepend")
AppendOption = option(
    str, "--append", help="Value to append")


# Q: Why not dataclass inheritance and an adapter (hint->typer/click)?
# A: That's complex type hint stuff and a last resort
def run_command_from_locals(
    action: str,
    *,
    required: Iterable[str] = (),
    optional: Iterable[str] = (),
    defaults: DictArgsLike[str, V] = (),
) -> None:
    """Run an Obsidian URI command from calling scope values.

    * An awful kludge
    * Simpler than building helpers to read dataclass typehints

    If typer supported dataclasses natively, this would be a non-issue.
    """
    outer_frame: inspect.FrameInfo =\
        inspect.currentframe().f_back  # type: ignore
    f_locals: dict[str, Any] = outer_frame.f_locals  # type: ignore
    parameters = ParamDict(
        get_keys(
            source=f_locals,
            required=required,
            optional=optional,
            defaults=defaults
        )
    )
    run_obsidian_uri_command(
        action,
        parameters=parameters)


VAULT_ONLY: Final[KEY_TUPLE] = ('vault',)
BASE_OPTIONS: Final[KEY_TUPLE] = (
    *VAULT_ONLY,
    'name',)
SHARED_OPTIONS: Final[KEY_TUPLE] = (
    *BASE_OPTIONS,
    'path',
    'file')
PREPEND_APPEND: Final[KEY_TUPLE] = (
    *SHARED_OPTIONS,
    'prepend',
    'append')


# Named to avoid clobbering the built-in open() function.
@app.command("open")
def note_open(
    # These are used and your IDE / pyright are wrong (see get_locals)
    name: NoteNameOption = None,
    vault: VaultOption = None,
    path: NotePathOption = None,
    file: NoteFileOption = None,
    prepend: PrependOption = None,
    append: AppendOption = None,
    _: LogLevelOption = "WARNING"
) -> None:
    """Attempt to open the note with a given name."""
    run_command_from_locals(
        _URIAction.OPEN,
        required=PREPEND_APPEND
    )


@app.command("new")
def note_new(
    name: NoteNameOption,
    vault: VaultOption = None,
    path: NotePathOption = None,
    file: NoteFileOption = None,
    _: LogLevelOption = "WARNING"
) -> None:
    """Attempt to create a new note with the given name.

    May add a number at the end of the name already exists.
    """
    run_command_from_locals(
        _URIAction.NEW,
        required=SHARED_OPTIONS
    )


@app.command("search")
def note_search(
    query: QueryOption = None,
    vault: VaultOption = None,
    _: LogLevelOption = "WARNING"
) -> None:
    run_command_from_locals(
        _URIAction.SEARCH,
        required=(*VAULT_ONLY, 'query')
    )


if __name__ == "__main__":
    app()
