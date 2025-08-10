"""
This module contains the class for interacting with the Goodgame Empire API's repair-related functions.

The `Repair` class provides methods for repairing buildings. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Repair(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's repair-related functions.

    This class provides methods for repairing buildings. It is a subclass of `BaseGgeSocket`.
    """

    def repair_building(
        self, building_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Repair a building.

        Args:
            building_id (int): The ID of the building to repair.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("rbu", {"OID": building_id, "PO": -1, "PWR": 0})
            if sync:
                response = self.wait_for_json_response("rbu")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def ask_alliance_help_repair(
        self, building_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Ask for alliance help to repair a building.

        Args:
            building_id (int): The ID of the building to repair.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("ahr", {"ID": building_id, "T": 3})
            if sync:
                response = self.wait_for_json_response("ahr")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def repair_all(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Repair all damaged buildings.

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
            self.send_json_command("ira", {})
            if sync:
                response = self.wait_for_json_response("ira")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
