"""
A module for interacting with the Storm Islands feature in Goodgame Empire.

This module defines the `StormIslands` class, which provides methods for interacting with the Storm Islands.
"""

from ..base_gge_socket import BaseGgeSocket

class StormIslands(BaseGgeSocket):
    """
    A class for interacting with the Storm Islands feature in Goodgame Empire.

    This class provides methods for interacting with the Storm Islands.
    """

    def get_alliance_plunder_ranking(self, alliance_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Get the plunder ranking for the Storm Islands.

        Args:
            alliance_id (int): The ID of the alliance for which to get the plunder ranking.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.
        """
        try:
            self.send_json_command("ama", {"AID": alliance_id})
            if sync:
                response = self.wait_for_json_response("ama")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False