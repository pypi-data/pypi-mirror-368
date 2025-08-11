"""
This module defines type aliases for identifiers used within the QLearning agent.

Type Aliases:
    IdentifierPr: A type that can be an integer, a string, or a tuple of two integers.
        Used to represent flexible identifier formats throughout the agent codebase.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import List, Tuple, Union

TrainStateType = Tuple[int, int]

QValueType = List[Union[float, int]]
