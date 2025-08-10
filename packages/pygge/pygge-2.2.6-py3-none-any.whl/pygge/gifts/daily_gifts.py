"""
Module for interacting with the Daily Gifts feature in Goodgame Empire.

This module defines the `DailyGifts` class, which provides methods to collect various types of 
daily gifts, including standard gifts, VIP gifts, and alliance gifts.
"""

from ..base_gge_socket import BaseGgeSocket

class DailyGifts(BaseGgeSocket):
    """
    A class for interacting with the Daily Gifts feature in Goodgame Empire.

    This class provides methods to collect standard daily gifts, VIP gifts, 
    and alliance gifts.
    """

    def collect_daily_gift(self, choice: str, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect a standard daily gift.

        Args:
            choice (str): The type of gift to collect.
                - "MS1": 1 minute time skip
                - "F": Food gift
                - "U" + wod_id: Unit gift
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("clb", {
                "ID": -1,
                "I": choice,
                "SP": None
            })
            if sync:
                response = self.wait_for_json_response("clb")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_daily_gift_vip(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect the VIP daily gift.

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
            self.send_json_command("clb", {
                "ID": -1,
                "I": None,
                "SP": "VIP"
            })
            if sync:
                response = self.wait_for_json_response("clb")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_daily_gift_alliance(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect the alliance daily gift.

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
            self.send_json_command("clb", {
                "ID": -1,
                "I": None,
                "SP": "ALLI"
            })
            if sync:
                response = self.wait_for_json_response("clb")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
