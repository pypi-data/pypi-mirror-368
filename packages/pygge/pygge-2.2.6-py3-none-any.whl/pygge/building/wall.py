"""
This module contains the class for interacting with the Goodgame Empire API's wall-related functions.

The `Wall` class provides methods for upgrading walls. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Wall(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's wall-related functions.

    This class provides methods for upgrading walls. It is a subclass of `BaseGgeSocket`.
    """

    def upgrade_wall(
        self, building_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Upgrade the wall.

        Args:
            building_id (int): The ID of the wall to upgrade.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("eud", {"OID": building_id, "PWR": 0, "PO": -1})
            if sync:
                response = self.wait_for_json_response("eud")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
