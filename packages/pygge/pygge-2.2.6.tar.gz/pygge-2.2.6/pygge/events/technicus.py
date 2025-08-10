"""
Module for interacting with the Technicus feature in Goodgame Empire.

This module defines the `Technicus` class, which provides a method to upgrade equipment 
using the Technicus feature, with optional premium enhancements.
"""

from ..base_gge_socket import BaseGgeSocket

class Technicus(BaseGgeSocket):
    """
    A class for interacting with the Technicus feature in Goodgame Empire.

    This class provides a method to upgrade equipment, allowing optional premium enhancements.
    """

    def upgrade_equipment_technicus(self, equipment_id: int, premium: int = 0, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Upgrade equipment using the Technicus.

        Args:
            equipment_id (int): The ID of the equipment to upgrade.
            premium (int, optional): Whether to use a premium upgrade (default is 0).
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("eqe", {
                "C2": premium,
                "EID": equipment_id
            })
            if sync:
                response = self.wait_for_json_response("eqe")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
