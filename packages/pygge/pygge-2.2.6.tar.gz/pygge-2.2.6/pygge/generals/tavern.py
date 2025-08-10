"""
Module for interacting with the Tavern feature in Goodgame Empire.

This module defines the `Tavern` class, which provides a method to retrieve the status of current offerings.
"""

from ..base_gge_socket import BaseGgeSocket

class Tavern(BaseGgeSocket):
    """
    A class for interacting with the Tavern feature in Goodgame Empire.

    This class provides a method to retrieve the status of current offerings.
    """

    def get_offerings_status(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve the status of current offerings in the Tavern.

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
            self.send_json_command("gcs", {})
            if sync:
                response = self.wait_for_json_response("gcs")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def make_offering(self, character_id: int, offering_id: int, free_offering: int = 1, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Make an offering at the Tavern.

        Args:
            character_id (int): The ID of the character to make the offering with.
            offering_id (int): The ID of the offering to make.
            free_offering (bool): Whether the offering is free. Defaults to 1.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("sct", {"CID": character_id, "OID": offering_id, "IF": free_offering})
            if sync:
                response = self.wait_for_json_response("sct")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False