"""
Defines a discrete set of actions for reinforcement learning agents.

This module provides the `ActionSet` class, which represents a discrete
action space with a fixed number of actions. It supports sampling random
actions and checking action membership.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

import random


class ActionSet:
    """
    Represents a discrete set of actions.

    Attributes:
        _n (int): Number of discrete actions.
    """

    def __init__(self, n: int):
        """
        Initializes the ActionSet.

        Args:
            n (int): Number of discrete actions. Must be greater than zero.
            dtype (Type[np.number], optional): Data type for actions (not used internally).
                Defaults to np.float32.

        Raises:
            AssertionError: If `n` is not greater than zero.
        """
        assert n > 0, "n must be greater than 0"
        self._n = n

    def __repr__(self) -> str:
        """
        Returns the string representation of the ActionSet.

        Returns:
            str: String in the format "ActionSet(n=number_of_actions)".
        """
        return f"{self.__class__.__name__}(n={self._n})"

    def contains(self, x: int) -> bool:
        """
        Checks if a given action index is valid in this action set.

        Args:
            x (int): The action index to check.

        Returns:
            bool: True if `x` is an integer within [0, n-1], False otherwise.
        """
        return isinstance(x, int) and 0 <= x < self._n

    def sample(self) -> int:
        """
        Randomly samples an action index from the action set.

        Returns:
            int: A random integer in the range [0, n-1].
        """
        return random.randint(0, self._n - 1)

    @property
    def shape(self) -> tuple[int]:
        """
        Returns the shape of the action set.

        Returns:
            tuple[int]: A tuple representing the shape (number of actions,).
        """
        return (self._n,)

    @property
    def n(self) -> int:
        """
        Returns the number of discrete actions in the set.

        Returns:
            int: The number of actions.
        """
        return self._n
