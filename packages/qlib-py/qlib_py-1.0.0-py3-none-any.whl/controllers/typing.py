"""
Defines the signature for action functions.

An action function takes two integer arguments (e.g., coordinates)
and returns a tuple of two integers (e.g., new coordinates).

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import Callable, Dict, Tuple

ActionFn = Callable[[int, int], Tuple[int, int]]

IndexType = Dict[int, str]

NameIndexType = Dict[str, int]
