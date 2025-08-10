"""
This module contains the class for interacting with the Goodgame Empire API's friends-related functions.

The `Friends` class provides methods for getting friends and sending emails to other players. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Friends(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's friends-related functions.

    This class provides methods for getting friends and sending emails to other players. It is a subclass of `BaseGgeSocket`.
    """

    def get_friends(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Get the list of friends.

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
            self.send_json_command("gfc", {})
            if sync:
                response = self.wait_for_json_response("gfc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def send_email(
        self, sender_name: str, target_name: str, target_email: str, message: str, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Send an email to another player.

        Args:
            sender_name (str): The name of the sender.
            target_name (str): The name of the recipient.
            target_email (str): The email address of the recipient.
            message (str): The message to send.
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
                "sem",
                {
                    "SN": sender_name,
                    "TN": target_name,
                    "EM": target_email,
                    "TXT": message,
                },
            )
            if sync:
                response = self.wait_for_json_response("sem")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
