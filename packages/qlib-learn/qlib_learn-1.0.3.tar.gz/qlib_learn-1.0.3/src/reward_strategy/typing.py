"""
This module defines type aliases for representing positions of entities and state functions
within the Q-Learning reward strategy context.

Type Aliases:
    EntityPos: A tuple of two integers representing the (x, y) position of an entity.
    StateFn: A list of EntityPos tuples, representing the positions of multiple entities in a state.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import List, Tuple

EntityPos = Tuple[int, int]
StateFn = List[EntityPos]
