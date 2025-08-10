"""
Module for interacting with the Ruins feature in Goodgame Empire.

This module defines the `Ruins` class, which provides methods to retrieve ruin information 
and request ruin messages.
"""

from ..base_gge_socket import BaseGgeSocket

class Ruins(BaseGgeSocket):
    """
    A class for interacting with the Ruins feature in Goodgame Empire.

    This class provides methods to retrieve information about ruins and 
    request ruin messages.
    """

    def get_ruin_infos(self, x: int, y: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve information about a specific ruin.

        Args:
            x (int): The x-coordinate of the ruin.
            y (int): The y-coordinate of the ruin.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("rui", {
                "PX": x,
                "PY": y
            })
            if sync:
                response = self.wait_for_json_response("rui")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def ask_ruin_infos_message(self, x: int, y: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Request additional information about a ruin.

        Args:
            x (int): The x-coordinate of the ruin.
            y (int): The y-coordinate of the ruin.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("rmb", {
                "PX": x,
                "PY": y
            })
            if sync:
                response = self.wait_for_json_response("rmb")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
