"""
This module contains the class for interacting with the Goodgame Empire API's extension-related functions.

The `Extension` class provides methods for buying and collecting extensions. It is a subclass of `BaseGge
"""

from ..base_gge_socket import BaseGgeSocket


class Extension(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's extension-related functions.

    This class provides methods for buying and collecting extensions. It is a subclass of `BaseGgeSocket`.
    """

    def buy_extension(
        self, x: int, y: int, rotated: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Buy an extension.

        Args:
            x (int): The X coordinate of the extension.
            y (int): The Y coordinate of the extension.
            rotated (int): The rotation of the extension.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("ebe", {"X": x, "Y": y, "R": rotated, "CT": 1})
            if sync:
                response = self.wait_for_json_response("ebe")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_extension_gift(
        self, building_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Collect an extension gift.

        Args:
            building_id (int): The building ID of the extension gift.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("etc", {"OID": building_id})
            if sync:
                response = self.wait_for_json_response("etc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
