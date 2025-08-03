# obsidian-runny

CLI helpers for [Obsidian][] using Python 3.12+.

## Examples

> [!TIP]
> Add a shorthand [shell alias][] to use a different command

[shell alias]: https://unix.stackexchange.com/questions/146419/creating-an-alias-for-a-bash-script

Create a note from current clipboard contents:

```shell
obsidian_runny new --name "My new note" --clipboard
```

## Installing

> [!IMPORTANT]
> Pre-alpha software means you should expect bugs.

### Requirements

1. Python 3.12+
2. [Obsidian][]
3. A high tolerance for unfinished software

> [!NOTE]
> [`pipx`][pipx] is also useful for use as a system-wide utility.

### Installing

| Approach    | Command                                                                     |
|-------------|-----------------------------------------------------------------------------|
| Local venv  | `pip install git+https://git+https://github.com/pushfoo/obsidian-runny.git` |
| System-wide | `pipx install git+https://github.com/pushfoo/obsidian-runny.git`            |

> [!CAUTION]
> **Never** attempt to use `sudo` with `pip`! ([Learn why](#why-never-sudo-pip-install))


[Obsidian]: https://obsidian.md/
[pipx]: https://pipx.pypa.io/


## Errata

### Why never `sudo pip install`?

**TL;DR:** It's the fastest way to break your system.

Especially on `apt`-based Linux distros, it is a bad time. Just
don't do it.

1. The override flag is `--break-system-packages` for a reason
2. The `apt` package manager relies on the "system" Python install
3. If you break system Python, you also break:
   * `apt` (can't install software)
   * network utilities (not always, but it hurts)

Reinstalling is often faster than manually fixing the issues,
but it is also no fun.

#### Ok, what should I use then?

Instead, use one of the following:
* [`pipx`][pipx]
* [`uv`][uv]
* An ordinary virtual environment (venv)
* Any other reputable tool

[uv]: https://docs.astral.sh/uv/
