"""
This module contains the class for interacting with the Goodgame Empire API's castle-related functions.

The `Castle` class provides methods for managing castles. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Castle(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's castle-related functions.

    This class provides methods for managing castles. It is a subclass of `BaseGgeSocket`.
    """

    def get_castles(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Get the castles owned by the player.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("gcl", {})
            if sync:
                response = self.wait_for_json_response("gcl")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_detailed_castles(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Get detailed information about the castles owned by the player.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("dcl", {})
            if sync:
                response = self.wait_for_json_response("dcl")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_castle_resources(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Get the resources of the current castle.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("grc", {})
            if sync:
                response = self.wait_for_json_response("grc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_castle_production(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Get the resources production of the current castle.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("gpa", {})
            if sync:
                response = self.wait_for_json_response("gpa")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def go_to_castle(
        self, kingdom: int, castle_id: int = -1, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Go to a castle.

        Args:
            kingdom (int): The kingdom number.
            castle_id (int, optional): The ID of the castle to go to. Defaults to -1 (main castle).
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("jca", {"CID": castle_id, "KID": kingdom})
            if sync:
                response = self.wait_for_json_response("jaa")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def rename_castle(
        self,
        kingdom: int,
        castle_id: int,
        castle_type: int,
        name: str,
        paid: int = 0,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Rename a castle.

        Args:
            kingdom (int): The kingdom number.
            castle_id (int): The ID of the castle to rename.
            castle_type (int): The type of the castle.
            name (str): The new name for the castle.
            paid (int, optional): Whether to use rubies to rename the castle. Defaults to 0.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command(
                "arc",
                {
                    "CID": castle_id,
                    "P": paid,
                    "KID": kingdom,
                    "AT": castle_type,
                    "N": name,
                },
            )
            if sync:
                response = self.wait_for_json_response("arc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def relocate_main_castle(
        self, x: int, y: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Relocate the main castle.

        Args:
            x (int): The x-coordinate to relocate to.
            y (int): The y-coordinate to relocate to.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("rst", {"PX": x, "PY": y})
            if sync:
                response = self.wait_for_json_response("rst")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
