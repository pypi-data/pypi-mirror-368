"""
Module for interacting with various events in Goodgame Empire.

This module defines the `Events` class, which provides methods to retrieve event points, 
fetch rankings, and choose event difficulties.
"""

from ..base_gge_socket import BaseGgeSocket

class Events(BaseGgeSocket):
    """
    A class for interacting with various events in Goodgame Empire.

    This class provides methods for retrieving event points, fetching ranking data, 
    and selecting event difficulty levels.
    """

    def get_events(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Get the list of events available to the player.

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
            self.send_json_command("sei", {})
            if sync:
                response = self.wait_for_json_response("sei")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_event_points(self, event_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve the player's points for a specific event.

        Args:
            event_id (int): The ID of the event.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("pep", {
                "EID": event_id
            })
            if sync:
                response = self.wait_for_json_response("pep")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_ranking(self, ranking_type: int, category: int = -1, search_value: int = -1, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve ranking data for a specific event category.

        Args:
            ranking_type (int): The type of ranking to retrieve.
            category (int, optional): The category of ranking. Defaults to -1.
            search_value (int, optional): A search filter for rankings. Defaults to -1.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("hgh", {
                "LT": ranking_type,
                "LID": category,
                "SV": search_value
            })
            if sync:
                response = self.wait_for_json_response("hgh")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def choose_event_difficulty(self, event_id: int, difficulty_id: int, premium_unlock: int = 0, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Select a difficulty level for a specific event.

        Args:
            event_id (int): The ID of the event.
            difficulty_id (int): The ID of the selected difficulty level.
            premium_unlock (int, optional): Whether to unlock the difficulty with premium currency (default is 0).
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("sede", {
                "EID": event_id,
                "EDID": difficulty_id,
                "C2U": premium_unlock
            })
            if sync:
                response = self.wait_for_json_response("sede")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
