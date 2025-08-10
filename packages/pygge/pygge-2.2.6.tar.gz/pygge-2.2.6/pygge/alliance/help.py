"""
This module contains the class for interacting with the Goodgame Empire API's help-related functions.

The `Help` class provides methods for helping alliance members and the entire alliance. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Help(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's help-related functions.

    This class provides methods for helping alliance members and the entire alliance. It is a subclass of `BaseGgeSocket`.
    """

    def help_alliance_member(
        self, kingdom: int, help_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Help an alliance member.

        Args:
            kingdom (int): The kingdom number.
            help_id (int): The ID of the member to help.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("ahc", {"LID": help_id, "KID": kingdom})
            if sync:
                response = self.wait_for_json_response("ahc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def help_alliance_all(
        self, kingdom: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Help all alliance members.

        Args:
            kingdom (int): The kingdom number.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("aha", {"KID": kingdom})
            if sync:
                response = self.wait_for_json_response("aha")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
