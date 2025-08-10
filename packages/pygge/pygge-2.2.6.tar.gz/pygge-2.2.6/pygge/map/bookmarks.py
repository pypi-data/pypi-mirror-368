"""
Module for managing bookmarks in Goodgame Empire.

This module defines the `Bookmarks` class, which provides methods to retrieve the 
player's saved bookmarks.
"""

from ..base_gge_socket import BaseGgeSocket

class Bookmarks(BaseGgeSocket):
    """
    A class for managing bookmarks in Goodgame Empire.

    This class provides methods to retrieve a player's saved bookmarks.
    """

    def get_bookmarks(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve the player's saved bookmarks.

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
            self.send_json_command("gbl", {})
            if sync:
                response = self.wait_for_json_response("gbl")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
