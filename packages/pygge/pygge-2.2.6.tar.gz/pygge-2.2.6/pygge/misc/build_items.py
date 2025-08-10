"""
Module for managing build items in Goodgame Empire.

This module defines the `BuildItems` class, which provides a method to equip build items 
to buildings in castles across different kingdoms.
"""

from ..base_gge_socket import BaseGgeSocket

class BuildItems(BaseGgeSocket):
    """
    A class for managing build items in Goodgame Empire.

    This class provides a method to equip build items to buildings in a specified castle 
    within a given kingdom.
    """

    def equip_build_item(self, kingdom_id: int, castle_id: int, building_id: int, slot_id: int, item_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Equip a build item to a building.

        Args:
            kingdom_id (int): The ID of the kingdom where the castle is located.
            castle_id (int): The ID of the castle where the building is located.
            building_id (int): The ID of the building to equip the item to.
            slot_id (int): The slot ID where the item will be equipped.
            item_id (int): The ID of the build item being equipped.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("rpc", {
                "OID": building_id,
                "CID": item_id,
                "SID": slot_id,
                "M": 0,
                "KID": kingdom_id,
                "AID": castle_id
            })
            if sync:
                response = self.wait_for_json_response("rpc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
