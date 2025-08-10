# *** imports

# ** core
from typing import List, Any

# ** infra
from tiferet.contracts import Repository, abstractmethod

# *** contracts

# ** contract: board_repo
class BoardRepository(Repository):
    """
    Repository for managing board-related operations.
    """

    # * method: add_column
    @abstractmethod
    def add_column(self, board_id: str | int, column_name: str, column_type: str, description: str = None, labels: List[str] = None):
        """
        Adds a new column to the specified board.

        :param board_id: ID of the board to which the column will be added.
        :type board_id: str | int
        :param column_name: Name of the new column.
        :type column_name: str
        :param column_type: Type of the new column (e.g., 'text', 'date').
        :type column_type: str
        :param description: Optional description for the column.
        :type description: str
        :param labels: Optional list of labels for the column.
        :type labels: List[str]
        """
        raise NotImplementedError('The add_column method must be implemented by the board repository.')
    
    # * method: list_columns
    @abstractmethod
    def list_columns(self, board_id: str | int) -> List[dict]:
        """
        Lists all columns in the specified board.

        :param board_id: ID of the board from which to list columns.
        :type board_id: str | int
        :return: List of columns in the board.
        :rtype: List[dict]
        """
        raise NotImplementedError('The list_columns method must be implemented by the board repository.')
    
    # * method: delete_column
    @abstractmethod
    def delete_column(self, board_id: str | int, column_id: str):
        """
        Deletes a column from the specified board.

        :param board_id: ID of the board from which the column will be deleted.
        :type board_id: str | int
        :param column_id: ID of the column to be deleted.
        :type column_id: str
        """
        raise NotImplementedError('The delete_column method must be implemented by the board repository.')
    
    # * method: create_item
    @abstractmethod
    def create_item(self, board_id: str | int, item_name: str, group_id: str = None) -> Any:
        """
        Creates a new item in the specified board.

        :param board_id: ID of the board in which the item will be created.
        :type board_id: str | int
        :param item_name: Name of the item to be created.
        :type item_name: str
        :param group_id: Optional ID of the group under which the item will be created.
        :type group_id: str
        :return: Result of the item creation operation.
        :rtype: Any
        """
        raise NotImplementedError('The create_item method must be implemented by the board repository.')
