# *** imports

# ** infra
from moncli import api_v2 as api

# ** app
from ...contracts.item import *

# *** proxies

# ** proxy: item_moncli_proxy
class ItemMondayProxy(ItemRepository):
    """
    Proxy for managing item-related operations using the Moncli client.
    """

    # * attribute: monday_api_key
    monday_api_key: str

    # * init
    def __init__(self, monday_api_key: str):
        """
        Initializes the ItemMondayProxy with the Monday.com API key.

        :param monday_api_key: API key for accessing the Monday.com API.
        :type monday_api_key: str
        """
        self.monday_api_key = monday_api_key


    # * method: update_simple_column_value
    def update_simple_column_value(self, item_id: str | int, board_id: str | int, column_id: str, value: str):
        """
        Updates the value of a simple column for the specified item using the Moncli client.

        :param item_id: ID of the item to be updated.
        :type item_id: str | int
        :param board_id: ID of the board to which the item belongs.
        :type board_id: str | int
        :param column_id: ID of the column to be updated.
        :type column_id: str
        :param value: New value for the column.
        :type value: str
        """

        # Import and moncli api_v2 handlers.
        return api.change_simple_column_value(
            api_key=self.monday_api_key,
            item_id=item_id,
            board_id=board_id,
            column_id=column_id,
            value=value
        )
    
    # * method: create_subitem
    def create_subitem(self, parent_item_id: str | int, item_name: str) -> Any:
        """
        Creates a subitem under the specified item using the Moncli client.

        :param parent_item_id: ID of the parent item under which the subitem will be created.
        :type parent_item_id: str | int
        :param item_name: Name of the subitem to be created.
        :type item_name: str
        :return: Result of the subitem creation operation.
        :rtype: Any
        """

        # Import and moncli api_v2 handlers.
        return api.requests.execute_query(
            api_key=self.monday_api_key,
            query="""
                mutation ($parent_item_id: ID!, $item_name: String!) {
                    create_subitem(parent_item_id: $parent_item_id, item_name: $item_name) {
                        id
                        name  
                    }
                }
            """,
            variables={
                'parent_item_id': int(parent_item_id),
                'item_name': item_name
            },
            query_name='create_subitem',
        )
