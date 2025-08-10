"""
Module for interacting with the Gifts feature in Goodgame Empire.

This module defines the `Gifts` class, which provides a method to send gifts to other players.
"""

from ..base_gge_socket import BaseGgeSocket

class Gifts(BaseGgeSocket):
    """
    A class for interacting with the Gifts feature in Goodgame Empire.

    This class provides a method to send gifts to other players.
    """

    def send_gift(self, target_id: int, package_type: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Send a gift to another player.

        Args:
            target_id (int): The ID of the recipient player.
            package_type (int): The type of gift package to send.
            amount (int): The quantity of the gift to send.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("gpg", {
                "PID": package_type,
                "RID": target_id,
                "A": amount
            })
            if sync:
                response = self.wait_for_json_response("gpg")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
