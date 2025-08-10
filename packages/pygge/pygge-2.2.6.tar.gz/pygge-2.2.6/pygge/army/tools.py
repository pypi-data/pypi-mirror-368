"""
This module contains the class for interacting with the Goodgame Empire API's tools-related functions.

The `Tools` class provides methods for producing tools and managing the production queue. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Tools(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's tools-related functions.

    This class provides methods for producing tools and managing the production queue. It is a subclass of `BaseGgeSocket`.
    """

    def get_production_queue(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Get the production queue.

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
            self.send_json_command("spl", {"LID": 1})
            if sync:
                response = self.wait_for_json_response("spl")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def produce_tools(
        self,
        castle_id: int,
        wod_id: int,
        amount: int,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Produce tools.

        Args:
            castle_id (int): The ID of the castle to produce tools in.
            wod_id (int): The type of tool to produce.
            amount (int): The number of tools to produce.
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
                "bup",
                {
                    "LID": 1,
                    "WID": wod_id,
                    "AMT": amount,
                    "PO": -1,
                    "PWR": 0,
                    "SK": 73,
                    "SID": 0,
                    "AID": castle_id,
                },
            )
            if sync:
                response = self.wait_for_json_response("bup")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def double_production_slot(
        self,
        castle_id: int,
        slot_type: str,
        slot: int,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Double the production slot.

        Args:
            castle_id (int): The ID of the castle to double the production slot in.
            slot_type (str): The type of slot to double. Either "production" or "queue".
            slot (int): The slot number to double.
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
                "bou",
                {"LID": 1, "S": slot, "AID": castle_id, "SID": 0, "ST": slot_type},
            )
            if sync:
                response = self.wait_for_json_response("bou")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def cancel_production(
        self, slot_type: str, slot: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Cancel a production operation.

        Args:
            slot_type (str): The type of slot to cancel. Either "production" or "queue".
            slot (int): The slot number to cancel.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("mcu", {"LID": 1, "S": slot, "ST": slot_type})
            if sync:
                response = self.wait_for_json_response("mcu")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
