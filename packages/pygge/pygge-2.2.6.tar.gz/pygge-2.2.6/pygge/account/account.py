"""
This module contains the class for interacting with the Goodgame Empire API's account-related functions.

The `Account` class contains methods for retrieving and modifying account information. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Account(BaseGgeSocket):
    """
    The main class for interacting with the Goodgame Empire API's account-related functions.

    This class contains methods for retrieving and modifying account information. It is a subclass of `BaseGgeSocket`.
    """

    def get_account_infos(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve account information.

        Sends a command to retrieve account information and optionally waits for a response.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The account information if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("gpi", {})
            if sync:
                response = self.wait_for_json_response("gpi")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def register_email(
        self,
        email: str,
        subscribe: bool = False,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Register an email address.

        Sends a command to register an email address and optionally waits for a response.

        Args:
            email (str): The email address to register.
            subscribe (bool, optional): Whether to subscribe to the newsletter. Defaults to False.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("vpm", {"MAIL": email, "NEWSLETTER": subscribe})
            if sync:
                response = self.wait_for_json_response("vpm")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_username_change_infos(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Retrieve information about changing the username.

        Sends a command to retrieve information about changing the username and optionally waits for a response.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("gnci", {})
            if sync:
                response = self.wait_for_json_response("gnci")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def change_username(
        self, new_username: str, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Change the username.

        Sends a command to change the username and optionally waits for a response.

        Args:
            new_username (str): The new username.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("cpne", {"PN": new_username})
            if sync:
                response = self.wait_for_json_response("cpne")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def change_password(
        self,
        old_password: str,
        new_password: str,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Change the password.

        Sends a command to change the password and optionally waits for a response.

        Args:
            old_password (str): The old password.
            new_password (str): The new password.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("scp", {"OPW": old_password, "NPW": new_password})
            if sync:
                response = self.wait_for_json_response("scp")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def ask_email_change(
        self, new_email: str, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Request a change of email address.

        Sends a command to request a change of email address and optionally waits for a response.

        Args:
            new_email (str): The new email address.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("rmc", {"PMA": new_email})
            if sync:
                response = self.wait_for_json_response("rmc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_email_change_status(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Retrieve the status of the email change.

        Sends a command to retrieve the status of the email change and optionally waits for a response.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("mns", {})
            if sync:
                response = self.wait_for_json_response("mns")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def cancel_email_change(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Cancel the email change.

        Sends a command to cancel the email change and optionally waits for a response.

        Args:
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("cmc", {})
            if sync:
                response = self.wait_for_json_response("cmc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def activate_facebook_connection(
        self,
        facebook_id: str,
        facebook_token: str,
        facebook_account_id: str,
        activate: bool = True,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Activate or deactivate the Facebook connection.

        Sends a command to activate or deactivate the Facebook connection and optionally waits for a response.

        Args:
            facebook_id (str): The Facebook ID.
            facebook_token (str): The Facebook token.
            facebook_account_id (str): The Facebook account ID.
            activate (bool, optional): Whether to activate or deactivate the connection. Defaults to True.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:

            self.send_json_command(
                "fcs",
                {
                    "SFC": activate,
                    "FID": facebook_id,
                    "FTK": facebook_token,
                    "FAID": facebook_account_id,
                },
            )
            if sync:
                response = self.wait_for_json_response("fcs")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
