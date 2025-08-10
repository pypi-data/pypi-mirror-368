"""
Module for interacting with the Imperial Patronage feature in Goodgame Empire.

This module defines the `ImperialPatronage` class, which provides methods to 
open the patronage menu and donate resources.
"""

from ..base_gge_socket import BaseGgeSocket

class ImperialPatronage(BaseGgeSocket):
    """
    A class for interacting with the Imperial Patronage system in Goodgame Empire.

    This class provides methods to access the patronage menu and donate various 
    resources or tokens as part of the system.
    """

    def open_imperail_patronage(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Open the Imperial Patronage menu.

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
            self.send_json_command("gdti", {})
            if sync:
                response = self.wait_for_json_response("gdti")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def give_imperial_patronage(self, devise_id: int, amount: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Donate resources or tokens to the Imperial Patronage system.

        Args:
            devise_id (int): The ID of the resource/token being donated.
                - 31: Construction token
                - 32: Sceats
                - 33: Amelioration token
                - 34: Daimyo token
                - 35: Samurai token
                - 36: Khan token
                - 37: Khan tablet
                - Premium IDs:
                    - 38: Imperial Patronage scroll
                    - 39: Construction token
                    - 40: Sceats
                    - 41: Amelioration token
                    - 42: Daimyo token
                    - 43: Samurai token
                    - 44: Khan token
                    - 45: Khan tablet
            amount (int): The quantity of the selected resource/token to donate.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("ddi", {
                "DIV": [{
                    "DII": devise_id, "DIA": amount
                }]
            })
            if sync:
                response = self.wait_for_json_response("ddi")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
