import logging
import platform
import subprocess

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from urllib.parse import quote as urlquote


from obsidian_runny.annotations import V
from obsidian_runny.containers import ParamDict
from obsidian_runny.uri_handling import fmt_uri, platform_uri_opener


log: logging.Logger | logging.LoggerAdapter

from typing_extensions import (
    Annotated,
    Optional,
    Protocol,
    Mapping,
)

import typer



app = typer.Typer()


def set_log_level(level: str):
    level_int = getattr(logging, level.upper(), None)
    if isinstance(level_int, int):
        logging.basicConfig(level=level_int)
    else:
        raise ValueError(f"Cannot parse logging value {level!r}")

    # A little dirty trick (it's a utility script)
    global log
    log = logging.getLogger(__file__)


def get_obsidian_uri(
    action: str,
    parameters: Mapping[str, V]
) -> str:
    if isinstance(parameters, ParamDict):
       use_params = parameters
    else:
       use_params = ParamDict(parameters)

    return fmt_uri(
        protocol="obsidian",
        resource=action,
        parameters=parameters
    )


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


def run_obsidian_uri_command(
    action: str | _URIAction,
    parameters: Mapping[str, V]
) -> None:
    """Assemble and run a URI for an Obsidian command.

    See the Obsidian documentation for more info:
    https://help.obsidian.md/Extending+Obsidian/Obsidian+URI

    Example URI
    ```
    obsidian://new?vault=Obsidian%20Vault&file=New%20Note%20In%Root
    ```
    """
    validated_action = _URIAction(action)
    uri = get_obsidian_uri(validated_action, parameters)
    log.info(f"action  : {validated_action}")
    log.info(f"full uri: {uri}")

    platform_uri_opener(uri)


NoteNameOption = Annotated[
    Optional[str], typer.Option(
        "--name",
        help="The name of the note to create",
    )]

NotePathOption = Annotated[
    Optional[str], typer.Option(
        "--path",
        help="The vault-relative path of the note (overrides --name)",
        )]

NoteFileOption = Annotated[
    Optional[Path], typer.Option(
        "--file",
        help="The absolute OS path of the note (overrides --path)",
        )]

LogLevelOption = Annotated[
    str, typer.Option("--log-level", help="The logging level to use")]
VaultOption = Annotated[Optional[
    str], typer.Option("--vault", help="The name or vault ID")]
QueryOption = Annotated[
    Optional[str], typer.Option("--query", help="A search query to run.")]

SilentFlag = Annotated[
    bool, typer.Option("--silent", help="Do not show the note.")]
ClipboardFlag = Annotated[
    bool, typer.Option("--clipboard", help="Use clipboard contents.")]
OverwriteFlag = Annotated[
    bool, typer.Option("--overwrite", help="Overwrite current contents.")]
AppendFlag = Annotated[
    bool, typer.Option("--append", help="Append to any existing file.")]


# Named to avoid clobbering the built-in open() function.
@app.command("open")
def note_open(
    name: NoteNameOption = None,
    vault: VaultOption = None,
    path: NotePathOption = None,
    file: NoteFileOption = None,
    log_level: LogLevelOption = "WARNING",
    prepend: Annotated[Optional[str], typer.Option("--prepend", help="Value to prepend")] = None,
    append: Annotated[Optional[str], typer.Option("--append", help="Value to append")] = None
) -> None:
    """Attempt to open the note with a given name."""

    set_log_level(log_level)
    parameters = ParamDict(
        name=name,
        vault=vault,
        path=path,
        file=file,
        prepend=prepend,
        append=append
    )

    run_obsidian_uri_command(
        _URIAction.NEW,
        parameters
    )


@app.command("new")
def note_new(
    name: NoteNameOption,
    vault: VaultOption = None,
    path: NotePathOption = None,
    file: NoteFileOption = None,
    log_level: LogLevelOption = "WARNING"
) -> None:
    """Create a new note with the given name."""
    set_log_level(log_level)
    parameters = ParamDict(
        name=name, vault=vault, path=path, file=file)

    run_obsidian_uri_command(
        _URIAction.NEW,
        parameters
    )


@app.command("search")
def note_search(
    query: QueryOption = None,
    vault: VaultOption = None,
    log_level: LogLevelOption = "WARNING"
):
    set_log_level(log_level)
    run_obsidian_uri_command(
        _URIAction.SEARCH,
        dict(
        vault=vault,
        query=query
        )
    )



if __name__ == "__main__":
    app()

