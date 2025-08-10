"""
Module for handling in-game purchases in Goodgame Empire.

This module defines the `Shop` class, which provides methods to buy various in-game items 
from different shops, including the VIP shop, master blacksmith, traveling merchant, 
armorer, and more.
"""

from ..base_gge_socket import BaseGgeSocket

class Shop(BaseGgeSocket):
    """
    A class for handling in-game purchases in Goodgame Empire.

    This class provides methods to buy various items from different shops, including 
    VIP time, VIP points, blacksmith items, armorer gear, and more.
    """

    def buy_package_generic(self, kingdom: int, shop_type: int, shop_id: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase a package from a specified shop.

        Args:
            kingdom (int): The ID of the kingdom where the shop is located.
            shop_type (int): The type of shop.
            shop_id (int): The ID of the specific shop.
            package_id (int): The ID of the package to purchase.
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
            self.send_json_command("sbp", {
                "PID": package_id,
                "BT": shop_type,
                "TID": shop_id,
                "AMT": amount,
                "KID": kingdom,
                "AID": -1,
                "PC2": -1,
                "BA": 0,
                "PWR": 0,
                "_PO": -1
            })
            if sync:
                response = self.wait_for_json_response("sbp")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def buy_vip_time(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase VIP time.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the VIP time package.
                - 170: 1 day
                - 171: 7 days
                - 172: 30 days
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 2, -1, package_id, amount, sync, quiet)

    def buy_vip_points(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase VIP points.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the VIP points package.
                - 167: 300 points
                - 168: 1500 points
                - 169: 4500 points
            amount (int): The quantity to buy.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 2, -1, package_id, amount, sync, quiet)

    def buy_from_master_blacksmith(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase items from the master blacksmith.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the package to purchase.
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 0, 116, package_id, amount, sync, quiet)

    def buy_from_nomad_shop(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase items from the nomad shop.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the package to purchase.
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 0, 94, package_id, amount, sync, quiet)

    def buy_from_nomad_armorer(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase items from the nomad armorer.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the package to purchase.
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 0, 49, package_id, amount, sync, quiet)

    def buy_from_traveling_merchant(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase items from the traveling merchant.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the package to purchase.
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 0, 22, package_id, amount, sync, quiet)

    def buy_from_armorer(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase items from the armorer.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the package to purchase.
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 0, 27, package_id, amount, sync, quiet)

    def buy_from_blacksmith(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase items from the blacksmith.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the package to purchase.
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 0, 101, package_id, amount, sync, quiet)

    def buy_from_gift_seller(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase items from the gift seller.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the package to purchase.
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 0, 66, package_id, amount, sync, quiet)

    def buy_from_blade_coast_shop(self, kingdom: int, package_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase items from the blade coast shop.

        Args:
            kingdom (int): The ID of the kingdom.
            package_id (int): The ID of the package to purchase.
            amount (int): The quantity to buy.
            sync (bool, optional): If True, waits for a response. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.buy_package_generic(kingdom, 0, 4, package_id, amount, sync, quiet)

    def set_buying_castle(self, castle_id: int, kingdom: int = 0, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Set the castle where purchases will be delivered.

        Args:
            castle_id (int): The ID of the castle.
            kingdom (int, optional): The kingdom where the castle is located. Defaults to 0.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("gbc", {
                "CID": castle_id,
                "KID": kingdom
            })
            if sync:
                response = self.wait_for_json_response("gbc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
