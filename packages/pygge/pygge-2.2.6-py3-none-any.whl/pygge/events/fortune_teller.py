"""
A module for interacting with the Fortune Teller feature in Goodgame Empire.

This module defines the `FortuneTeller` class, which provides methods for interacting with the Fortune Teller.
"""

from ..base_gge_socket import BaseGgeSocket

class FortuneTeller(BaseGgeSocket):
    """
    A class for interacting with the Fortune Teller feature in Goodgame Empire.

    This class provides methods for interacting with the Fortune Teller.
    """

    def make_divination(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Make a divination at the Fortune Teller.
        Args:
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("ftl", {})
            if sync:
                response = self.wait_for_json_response("ftl")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False