"""
This module provides a class to interact with the Goodgame Empire API's units-related functions.

The `Units` class provides methods for managing units in the game. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Units(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's units-related functions.

    This class provides methods for managing units in the game. It is a subclass of `BaseGgeSocket`.
    """

    def get_units_inventory(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Get the player's units inventory.

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
            self.send_json_command("gui", {})
            if sync:
                response = self.wait_for_json_response("gui")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def delete_units(
        self, wod_id: int, amount: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Delete units from the player's inventory.

        Args:
            wod_id (int): The type of unit to delete.
            amount (int): The number of units to delete.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("dup", {"WID": wod_id, "A": amount, "S": 0})
            if sync:
                response = self.wait_for_json_response("dup")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def wait_receive_units(
        self,
        kingdom: int,
        castle_id: int,
        wod_id: int,
        amount: int,
        timeout: int = 5,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Wait to receive units.

        Args:
            kingdom (int): The kingdom number.
            castle_id (int): The ID of the castle to receive units in.
            wod_id (int): The type of unit to receive.
            amount (int): The number of units to receive.
            timeout (int, optional): The time to wait for a response. Defaults to 5.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if the operation was successful.
            bool: False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            response = self.wait_for_json_response(
                "rue",
                {"AID": castle_id, "SID": kingdom, "WID": wod_id, "RUA": amount},
                timeout=timeout,
            )
            self.raise_for_status(response)
            return response
        except Exception as e:
            if not quiet:
                raise e
            return False
