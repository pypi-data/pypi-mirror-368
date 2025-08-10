# *** imports

# ** infra
from moncli import client
from moncli.entities import Item

# ** app
from tiferet.commands import *

# *** commands

# command: get_moncli_item
class GetMoncliItem(Command):
    """
    Command to retrieve an item from Monday.com using the Moncli client.
    """

    # * attribute: monday_api_key
    monday_api_key: str

    # * init
    def __init__(self, monday_api_key: str):
        """
        Initializes the GetMoncliItem command with the Monday.com API key.

        :param monday_api_key: API key for accessing the Monday.com API.
        :type monday_api_key: str
        """
        self.monday_api_key = monday_api_key

    # * method: execute
    def execute(self, item_id: str | int, **kwargs) -> Item:
        """
        Retrieves an item by its ID using the Moncli client.

        :param item_id: ID of the item to retrieve.
        :type item_id: str | int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The item data.
        :rtype: Item
        """
        
        # Set the api key to the client.
        client.api_key = self.monday_api_key

        # Retrieve and return the item data.
        try:
            return client.get_items(
                ids=[item_id]
            )[0]
        
        # Handle case where item is not found.
        except IndexError:
            self.raise_error('ITEM_NOT_FOUND', f'Item with ID {item_id} not found.')