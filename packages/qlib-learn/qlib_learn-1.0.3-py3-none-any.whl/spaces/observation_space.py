"""
Multi-entity observation space for structured spatial data.

This module defines the `ObservationSpace` class, which manages a multi-channel
observation grid where each channel corresponds to a specific entity type.
It uses an `EntityChannelMap` to associate entity names with channels and an
`ObservationGrid` to store spatial data.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import List, Mapping, Type

import numpy as np

from ..global_typing import GridType, NumericType, PosType
from .entity_channel_map import EntityChannelMap
from .observation_grid import ObservationGrid


class ObservationSpace:
    """
    Represents a multi-channel observation space for entities in a 2D environment.

    Each entity type is assigned a channel, and spatial information is stored
    in a grid using NumPy arrays.

    Attributes:
        _entity_map (EntityChannelMap): Maps entity names to their channel indices.
        _grid (ObservationGrid): Stores the spatial data for each entity channel.
        channel (Callable[[str], int]): Shortcut method for retrieving an entity's channel index.
    """

    def __init__(
        self,
        size: GridType,
        entities: List[str],
        dtype: Type[np.dtype] = np.int32,
    ):
        """
        Initializes the observation space.

        Args:
            size (GridType): Size of the 2D grid as (rows, cols).
            entities (List[str]): List of entity names to track in separate channels.
            dtype (Type[np.dtype], optional): NumPy data type for grid values.
                Defaults to np.int32.
        """
        self._entity_map = EntityChannelMap(entities)
        self._grid = ObservationGrid((*size, len(entities)), dtype)
        self.channel = self._entity_map.get_channel

    def set_entity(self, name: str, position: PosType, value: int = 1) -> None:
        """
        Places or updates an entity's value in the grid.

        Args:
            name (str): Name of the entity.
            position (PosType): (row, col) coordinates in the grid.
            value (int, optional): Value to set. Defaults to 1.
        """
        self._grid.set(position, self.channel(name), value)

    def clear_entity(self, name: str) -> None:
        """
        Clears all values for a given entity from the grid.

        Args:
            name (str): Name of the entity to clear.
        """
        self._grid.clear_channel(self.channel(name))

    def get_entity_position(self, name: str, value: int = 1) -> PosType:
        """
        Retrieves the position of the first occurrence of a given value
        for the specified entity.

        Args:
            name (str): Name of the entity.
            value (int, optional): Value to search for. Defaults to 1.

        Returns:
            PosType: Coordinates (row, col) of the found value.

        Raises:
            ValueError: If the value is not found in the entity's channel.
        """
        return self._grid.find_position(self.channel(name), value)

    def entity_matrix(self, name: str) -> np.ndarray:
        """
        Retrieves the entire 2D matrix for a given entity.

        Args:
            name (str): Name of the entity.

        Returns:
            np.ndarray: A 2D NumPy array representing the entity's positions.
        """
        return self._grid.get_channel_matrix(self.channel(name))

    def as_array(self) -> np.ndarray:
        """
        Returns the complete observation grid.

        Returns:
            np.ndarray: A 3D NumPy array with shape (rows, cols, channels).
        """
        return self._grid.get_full()

    @property
    def shape(self) -> GridType:
        """
        Retrieves the shape of the observation grid.

        Returns:
            GridType: Shape as (rows, cols, channels).
        """
        return self._grid.shape

    @property
    def entities(self) -> Mapping[str, NumericType]:
        """
        Retrieves the entity-to-channel mapping.

        Returns:
            Mapping[str, NumericType]: Dictionary mapping entity names to channel indices.
        """
        return self._entity_map.all()
