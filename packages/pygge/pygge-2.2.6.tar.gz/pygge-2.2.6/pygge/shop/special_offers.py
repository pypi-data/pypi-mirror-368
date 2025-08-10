"""
Module for handling special offers in Goodgame Empire.

This module defines the `SpecialOffers` class, which provides methods to purchase 
special offers and collect special offer gifts.
"""

from ..base_gge_socket import BaseGgeSocket

class SpecialOffers(BaseGgeSocket):
    """
    A class for handling special offers in Goodgame Empire.

    This class provides methods to purchase special offers and collect 
    gifts associated with special offers.
    """

    def buy_special_offer(self, offer_id: int, package_ids: list[int] = [0], sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase a special offer.

        Args:
            offer_id (int): The ID of the special offer to purchase.
            package_ids (list[int], optional): A list of package IDs included in the offer. Defaults to [0].
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("oop", {
                "OID": offer_id,
                "C": 1,
                "ODI": package_ids
            })
            if sync:
                response = self.wait_for_json_response("oop")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_special_offer_gift(self, gift_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect a special offer gift.

        Args:
            gift_id (int): The ID of the special offer gift to collect.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("oop", {
                "OID": gift_id,
                "C": 1,
                "ODI": [0]
            })
            if sync:
                response = self.wait_for_json_response("oop")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
