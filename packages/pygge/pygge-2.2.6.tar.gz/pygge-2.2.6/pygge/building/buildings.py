"""
This module contains the class for interacting with the Goodgame Empire API's building-related functions.

The `Buildings` class provides methods for building, upgrading, moving, selling, and destroying buildings. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket

import time


class Buildings(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's building-related functions.

    This class provides methods for building, upgrading, moving, selling, and destroying buildings. It is a subclass of `BaseGgeSocket`.
    """

    def build(
        self,
        wod_id: int,
        x: int,
        y: int,
        rotated: int = 0,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Build a building.

        Args:
            wod_id (int): The type of building to build.
            x (int): The X coordinate of the building.
            y (int): The Y coordinate of the building.
            rotated (int, optional): The rotation of the building. Defaults to 0.
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
                "ebu",
                {
                    "WID": wod_id,
                    "X": x,
                    "Y": y,
                    "R": rotated,
                    "PWR": 0,
                    "PO": -1,
                    "DOID": -1,
                },
            )
            if sync:
                response = self.wait_for_json_response("ebu")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def upgrade_building(
        self, building_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Upgrade a building.

        Args:
            building_id (int): The ID of the building to upgrade.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("eup", {"OID": building_id, "PWR": 0, "PO": -1})
            if sync:
                response = self.wait_for_json_response("eup")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def move_building(
        self,
        building_id: int,
        x: int,
        y: int,
        rotated: int = 0,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Move a building.

        Args:
            building_id (int): The ID of the building to move.
            x (int): The new X coordinate of the building.
            y (int): The new Y coordinate of the building.
            rotated (int, optional): The new rotation of the building. Defaults to 0.
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
                "emo", {"OID": building_id, "X": x, "Y": y, "R": rotated}
            )
            if sync:
                response = self.wait_for_json_response("emo")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def sell_building(
        self, building_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Sell a building.

        Args:
            building_id (int): The ID of the building to sell.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("sbd", {"OID": building_id})
            if sync:
                response = self.wait_for_json_response("sbd")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def destroy_building(
        self, building_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Destroy a building.

        Args:
            building_id (int): The ID of the building to destroy.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("edo", {"OID": building_id})
            if sync:
                response = self.wait_for_json_response("edo")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def skip_construction(
        self,
        building_id: int,
        free_skip: int = 1,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Skip construction of a building.

        Args:
            building_id (int): The ID of the building to skip construction for.
            free_skip (int, optional): Whether to use only free skip. Defaults to 1.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("fco", {"OID": building_id, "FS": free_skip})
            if sync:
                response = self.wait_for_json_response("fco")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def time_skip_construction(
        self,
        building_id: int,
        time_skip: str,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Skip construction of a building.

        Args:
            building_id (int): The ID of the building to skip construction for.
            time_skip (str): The type of time skip to use.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("msb", {"OID": building_id, "MST": time_skip})
            if sync:
                response = self.wait_for_json_response("msb")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def wait_finish_construction(
        self, building_id: int, timeout: int = 5, quiet: bool = False
    ) -> dict | bool:
        """
        Wait for a building to finish construction.

        Args:
            building_id (int): The ID of the building to wait for.
            timeout (int, optional): The time to wait for a response. Defaults to 5.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if the operation was successful.
            bool: False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            response = self.wait_for_json_response(
                "fbe", {"OID": building_id}, timeout=timeout
            )
            self.raise_for_status(response)
            return response
        except Exception as e:
            if not quiet:
                raise e
            return False

    def instant_build(
        self,
        building_id: int,
        wod_id: int,
        x: int,
        y: int,
        rotated: int = 0,
        time_skips: list[str] = [],
        cooldown: int = 0,
        free_skip: int = 1,
        sync: bool = True,
        quiet: bool = False,
    ) -> None:
        """
        Instantly build a building.

        Args:
            building_id (int): The ID of the building to build.
            wod_id (int): The type of building to build.
            x (int): The X coordinate of the building.
            y (int): The Y coordinate of the building.
            rotated (int, optional): The rotation of the building. Defaults to 0.
            time_skips (list[str], optional): The types of time skips to use. Defaults to [].
            cooldown (int, optional): The time in seconds to wait before skipping construction. Defaults to 0.
            free_skip (int, optional): Whether to use only free skip. Defaults to 1.
            sync (bool, optional): If True, wait for a response. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions. Defaults to False.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        self.build(wod_id, x, y, rotated, sync=sync, quiet=quiet)
        for skip in time_skips:
            self.time_skip_construction(building_id, skip, sync=sync, quiet=quiet)
        time.sleep(cooldown)
        self.skip_construction(building_id, free_skip, sync=sync, quiet=quiet)
        if sync:
            self.wait_finish_construction(building_id, quiet=quiet)

    def instant_upgrade(
        self,
        building_id: int,
        time_skips: list[str] = [],
        cooldown: int = 0,
        free_skip: int = 1,
        sync: bool = True,
        quiet: bool = False,
    ) -> None:
        """
        Instantly upgrade a building.

        Args:
            building_id (int): The ID of the building to upgrade.
            time_skips (list[str], optional): The types of time skips to use. Defaults to [].
            cooldown (int, optional): The time in seconds to wait before skipping construction. Defaults to 0.
            free_skip (int, optional): Whether to use only free skip. Defaults to 1.
            sync (bool, optional): If True, wait for a response. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions. Defaults to False.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        self.upgrade_building(building_id, sync=sync, quiet=quiet)
        for skip in time_skips or []:
            self.time_skip_construction(building_id, skip, sync=sync, quiet=quiet)
        time.sleep(cooldown)
        self.skip_construction(building_id, free_skip, sync=sync, quiet=quiet)
        if sync:
            self.wait_finish_construction(building_id, quiet=quiet)

    def instant_destroy(
        self,
        building_id: int,
        time_skips: list[str] = [],
        cooldown: int = 0,
        free_skip: int = 1,
        sync: bool = True,
        quiet: bool = False,
    ) -> None:
        """
        Instantly destroy a building.

        Args:
            building_id (int): The ID of the building to destroy.
            time_skips (list[str], optional): The types of time skips to use. Defaults to [].
            cooldown (int, optional): The time in seconds to wait before skipping construction. Defaults to 0.
            free_skip (int, optional): Whether to use only free skip. Defaults to 1.
            sync (bool, optional): If True, wait for a response. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions. Defaults to False.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        self.destroy_building(building_id, sync=sync, quiet=quiet)
        for skip in time_skips or []:
            self.time_skip_construction(building_id, skip, sync=sync, quiet=quiet)
        time.sleep(cooldown)
        self.skip_construction(building_id, free_skip, sync=sync, quiet=quiet)
