"""
Module for interacting with the Lucky Wheel feature in Goodgame Empire.

This module defines the `LuckyWheel` class, which provides methods to switch wheel modes,
spin the wheel using different types, and handle rewards.
"""

from ..base_gge_socket import BaseGgeSocket

class LuckyWheel(BaseGgeSocket):
    """
    A class for interacting with the Lucky Wheel feature in Goodgame Empire.

    This class provides methods for switching the wheel mode and spinning the 
    wheel in both classic and premium modes.
    """

    def switch_lucky_wheel_mode(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Switch the Lucky Wheel mode.

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
            self.send_json_command("lwm", {})
            if sync:
                response = self.wait_for_json_response("lwm")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def spin_lucky_wheel(self, wheel_type: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Spin the Lucky Wheel.

        Args:
            wheel_type (int): The type of wheel to spin.
                - 0: Classic Lucky Wheel
                - 1: Paid Lucky Wheel
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("lws", {
                "LWET": wheel_type
            })
            if sync:
                response = self.wait_for_json_response("lws")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def spin_classic_lucky_wheel(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Spin the Classic Lucky Wheel.

        Args:
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.spin_lucky_wheel(0, sync, quiet)

    def spin_paid_lucky_wheel(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Spin the Paid Lucky Wheel (premium version).

        Args:
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        return self.spin_lucky_wheel(1, sync, quiet)
