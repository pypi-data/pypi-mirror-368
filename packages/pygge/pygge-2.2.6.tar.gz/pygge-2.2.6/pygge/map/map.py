"""
Module for interacting with the world map in Goodgame Empire.

This module defines the `Map` class, which provides methods to retrieve map chunks, 
locate NPCs, and fetch target information.
"""

from ..base_gge_socket import BaseGgeSocket

class Map(BaseGgeSocket):
    """
    A class for interacting with the world map in Goodgame Empire.

    This class provides methods to retrieve specific map chunks, locate NPCs, 
    and fetch information about target locations.
    """

    def get_map_chunk(self, kingdom: int, x: int, y: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve a chunk of the world map.

        Args:
            kingdom (int): The ID of the kingdom to retrieve the map chunk from.
            x (int): The x-coordinate of the top-left corner of the chunk.
            y (int): The y-coordinate of the top-left corner of the chunk.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("gaa", {
                "KID": kingdom,
                "AX1": x,
                "AY1": y,
                "AX2": x + 12,
                "AY2": y + 12
            })
            if sync:
                response = self.wait_for_json_response("gaa")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_closest_npc(self, kingdom: int, npc_type: int, min_level: int = 1, max_level: int = -1, owner_id: int = -1, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Locate the closest NPC based on given criteria.

        Args:
            kingdom (int): The ID of the kingdom to search in.
            npc_type (int): The type of NPC to locate.
            min_level (int, optional): The minimum level of the NPC. Defaults to 1.
            max_level (int, optional): The maximum level of the NPC (-1 for no limit). Defaults to -1.
            owner_id (int, optional): The ID of the NPC owner (-1 for any owner). Defaults to -1.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("fnm", {
                "T": npc_type,
                "KID": kingdom,
                "LMIN": min_level,
                "LMAX": max_level,
                "NID": owner_id
            })
            if sync:
                response = self.wait_for_json_response("fnm")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_target_infos(self, kingdom: int, sx: int, sy: int, tx: int, ty: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve information about a specific target on the map.

        Args:
            kingdom (int): The ID of the kingdom where the target is located.
            sx (int): The x-coordinate of the starting position.
            sy (int): The y-coordinate of the starting position.
            tx (int): The x-coordinate of the target.
            ty (int): The y-coordinate of the target.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("adi", {
                "SX": sx,
                "SY": sy,
                "TX": tx,
                "TY": ty,
                "KID": kingdom
            })
            if sync:
                response = self.wait_for_json_response("adi")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
