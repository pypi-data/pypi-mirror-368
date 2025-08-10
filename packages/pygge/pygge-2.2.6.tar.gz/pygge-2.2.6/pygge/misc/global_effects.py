"""
Module for managing global effects in Goodgame Empire.

This module defines the `GlobalEffects` class, which provides methods to retrieve active 
global effects and upgrade specific effects.
"""

from ..base_gge_socket import BaseGgeSocket

class GlobalEffects(BaseGgeSocket):
    """
    A class for managing global effects in Goodgame Empire.

    This class provides methods to retrieve currently active global effects 
    and upgrade specific effects.
    """

    def get_global_effects(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve a list of currently active global effects.

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
            self.send_json_command("usg", {})
            if sync:
                response = self.wait_for_json_response("usg")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def upgrade_global_effect(self, effect_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Upgrade a specific global effect.

        Args:
            effect_id (int): The ID of the global effect to upgrade.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("agb", {
                "GEID": effect_id
            })
            if sync:
                response = self.wait_for_json_response("agb")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
