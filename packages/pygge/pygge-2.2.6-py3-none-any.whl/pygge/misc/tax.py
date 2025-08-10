"""
Module for managing the tax system in Goodgame Empire.

This module defines the `Tax` class, which provides methods to retrieve tax information, 
start a tax collection process, and collect earned taxes.
"""

from ..base_gge_socket import BaseGgeSocket

class Tax(BaseGgeSocket):
    """
    A class for managing the tax system in Goodgame Empire.

    This class provides methods to retrieve tax information, start tax collection, 
    and collect accumulated taxes.
    """

    def get_tax_infos(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve tax-related information.

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
            self.send_json_command("txi", {})
            if sync:
                response = self.wait_for_json_response("txi")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def start_tax(self, tax_type: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Start a tax collection process.

        Args:
            tax_type (int): The type of tax collection to initiate.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("txs", {
                "TT": tax_type,
                "TX": 3
            })
            if sync:
                response = self.wait_for_json_response("txs")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_tax(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect the accumulated tax.

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
            self.send_json_command("txc", {
                "TR": 29
            })
            if sync:
                response = self.wait_for_json_response("txc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
