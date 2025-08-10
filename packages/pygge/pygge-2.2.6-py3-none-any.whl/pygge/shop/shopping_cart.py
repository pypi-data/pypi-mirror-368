"""
Module for managing the shopping cart in Goodgame Empire.

This module defines the `ShoppingCart` class, which provides a method to modify 
the shopping cart by selecting packages for different sections.
"""

from ..base_gge_socket import BaseGgeSocket

class ShoppingCart(BaseGgeSocket):
    """
    A class for managing the shopping cart in Goodgame Empire.

    This class provides a method to edit the shopping cart by selecting packages 
    for different sections.
    """

    def edit_shopping_cart(self, packages_left: list[int] = [], packages_middle: list[int] = [], packages_right: list[int] = [], sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Modify the shopping cart by selecting packages.

        Args:
            packages_left (list[int], optional): List of package IDs to place in the left section of the cart. Defaults to an empty list.
            packages_middle (list[int], optional): List of package IDs to place in the middle section of the cart. Defaults to an empty list.
            packages_right (list[int], optional): List of package IDs to place in the right section of the cart. Defaults to an empty list.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("ssc", {
                "IGC": 0,
                "SCA": packages_left,
                "SCB": packages_middle,
                "SCC": packages_right
            })
            if sync:
                response = self.wait_for_json_response("ssc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
