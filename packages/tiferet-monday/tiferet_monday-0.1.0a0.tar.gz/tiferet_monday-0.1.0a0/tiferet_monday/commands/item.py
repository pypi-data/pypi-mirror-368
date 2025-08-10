# *** imports

# ** core
from typing import Dict, Any

# ** infra
from tiferet.commands import Command
from moncli.entities import Item

# ** app
from ..contracts.item import ItemRepository

# *** commands

# ** command: update_simple_column_value
class UpdateSimpleColumnValue(Command):
    """
    Command for updating the value of a simple column for a specified item.
    """

    # ** attribute: item_repo
    item_repo: ItemRepository

    # ** init
    def __init__(self, item_repo: ItemRepository):
        """
        Initializes the UpdateSimpleColumnValue command with the item repository.

        :param item_repo: The repository for managing item operations.
        :type item_repo: ItemRepository
        """
        self.item_repo = item_repo

    # ** method: execute
    def execute(self, item: Item, column_id: str, value: str, **kwargs) -> Dict[str, Any]:
        """
        Executes the command to update the value of a simple column for the specified item.

        :param item: The item for which the column value will be updated.
        :type item: Item
        :param column_id: ID of the column to be updated.
        :type column_id: str
        :param value: New value for the column.
        :type value: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Result of the update operation.
        :rtype: Dict[str, Any]
        """
        
        # Call the repository method to update the column value.
        return self.item_repo.update_simple_column_value(item_id=item.id, board_id=item.board.id, column_id=column_id, value=value)
    
# ** command: create_subitem
class CreateSubitem(Command):
    """
    Command for creating a subitem under a specified item.
    """

    # ** attribute: item_repo
    item_repo: ItemRepository

    # ** init
    def __init__(self, item_repo: ItemRepository):
        """
        Initializes the CreateSubitem command with the item repository.

        :param item_repo: The repository for managing item operations.
        :type item_repo: ItemRepository
        """
        self.item_repo = item_repo

    # ** method: execute
    def execute(self, parent_item_id: str | int, item_name: str, **kwargs) -> Any:
        """
        Executes the command to create a subitem under the specified parent item.

        :param parent_item_id: ID of the parent item under which the subitem will be created.
        :type parent_item_id: str | int
        :param item_name: Name of the subitem to be created.
        :type item_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Result of the subitem creation operation.
        :rtype: Any
        """
        
        # Call the repository method to create the subitem.
        return self.item_repo.create_subitem(
            parent_item_id=parent_item_id,
            item_name=item_name
        )