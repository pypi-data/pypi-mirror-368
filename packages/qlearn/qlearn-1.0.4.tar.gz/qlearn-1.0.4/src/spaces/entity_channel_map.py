"""
Mapping utility for associating entities with channel indices.

This module provides the `EntityChannelMap` class, which maps entity names
to numeric channel indices for structured data representations, such as
observation spaces in reinforcement learning.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import Dict, List


class EntityChannelMap:
    """
    Maps entity names to corresponding channel indices.

    This class provides methods to retrieve the channel index for an entity,
    list all registered mappings, and check whether an entity is registered.

    Attributes:
        _map (Dict[str, int]): Internal mapping from entity name to channel index.
    """

    def __init__(self, entity_names: List[str]) -> None:
        """
        Initializes the EntityChannelMap with a list of entity names.

        Args:
            entity_names (List[str]): List of entity names to be mapped to
                sequential channel indices starting from 0.
        """
        self._map = {name: idx for idx, name in enumerate(entity_names)}

    def get_channel(self, entity_name: str) -> int:
        """
        Retrieves the channel index for the given entity name.

        Args:
            entity_name (str): The name of the entity.

        Returns:
            int: The channel index associated with the entity.

        Raises:
            KeyError: If the entity name is not registered in the map.
        """
        if entity_name not in self._map:
            raise KeyError(f"Entity '{entity_name}' not registered.")
        return self._map[entity_name]

    def all(self) -> Dict[str, int]:
        """
        Returns a copy of the entity-to-channel mapping.

        Returns:
            Dict[str, int]: A dictionary mapping entity names to channel indices.
        """
        return dict(self._map)

    def __contains__(self, entity_name: str) -> bool:
        """
        Checks whether an entity name is registered in the map.

        Args:
            entity_name (str): The name of the entity to check.

        Returns:
            bool: True if the entity is registered, False otherwise.
        """
        return entity_name in self._map
