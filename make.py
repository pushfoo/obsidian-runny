#!/usr/bin/env python
"""
Low-dependency build script.
"""
# Does not use typer to allow:
#
# - Faster CI (test and doc build need fewer deps)
# - Simpler code (no adapter shims)
# - More reliable code (less API to break)
from __future__ import annotations

import subprocess
import sys


def stderr(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


commands = {}


def command(f) -> None:
    """We have typer at home."""
    commands[f.__name__.replace("_", "-")] = f
    return f


@command
def test(**_) -> None:
    """Run pytest."""
    subprocess.run(['pytest', 'tests'])


@command
def typecheck(**_) -> None:
    """Type-check with pyright."""
    subprocess.run(['pyright', 'obsidian_runny'])


@command
def help(print_func=print, **_) -> None:
    """Print usage information."""

    command_width = max(len(k) for k in commands)
    print_func(__doc__.strip(), end="\n\n")
    for name, func in commands.items():
        print_func(f"{sys.argv[0]} {name:<{command_width}}", end="      ")
        doc = getattr(func, '__doc__', '[ no docstring ]')
        print_func(doc.split("\n")[0])


def main():

    problem = 0
    kwargs = dict(print_func=print)

    if len(sys.argv) < 2:
        command_name = 'help'
    elif (command_name := sys.argv[1]) not in commands:
        problem = 1
        stderr(f"ERROR: unknown command {command_name!r}")
        command_name = 'help'
        kwargs.update(print_func=stderr)

    run_command = commands.get(command_name)
    run_command(**kwargs)
    exit(problem)


if __name__ == '__main__':
    main()

