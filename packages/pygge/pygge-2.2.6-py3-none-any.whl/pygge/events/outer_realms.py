"""
Module for interacting with the Outer Realms event in Goodgame Empire.

This module defines the `OuterRealms` class, which provides methods to retrieve event points, 
select a castle, obtain a token, and log in to the event.
"""

from ..base_gge_socket import BaseGgeSocket

class OuterRealms(BaseGgeSocket):
    """
    A class to interact with the Outer Realms event in Goodgame Empire.

    This class provides methods for retrieving event points, selecting a castle, 
    obtaining tokens, and logging into the event.
    """

    def get_outer_realms_points(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve the player's Outer Realms event points.

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
            self.send_json_command("tsh", {})
            if sync:
                response = self.wait_for_json_response("tsh")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def choose_outer_realm_castle(self, castle_id: int, only_rubies: int = 0, use_rubies: int = 0, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Select a castle for the Outer Realms event.

        Args:
            castle_id (int): The ID of the castle to choose.
            only_rubies (int, optional): If True, only use rubies for the selection. Defaults to 0.
            use_rubies (int, optional): If True, use rubies for the selection. Defaults to 0.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("tsc", {
                "ID": castle_id,
                "OC2": only_rubies,
                "PWR": use_rubies,
                "GST": 2
            })
            if sync:
                response = self.wait_for_json_response("tsc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_outer_realm_token(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve the Outer Realms event token.

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
            self.send_json_command("glt", {
                "GST": 2
            })
            if sync:
                response = self.wait_for_json_response("glt")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def login_outer_realm(self, token: str, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Log in to the Outer Realms event using a token.

        Args:
            token (str): The event token used for authentication.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("tlep", {
                "TLT": token
            })
            if sync:
                response = self.wait_for_json_response("lli")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
