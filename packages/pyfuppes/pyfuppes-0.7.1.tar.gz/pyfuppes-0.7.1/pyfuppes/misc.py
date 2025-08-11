# SPDX-FileCopyrightText: 2025 Florian Obersteiner / KIT
# SPDX-FileContributor: Florian Obersteiner <f.obersteiner@kit.edu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Misc tools."""

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

###############################################################################


class PCOLOR:
    """
    Print in color, using ANSI escape codes.

    This class provides ANSI escape codes for various text colors and styles.
    Usage: print(f"{PCOLOR.red}This text is red{PCOLOR.reset}")

    Caution: not all terminals suppot this.
    """

    # Text colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    magenta = "\x1b[35m"
    cyan = "\x1b[36m"
    white = "\x1b[37m"

    # Bright text colors
    bright_black = "\x1b[90m"
    bright_red = "\x1b[91m"
    bright_green = "\x1b[92m"
    bright_yellow = "\x1b[93m"
    bright_blue = "\x1b[94m"
    bright_magenta = "\x1b[95m"
    bright_cyan = "\x1b[96m"
    bright_white = "\x1b[97m"

    # Background colors
    bg_black = "\x1b[40m"
    bg_red = "\x1b[41m"
    bg_green = "\x1b[42m"
    bg_yellow = "\x1b[43m"
    bg_blue = "\x1b[44m"
    bg_magenta = "\x1b[45m"
    bg_cyan = "\x1b[46m"
    bg_white = "\x1b[47m"

    # Bright background colors
    bg_bright_black = "\x1b[100m"
    bg_bright_red = "\x1b[101m"
    bg_bright_green = "\x1b[102m"
    bg_bright_yellow = "\x1b[103m"
    bg_bright_blue = "\x1b[104m"
    bg_bright_magenta = "\x1b[105m"
    bg_bright_cyan = "\x1b[106m"
    bg_bright_white = "\x1b[107m"

    # Text styles
    bold = "\x1b[1m"
    dim = "\x1b[2m"
    italic = "\x1b[3m"
    underline = "\x1b[4m"
    blink = "\x1b[5m"
    reverse = "\x1b[7m"
    hidden = "\x1b[8m"
    strikethrough = "\x1b[9m"

    # Reset codes
    reset = "\x1b[0m"
    disable = "\x1b[0m"  # Alias for reset...

    @staticmethod
    def rgb(r: int, g: int, b: int):
        """Create a custom RGB color code (foreground)."""
        return f"\x1b[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_rgb(r: int, g: int, b: int):
        """Create a custom RGB color code (background)."""
        return f"\x1b[48;2;{r};{g};{b}m"


###############################################################################


def clean_path(p: Path | str, resolve: bool = True) -> Path:
    """Clean a path from stuff like ~ or $HOME."""
    path_str = Path(p).expanduser().as_posix()  # expanduser() resolves '~' to home path
    if path_str.startswith("$HOME"):
        path_str = path_str.replace("$HOME", Path().home().as_posix(), 1)

    if not resolve:
        return Path(path_str)
    return Path(path_str).resolve()


def to_list_of_Path(folders: str | list[str] | Path | list[Path]) -> list[Path]:
    """Turn input string or list of strings into a list of pathlib.Path objects."""
    if not isinstance(folders, list):
        folders = [folders]  # type: ignore

    return [Path(f) for f in folders]  # type: ignore


def insensitive_pattern(pattern: str) -> str:
    """Return a case-insensitive pattern to use in glob.glob or path.glob."""

    def either(c):
        return f"[{c.lower()}{c.upper()}]" if c.isalpha() else c

    return "".join(map(either, pattern))


###############################################################################


def print_progressbar(
    iteration: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    length: int = 100,
    fill: str = "█",
):
    """
    Print a progress bar.

    https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    access: 2018-12-20
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    progBar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{progBar}| {percent}%% {suffix}", end="\r")
    # Print New Line on Complete
    if iteration == total:
        print("\n")


# #
# # Sample Usage
# #

# from time import sleep

# # A List of Items
# items = list(range(0, 57))
# l = len(items)

# # Initial call to print 0% progress
# printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
# for i, item in enumerate(items):
#     # Do stuff...
#     sleep(0.1)
#     # Update Progress Bar
#     printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)


###############################################################################


def find_youngest_file(path: Path, pattern: str, n: int = 1) -> list[Path] | None:
    """
    Find the file that matches a pattern and has the youngest modification timestamp if there are multiple files that match the pattern.

    input:
        path, string or pathlib.Path, where to look for the file(s)
        pattern, string, pattern to look for in files (see pathlib.Path.glob)
        n, integer, how many to return. defaults to 1.

    Returns
    -------
        filename(s) of youngest file(s), including path
        None if no file
    """
    assert n >= 1, "n must be greater equal 1."

    path = Path(path)
    files = [Path(f) for f in path.glob(pattern) if os.path.isfile(f)]
    sortfiles = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

    if sortfiles:
        return sortfiles[:n]
    return None


###############################################################################


def find_fist_elem(arr: list | np.ndarray, val: Any, condition: Callable) -> Any | None:
    """
    Find the first element in arr that gives (arr[ix] condition val) == True.

    Inputs:
        arr: numeric numpy 1d array or python list
        val: scalar value
        condition: e.g. 'operator.ge' (operator package)

    Returns
    -------
        index of value matching the condition or None if no match is found.
    """
    if isinstance(arr, list):
        return next((ix for ix, v in enumerate(arr) if condition(v, val)), None)

    result = np.argmax(condition(arr, val))

    return result if condition(arr[result], val) else None


###############################################################################


def list_change_elem_index(lst: list, element: Any, new_index: int) -> list:
    """
    Change the index of an element in a list.

    see <https://stackoverflow.com/a/3173159/10197418>
    """
    if new_index >= len(lst) or new_index < 0:
        raise IndexError("new index is out of range")

    _lst = lst.copy()

    if element in lst:
        _lst.insert(new_index, _lst.pop(lst.index(element)))

    return _lst


###############################################################################


def set_compare(a: set, b: set) -> tuple[set, set, set]:
    """
    Compare two iterables a and b. set() is used for comparison, so only unique elements will be considered.

    Parameters
    ----------
    a : set
    b : set

    Returns
    -------
    tuple with 3 elements:
        (what is only in a but not in b,
         what is only in b but not in a,
         what is common in a and b)
    """
    return (a - b, b - a, a.intersection(b))
