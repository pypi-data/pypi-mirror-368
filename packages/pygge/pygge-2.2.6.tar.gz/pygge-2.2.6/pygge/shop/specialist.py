"""
Module for managing specialist purchases in Goodgame Empire.

This module defines the `Specialist` class, which provides methods to buy various 
specialist services, such as market carts, marauders, overseers, travel maps, 
tax collectors, and drill instructors.
"""

from ..base_gge_socket import BaseGgeSocket

class Specialist(BaseGgeSocket):
    """
    A class for managing specialist purchases in Goodgame Empire.

    This class provides methods to buy market carts, marauders, overseers, 
    travel maps, tax collectors, and drill instructors.
    """

    def buy_market_carts(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase market carts.

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
            self.send_json_command("bcs", {
                "PO": -1
            })
            if sync:
                response = self.wait_for_json_response("bcs")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def buy_marauder(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase a marauder.

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
            self.send_json_command("bms", {
                "PO": -1
            })
            if sync:
                response = self.wait_for_json_response("bms")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def buy_overseer(self, resource_type: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase an overseer for resource management.

        Args:
            resource_type (int): The type of resource overseer to buy.
                - 0: Wood
                - 1: Stone
                - 2: Food
                - ???: Honey (unknown)
                - ???: Mead (unknown)
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("bos", {
                "T": resource_type,
                "PO": -1
            })
            if sync:
                response = self.wait_for_json_response("bos")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def buy_travel_maps(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase travel maps.

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
            self.send_json_command("brs", {
                "PO": -1
            })
            if sync:
                response = self.wait_for_json_response("brs")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def buy_tax_collector(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase a tax collector.

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
            self.send_json_command("btx", {
                "PO": -1
            })
            if sync:
                response = self.wait_for_json_response("btx")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def buy_drill_instructor(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Purchase a drill instructor.

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
            self.send_json_command("bis", {
                "PO": -1
            })
            if sync:
                response = self.wait_for_json_response("bis")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
