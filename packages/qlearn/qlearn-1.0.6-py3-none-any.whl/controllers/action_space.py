"""
Extended action space supporting named and indexed actions.

This module defines the `ActionSpace` class, which extends the
`ActionSet` discrete action space by allowing actions to be accessed
and invoked by name or index, including support for calling actions
with arguments.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import Any, Dict, Union

import numpy as np

from .action_set import ActionSet
from .typing import ActionFn, IndexType, NameIndexType


class ActionSpace(ActionSet):
    """
    Discrete action space with named actions and callable interface.

    Attributes:
        _key_to_index (IndexType): Maps action names to indices.
        _index_to_key (IndexType): Maps indices to action names.
        _actions (Dict[str, ActionFn]): Maps action names to callable functions.
    """

    def __init__(self, **kwargs: ActionFn):
        """
        Initializes the ActionSpace with named actions.

        Args:
            **kwargs (ActionFn): Named actions as keyword arguments,
                where keys are action names and values are callable functions.

        Raises:
            AssertionError: If no actions are provided.
        """
        assert kwargs, "At least one action must be provided"
        super().__init__(n=len(kwargs))

        self._key_to_index: NameIndexType = {}
        self._index_to_key: IndexType = {}
        self._actions: Dict[str, ActionFn] = {}

        for idx, (key, func) in enumerate(kwargs.items()):
            self._key_to_index[key] = idx
            self._index_to_key[idx] = key
            self._actions[key] = func

    def __getitem__(
        self, key: Union[int, str, tuple, np.integer]
    ) -> Union[ActionFn, Any]:
        """
        Retrieves or invokes an action.

        If `key` is a tuple, treats the first element as the action key
        and the rest as arguments to call the action.

        Args:
            key (Union[int, str, tuple, np.integer]):
                The action key or (key, *args) tuple.

        Returns:
            Union[ActionFn, Any]: The action function or the result of calling it.

        Raises:
            TypeError: If the key type is unsupported.
        """
        if isinstance(key, tuple):
            first, *args = key
            func = self[first]
            return func(*args)

        if isinstance(key, str):
            return self._actions[key]

        if isinstance(key, (int, np.integer)):
            name = self._index_to_key[int(key)]
            return self._actions[name]

        raise TypeError(f"Unsupported key type: {type(key)}")

    def keys(self):
        """
        Returns the list of action names.

        Returns:
            List[str]: List of action keys.
        """
        return list(self._actions.keys())

    def values(self):
        """
        Returns the list of action functions.

        Returns:
            List[ActionFn]: List of action callables.
        """
        return list(self._actions.values())

    def items(self):
        """
        Returns the list of (action name, function) pairs.

        Returns:
            List[Tuple[str, ActionFn]]: List of key-function tuples.
        """
        return list(self._actions.items())

    def __repr__(self):
        """
        Returns the string representation of the ActionSpace.

        Returns:
            str: String with class name and list of action keys.
        """
        return f"{self.__class__.__name__}(actions={list(self._actions.keys())})"
