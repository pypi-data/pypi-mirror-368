"""
Module for interacting with the Tutorial feature in Goodgame Empire.

This module defines the `Tutorial` class, which provides methods for selecting a hero, 
collecting the beginner's gift, and skipping the generals' introduction.
"""

from ..base_gge_socket import BaseGgeSocket

class Tutorial(BaseGgeSocket):
    """
    A class for interacting with the Tutorial feature in Goodgame Empire.

    This class provides methods for choosing a hero, collecting a noob gift, 
    and skipping the generals' introduction.
    """

    def choose_hero(self, hero_id: int = 802, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Select a hero for the tutorial.

        Args:
            hero_id (int, optional): The ID of the hero to select. Defaults to 802.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("hdc", {
                "HID": hero_id
            })
            if sync:
                response = self.wait_for_json_response("hdc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_noob_gift(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect the beginner's gift.

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
            self.send_json_command("uoa", {})
            if sync:
                response = self.wait_for_json_response("uoa")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def skip_generals_intro(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Skip the introduction to generals.

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
            self.send_json_command("sgi", {})
            if sync:
                response = self.wait_for_json_response("sgi")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
