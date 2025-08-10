"""
Module for interacting with the Castle Gifts feature in Goodgame Empire.

This module defines the `CastleGifts` class, which provides methods to collect various types 
of gifts, including citizen gifts, citizen quest rewards, and resource gifts.
"""

from ..base_gge_socket import BaseGgeSocket

class CastleGifts(BaseGgeSocket):
    """
    A class for interacting with the Castle Gifts feature in Goodgame Empire.

    This class provides methods to collect citizen gifts, claim rewards from citizen quests, 
    and gather resource gifts.
    """

    def collect_citizen_gift(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect a citizen gift.

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
            self.send_json_command("irc", {})
            if sync:
                response = self.wait_for_json_response("irc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_citizen_quest(self, choice: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect a reward from a citizen quest.

        Args:
            choice (int): The choice of reward (0 or 1).
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("jjc", {
                "CO": choice
            })
            if sync:
                response = self.wait_for_json_response("jjc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_ressource_gift(self, resource_type: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect a resource gift.

        Args:
            resource_type (int): The type of resource to collect.
                - 0: Wood
                - 1: Stone
                - 2: Food
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("rcc", {
                "RT": resource_type
            })
            if sync:
                response = self.wait_for_json_response("rcc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
