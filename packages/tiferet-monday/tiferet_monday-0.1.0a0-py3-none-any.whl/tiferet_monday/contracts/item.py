# *** imports

# ** core
from typing import Any

# ** infra
from tiferet.contracts import Repository, abstractmethod

# *** contracts

# ** contract: item_repo
class ItemRepository(Repository):
    """
    Repository for managing item-related operations.
    """

    # * method: update_simple_column_value
    @abstractmethod
    def update_simple_column_value(self, item_id: str | int, board_id: str | int, column_id: str, value: str):
        """
        Updates the value of a simple column for the specified item.

        :param item_id: ID of the item to be updated.
        :type item_id: str | int
        :param board_id: ID of the board to which the item belongs.
        :type board_id: str | int
        :param column_id: ID of the column to be updated.
        :type column_id: str
        :param value: New value for the column.
        :type value: str
        """

        raise NotImplementedError('The update_simple_column_value method must be implemented by the item repository.')
    
    # * method: create_subitem
    @abstractmethod
    def create_subitem(self, parent_item_id: str | int, item_name: str) -> Any:
        """
        Creates a subitem under the specified item.

        :param parent_item_id: ID of the parent item under which the subitem will be created.
        :type parent_item_id: str | int
        :param item_name: Name of the subitem to be created.
        :type item_name: str
        :return: Result of the subitem creation operation.
        :rtype: Any
        """

        raise NotImplementedError('The create_subitem method must be implemented by the item repository.')