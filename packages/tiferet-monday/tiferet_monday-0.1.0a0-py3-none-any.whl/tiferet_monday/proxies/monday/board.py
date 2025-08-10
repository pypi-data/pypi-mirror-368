# *** imports

# ** core
from typing import List, Dict, Any

# ** infra
from moncli import api_v2 as api
from moncli import client as moncli_client
from moncli import ColumnType

# ** app
from ...contracts.board import BoardRepository

# *** proxies

# ** proxy: board_moncli_proxy
class BoardMondayProxy(BoardRepository):
    """
    Proxy for managing board-related operations using the Moncli client.
    """

    # * attribute: monday_api_key
    monday_api_key: str

    def __init__(self, monday_api_key: str):
        """
        Initializes the BoardMondayProxy with the Monday.com API key.

        :param monday_api_key: API key for accessing the Monday.com API.
        :type monday_api_key: str
        """
        self.monday_api_key = monday_api_key

    def add_column(self, board_id: str | int, title: str, column_type: str, description: str = None, labels: List[str] = None):
        """
        Adds a new column to the specified board using the Moncli client.

        :param board_id: ID of the board to which the column will be added.
        :type board_id: str | int
        :param title: Title of the new column.
        :type title: str
        :param column_type: Type of the new column (e.g., 'text', 'date').
        :type column_type: str
        :param description: Optional description for the column.
        :type description: str
        :param labels: Optional list of labels for the column.
        :type labels: List[str]
        """
        
        # Map the labels according to the column type.
        # If column_type is 'status', set defaults as a mapped set of labels.
        defaults = None
        if column_type == 'status' and labels:
            defaults = dict(
                labels={
                    str(index): label for index, label in enumerate(labels)
                }
            )

        # If column_type is 'dropdown', set defaults as a mapped set of labels.
        elif column_type == 'dropdown' and labels:
            defaults = dict(
                settings=dict(
                    labels=[
                        dict(id=index, name=label) for index, label in enumerate(labels)
                    ]
                )
            )

        # Execute the add column method from the client.
        api.create_column(
            api_key=self.monday_api_key,
            board_id=board_id,
            title=title,
            column_type=ColumnType[column_type],
            defaults=defaults,
            description=description
        )

    # * method: list_columns
    def list_columns(self, board_id: str | int) -> List[Dict[str, Any]]:
        """
        Lists all columns in the specified board using the Moncli client.

        :param board_id: ID of the board from which to list columns.
        :type board_id: str | int
        :return: List of columns in the specified board.
        :rtype: List[moncli.Column]
        """
        
        # Create a Moncli client instance with the API key.
        if moncli_client.api_key != self.monday_api_key:
            moncli_client.api_key = self.monday_api_key
        
        # Fetch the board using the Moncli client.
        board = moncli_client.get_board(board_id)
        
        # Return the list of columns in the board.
        return [column.to_primitive() for column in board.columns]
    
    # * method: delete_column
    def delete_column(self, board_id: str | int, column_id: str):
        """
        Deletes a specified column from the board using the Moncli client.

        :param board_id: ID of the board from which the column will be deleted.
        :type board_id: str | int
        :param column_id: ID of the column to be deleted.
        :type column_id: str
        """
        
        api.requests.execute_query(
            api_key=self.monday_api_key,
            query=f"""mutation ($boardId: ID!, $columnId: String!) {{
                delete_column (board_id: $boardId, column_id: $columnId) {{
                    id
                }}
            }}""",
            variables={
                'boardId': int(board_id),
                'columnId': column_id
            },
            query_name='delete_column',
        )

    # * method: create_item
    def create_item(self, board_id: str | int, item_name: str, group_id: str = None) -> Any:
        """
        Creates a new item in the specified board using the Moncli client.

        :param board_id: ID of the board in which the item will be created.
        :type board_id: str | int
        :param item_name: Name of the item to be created.
        :type item_name: str
        :param group_id: Optional ID of the group under which the item will be created.
        :type group_id: str
        :return: Result of the item creation operation.
        :rtype: Any
        """

        # Execute the create item method from the client.
        return api.requests.execute_query(
            api_key=self.monday_api_key,
            query="""
                mutation ($boardId: ID!, $itemName: String!, $groupId: String) {
                    create_item (board_id: $boardId, item_name: $itemName, group_id: $groupId) {
                        id
                        name
                    }
                }
            """,
            variables=dict(
                boardId=int(board_id),
                itemName=item_name,
                groupId=group_id
            ),
            query_name='create_item',
        )
