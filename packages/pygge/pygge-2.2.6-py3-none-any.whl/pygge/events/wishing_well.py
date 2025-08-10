"""
Module for interacting with the Wishing Well feature in Goodgame Empire.

This module defines the `WishingWell` class, which provides a method to upgrade the Wishing Well.
"""

from ..base_gge_socket import BaseGgeSocket

class WishingWell(BaseGgeSocket):
    """
    A class for interacting with the Wishing Well feature in Goodgame Empire.

    This class provides a method to upgrade the Wishing Well.
    """

    def upgrade_wishing_well(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Upgrade the Wishing Well.

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
            self.send_json_command("rww", {
                "PWR": 0,
                "_PO": -1,
                "WOP": "U"
            })
            if sync:
                response = self.wait_for_json_response("rww")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
