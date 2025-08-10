"""
This module contains the class for interacting with the Goodgame Empire API's hospital-related functions.

The `Hospital` class provides methods for healing wounded soldiers and managing the hospital. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Hospital(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's hospital-related functions.

    This class provides methods for healing wounded soldiers and managing the hospital. It is a subclass of `BaseGgeSocket`.
    """

    def heal(
        self, wod_id: int, amount: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Heal wounded soldiers.

        Args:
            wod_id (int): The type of wounded soldier to heal.
            amount (int): The number of soldiers to heal.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("hru", {"U": wod_id, "A": amount})
            if sync:
                response = self.wait_for_json_response("hru")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def cancel_heal(
        self, slot_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Cancel a healing operation.

        Args:
            slot_id (int): The slot ID of the healing operation to cancel.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("hcs", {"S": slot_id})
            if sync:
                response = self.wait_for_json_response("hcs")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def skip_heal(
        self, slot_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Skip a healing operation.

        Args:
            slot_id (int): The slot ID of the healing operation to complete.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("hss", {"S": slot_id})
            if sync:
                response = self.wait_for_json_response("hss")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def delete_wounded(
        self, wod_id: int, amount: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Delete wounded soldiers.

        Args:
            wod_id (int): The type of wounded soldier to delete.
            amount (int): The number of soldiers to delete.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("hdu", {"U": wod_id, "A": amount})
            if sync:
                response = self.wait_for_json_response("hdu")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def heal_all(
        self, max_cost: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Heal all wounded soldiers.

        Args:
            max_cost (int): The maximum number of rubies to spend on healing.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("hra", {"C2": max_cost})
            if sync:
                response = self.wait_for_json_response("hra")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def ask_alliance_help_heal(
        self, package_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Ask for alliance help in healing wounded soldiers.

        Args:
            package_id (int): The ID of the healing package.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("ahr", {"ID": package_id, "T": 2})
            if sync:
                response = self.wait_for_json_response("ahr")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
