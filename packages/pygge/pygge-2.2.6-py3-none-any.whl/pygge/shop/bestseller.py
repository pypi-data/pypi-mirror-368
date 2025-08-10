"""
Module for handling purchases from the Bestseller shop in Goodgame Empire.

This module defines the `Bestseller` class, which provides a method to buy items 
from the Bestseller shop using a specified package type and amount.
"""

from ..base_gge_socket import BaseGgeSocket

class Bestseller(BaseGgeSocket):
    """
    A class for handling purchases from the Bestseller shop in Goodgame Empire.

    This class provides a method to buy items from the Bestseller shop using a specific 
    bestseller ID, package type, and amount.
    """

    def buy_from_bestseller(self, bestseller_id: int, package_type: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase an item from the Bestseller shop.

        Args:
            bestseller_id (int): The ID of the Bestseller offer.
            package_type (int): The type of package being purchased.
            amount (int): The quantity of the package to buy.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("bso", {
                "OID": package_type,
                "AMT": amount,
                "POID": bestseller_id
            })
            if sync:
                response = self.wait_for_json_response("bso")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
