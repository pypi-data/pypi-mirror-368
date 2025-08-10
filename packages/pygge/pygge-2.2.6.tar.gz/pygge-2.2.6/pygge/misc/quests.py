"""
Module for managing quests in Goodgame Empire.

This module defines the `Quests` class, which provides methods to retrieve quests, 
complete various types of quests, track recommended quests, and wait for quest completion.
"""

from ..base_gge_socket import BaseGgeSocket

class Quests(BaseGgeSocket):
    """
    A class for managing quests in Goodgame Empire.

    This class provides methods to retrieve available quests, complete message and donation quests, 
    track recommended quests, and handle quest conditions.
    """

    def get_quests(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Retrieve the list of available quests.

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
            self.send_json_command("dcl", {
                "CD": 1
            })
            if sync:
                response = self.wait_for_json_response("dcl")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def complete_message_quest(self, quest_id: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Complete a message-based quest.

        Args:
            quest_id (int): The ID of the quest to complete.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("qsc", {
                "QID": quest_id
            })
            if sync:
                response = self.wait_for_json_response("qsc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def complete_donation_quest(self, quest_id: int, food: int = 0, wood: int = 0, stone: int = 0, gold: int = 0, oil: int = 0, coal: int = 0, iron: int = 0, glass: int = 0, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Complete a donation-based quest by contributing specified resources.

        Args:
            quest_id (int): The ID of the quest to complete.
            food (int, optional): Amount of food to donate. Defaults to 0.
            wood (int, optional): Amount of wood to donate. Defaults to 0.
            stone (int, optional): Amount of stone to donate. Defaults to 0.
            gold (int, optional): Amount of gold to donate. Defaults to 0.
            oil (int, optional): Amount of oil to donate. Defaults to 0.
            coal (int, optional): Amount of coal to donate. Defaults to 0.
            iron (int, optional): Amount of iron to donate. Defaults to 0.
            glass (int, optional): Amount of glass to donate. Defaults to 0.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("qdr", {
                "QID": quest_id,
                "F": food,
                "W": wood,
                "S": stone,
                "C1": gold,
                "O": oil,
                "C": coal,
                "I": iron,
                "G": glass,
                "PWR": 0,
                "PO": -1
            })
            if sync:
                response = self.wait_for_json_response("qdr")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def tracking_recommended_quests(self, quiet: bool = False) -> bool:
        """
        Track recommended quests.

        Args:
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            bool: True if the operation was successful, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("ctr", {
                "TRQ": 0
            })
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def complete_quest_condition(self, quest_id: int, condition: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Complete a specific condition of a quest.

        Args:
            quest_id (int): The ID of the quest.
            condition (int): The condition to complete.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("fcq", {
                "QTID": quest_id,
                "QC": condition
            })
            if sync:
                response = self.wait_for_json_response("fcq")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def wait_finish_quest(self, quest_id: int, timeout: int = 5, quiet: bool = False) -> dict | bool:
        """
        Wait for a quest to be completed.

        Args:
            quest_id (int): The ID of the quest.
            timeout (int, optional): The maximum time to wait for the quest to complete. Defaults to 5 seconds.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if the quest is completed.
            bool: False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            response = self.wait_for_json_response("qfi", {
                "QID": quest_id
            }, timeout=timeout)
            self.raise_for_status(response)
            return response
        except Exception as e:
            if not quiet:
                raise e
            return False
