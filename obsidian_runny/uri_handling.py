"""Pared down URI opener functions to talk to Obsidian.

* Windows and Mac get OS-specific defaults
* All other platforms (Linux, BSD, etc) assume `xdg-open`

See the links below to learn more, or file an issue if
you would like support for another approach.

Overview of XDG-open:

1. https://linux.die.net/man/1/xdg-open
2. https://wiki.archlinux.org/title/Xdg-utils#xdg-open
3. https://portland.freedesktop.org/doc/xdg-open.html
"""
import platform
import subprocess

from dataclasses import dataclass
from urllib.parse import quote as urlquote
from obsidian_runny.annotations import (
    V,
    PairFormatter,
    ParamsFormatter
)

from typing_extensions import (
    Any,
    Final,
    Callable,
    Generic,
    Mapping,
    Protocol,
    TypeVar
)


POSIX_REDIRECT_OUTPUT_TO_NULL: Final[str] = "> /dev/null 2>&1"
"""Helper constant for building commands."""

__all__ = [
    "fmt_uri_parameters",
    "fmt_uri",
    "platform_uri_opener",
    "PlatformURIOpener",
    "PosixLikeURIOpener",
    "POSIX_REDIRECT_OUTPUT_TO_NULL",
    "WindowsURIOpener",
    "MacURIOpener",
    "XDGMimeURIOpener"
]

_keys_are_bool = set((
    "clipboard",
    "silent",
    "overwrite"
))
_bool2str = {True: "true", False: "false"}


def fmt_uri_param_pair(k: str, v: Any) -> str:
    parts = [urlquote(k)]

    if k in _keys_are_bool:
        if v not in _bool2str:
            raise TypeError(f"Expected bool value for {k}, not {v!r}")
        parts.append(_bool2str[v]) # type: ignore
    else:
        parts.append(urlquote(str(v)))

    return "=".join(parts)


def fmt_uri_parameters(parameters: Mapping[str, Any]) -> str:
    """Format the parameter block into a joined string.

    Args:
        parameters: A mapping to format.
    """
    params_quoted = []

    for raw_key, raw_value in parameters.items():
        if not isinstance(raw_key, str):
            raise TypeError(f"{raw_key!r} is not a str")
        encoded = fmt_uri_param_pair(raw_key, raw_value)
        params_quoted.append(encoded)

    return "&".join(params_quoted)


def fmt_uri(
    protocol: str,
    resource: str,
    parameters: Mapping[str, V],
    param_formatter: ParamsFormatter[[Mapping[str, V]], str] = fmt_uri_parameters
) -> str:
    """Good-enough stub since urllib seems crufy and complicated."""

    if not isinstance(protocol, str):
        raise TypeError("expected string for protocol")
    if not isinstance(resource, str):
        raise TypeError("expected string for resource")

    parts = [protocol, "://", urlquote(resource)]
    if parameters:
        parts.extend((
            "?",
            fmt_uri_parameters(parameters)
        ))

    return "".join(parts)


class PlatformURIOpener(Protocol):

    def _pre_uri(self, parts: list[str]) -> None:
        return

    def _post_uri(self, parts: list[str]) -> None:
        return

    def _run_cmd(self, parts: list[str], **kwargs) -> None:
        subprocess.run(" ".join(parts), **kwargs)

    def __call__(self, uri: str) -> None:
        parts = []
        self._pre_uri(parts)
        parts.append(f"\"{uri}\"")
        self._post_uri(parts)
        self._run_cmd(parts)



class PosixLikeURIOpener(PlatformURIOpener):

    def _run_cmd(self, parts: list[str], shell: bool = True, **kwargs):
        super()._run_cmd(parts, shell=shell, **kwargs)


@dataclass(frozen=True)
class XDGMimeURIOpener(PosixLikeURIOpener):
    """Wraps `xdg-open`, a common URI / mimetype routing tool."""

    log: bool = False
    hup: bool = False

    def _pre_uri(self, parts: list[str]) -> None:
        if not self.hup:
            parts.append("nohup")
        parts.append("xdg-open")

    def _post_uri(self, parts: list[str]) -> None:
        if not self.log:
            parts.append(POSIX_REDIRECT_OUTPUT_TO_NULL)


class WindowsURIOpener(PlatformURIOpener):
    """Powershell-based opener"""

    def _pre_uri(self, parts: list[str]) -> None:
        parts.append("Start")


class MacURIOpener(PlatformURIOpener):
    """Mac opener"""

    def _pre_uri(self, parts: list[str]) -> None:
        parts.append("open -gja")


platform_uri_opener: PlatformURIOpener

match (_plat_name := platform.system()):
    case "Windows":
        platform_uri_opener = WindowsURIOpener()
    case "Mac":
        platform_uri_opener = MacURIOpener()

    # Linux and BSD-likes (hope for XDG, then fail if not found)
    case _:
        try:
            subprocess.run(
                f"xdg-open --help {POSIX_REDIRECT_OUTPUT_TO_NULL}",
                check=True,
                shell=True
            )
            platform_uri_opener = XDGMimeURIOpener()
        except subprocess.CalledProcessError as e:
            raise NotImplementedError(
                f"{_plat_name} (assumed POSIX-like) has no xdg-open.\n"
                f"Please file an issue https://github.com/pushfoo/obsidian-runny/issues/new"
            )

