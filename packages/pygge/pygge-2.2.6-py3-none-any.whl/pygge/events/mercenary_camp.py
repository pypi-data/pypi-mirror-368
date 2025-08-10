"""
Module for interacting with the Mercenary Camp feature in Goodgame Empire.

This module defines the `MercenaryCamp` class, which provides methods to retrieve, refresh, 
start, skip, and collect rewards from mercenary missions.
"""

from ..base_gge_socket import BaseGgeSocket

class MercenaryCamp(BaseGgeSocket):
    """
    A class for interacting with the Mercenary Camp feature in Goodgame Empire.

    This class provides methods for managing mercenary missions, including retrieving available missions, 
    refreshing missions, starting missions, skipping missions, and collecting rewards.
    """

    def get_mercenary_missions(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve available mercenary missions.

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
            self.send_json_command("mpe", {
                "MID": -1
            })
            if sync:
                response = self.wait_for_json_response("mpe")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def refresh_mercenary_mission(self, mission_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Refresh a specific mercenary mission.

        Args:
            mission_id (int): The ID of the mission to refresh.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("rmm", {
                "MID": mission_id
            })
            if sync:
                response = self.wait_for_json_response("rmm")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def start_mercenary_mission(self, mission_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Start a mercenary mission.

        Args:
            mission_id (int): The ID of the mission to start.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("mpe", {
                "MID": mission_id
            })
            if sync:
                response = self.wait_for_json_response("mpe")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def skip_mercenary_mission(self, mission_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Skip a mercenary mission.

        Args:
            mission_id (int): The ID of the mission to skip.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("mpe", {
                "MID": mission_id
            })
            if sync:
                response = self.wait_for_json_response("mpe")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def collect_mercenary_mission(self, mission_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Collect rewards from a completed mercenary mission.

        Args:
            mission_id (int): The ID of the mission to collect rewards from.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("mpe", {
                "MID": mission_id
            })
            if sync:
                response = self.wait_for_json_response("mpe")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
