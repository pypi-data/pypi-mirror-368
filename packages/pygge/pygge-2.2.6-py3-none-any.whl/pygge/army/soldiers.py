"""
This module contains the class for interacting with the Goodgame Empire API's soldiers-related functions.

The `Soldiers` class provides methods for recruiting soldiers and managing the recruitment queue. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Soldiers(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's soldiers-related functions.

    This class provides methods for recruiting soldiers and managing the recruitment queue. It is a subclass of `BaseGgeSocket`.
    """

    def get_recruitment_queue(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Get the recruitment queue.

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
            self.send_json_command("spl", {"LID": 0})
            if sync:
                response = self.wait_for_json_response("spl")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def recruit_soldiers(
        self,
        castle_id: int,
        wod_id: int,
        amount: int,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Recruit soldiers.

        Args:
            castle_id (int): The ID of the castle to recruit soldiers from.
            wod_id (int): The type of soldier to recruit.
            amount (int): The number of soldiers to recruit.
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
                    "LID": 0,
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

    def double_recruitment_slot(
        self,
        castle_id: int,
        slot_type: str,
        slot: int,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Double the recruitment slot.

        Args:
            castle_id (int): The ID of the castle to double the recruitment slot for.
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
                {"LID": 0, "S": slot, "AID": castle_id, "SID": 0, "ST": slot_type},
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

    def cancel_recruitment(
        self, slot_type: str, slot: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Cancel a recruitment operation.

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
            self.send_json_command("mcu", {"LID": 0, "S": slot, "ST": slot_type})
            if sync:
                response = self.wait_for_json_response("mcu")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def ask_alliance_help_recruit(
        self, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Ask for alliance help in recruiting soldiers.

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
            self.send_json_command("ahr", {"ID": 0, "T": 6})
            if sync:
                response = self.wait_for_json_response("ahr")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
