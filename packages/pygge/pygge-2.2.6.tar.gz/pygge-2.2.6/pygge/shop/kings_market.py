"""
Module for interacting with the King's Market in Goodgame Empire.

This module defines the `KingsMarket` class, which provides methods to purchase 
King's banners, activate protection, buy production slots, open castle gates, 
and buy feasts.
"""

from ..base_gge_socket import BaseGgeSocket

class KingsMarket(BaseGgeSocket):
    """
    A class for interacting with the King's Market in Goodgame Empire.

    This class provides methods to buy King's banners, activate protection, 
    purchase production slots, open castle gates, and buy feasts.
    """

    def buy_king_banner(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase a King’s Banner.

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
            self.send_json_command("gbp", {})
            if sync:
                response = self.wait_for_json_response("gbp")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def start_protection(self, duration: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Activate protection for a specified duration.

        Args:
            duration (int): The duration of the protection.
                - 0: 7 days
                - 1: 14 days
                - 2: 21 days
                - 3: 60 days
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("mps", {
                "CD": duration
            })
            if sync:
                response = self.wait_for_json_response("mps")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def buy_production_slot(self, queue_type: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase an additional production slot.

        Args:
            queue_type (int): The type of production queue.
                - 0: Barracks
                - 1: Workshop
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("ups", {
                "LID": queue_type
            })
            if sync:
                response = self.wait_for_json_response("ups")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def open_gates(self, kingdom: int, castle_id: int, duration: int = 0, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Open castle gates for a specified duration.

        Args:
            kingdom (int): The ID of the kingdom where the castle is located.
            castle_id (int): The ID of the castle.
            duration (int, optional): The duration for which the gates will be open.
                - 0: 6 hours
                - 1: 12 hours
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("mos", {
                "CID": castle_id,
                "KID": kingdom,
                "CD": duration
            })
            if sync:
                response = self.wait_for_json_response("mos")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def buy_feast(self, kingdom: int, castle_id: int, feast_type: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase a feast.

        Args:
            kingdom (int): The ID of the kingdom where the feast will take place.
            castle_id (int): The ID of the castle where the feast is hosted.
            feast_type (int): The type of feast to buy (0-9).
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("bfs", {
                "CID": castle_id,
                "KID": kingdom,
                "T": feast_type,
                "PO": -1,
                "PWR": 0
            })
            if sync:
                response = self.wait_for_json_response("bfs")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
