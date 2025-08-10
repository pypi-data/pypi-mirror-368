"""
This module contains the class for interacting with the Goodgame Empire API's building inventory-related functions.

The `BuildingsInventory` class provides methods for storing, selling, and retrieving buildings from the inventory. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class BuildingsInventory(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's building inventory-related functions.

    This class provides methods for storing, selling, and retrieving buildings from the inventory. It is a subclass of `BaseGgeSocket`.
    """

    def get_building_inventory(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Get the building inventory.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("sin", {})
            if sync:
                response = self.wait_for_json_response("sin")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def store_building(
        self, building_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Store a building in the inventory.

        Args:
            building_id (int): The ID of the building to store.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("sob", {"OID": building_id})
            if sync:
                response = self.wait_for_json_response("sob")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def sell_building_inventory(
        self,
        wod_id: int,
        amount: int,
        unique_id: int = -1,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Sell a building from the inventory.

        Args:
            wod_id (int): The type of the building to sell.
            amount (int): The amount of the building to sell.
            unique_id (int, optional): The unique ID of the building to sell. Defaults to -1.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command(
                "sds", {"WID": wod_id, "AMT": amount, "UID": unique_id}
            )
            if sync:
                response = self.wait_for_json_response("sds")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
