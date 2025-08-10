"""
Module for handling attack operations in Goodgame Empire.

This module defines the `Attack` class, which provides a method to send an attack with various 
parameters, including army composition, lord selection, horses, tools, and other modifiers.
"""

from ..base_gge_socket import BaseGgeSocket


class Attack(BaseGgeSocket):
    """
    A class for handling attack operations in Goodgame Empire.

    This class provides a method to send an attack, allowing customization of army composition,
    attack strategy, and various modifiers.
    """

    def send_attack(
        self,
        kingdom: int,
        sx: int,
        sy: int,
        tx: int,
        ty: int,
        army: list[dict[str, dict[str, list[list[int]]]]],
        lord_id: int = 0,
        horses_type: int = -1,
        feathers: int = 0,
        slowdown: int = 0,
        boosters: list[list[int]] = [],
        support_tools: list[int] = [],
        final_wave: list[list[int]] = [],
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Send an attack to a target location.

        Args:
            kingdom (int): The ID of the kingdom where the attack is being sent.
            sx (int): The x-coordinate of the starting position.
            sy (int): The y-coordinate of the starting position.
            tx (int): The x-coordinate of the target.
            ty (int): The y-coordinate of the target.
            army (list[dict[str, dict[str, list[list[int]]]]]): The composition of the attacking army.
            lord_id (int, optional): The ID of the lord leading the attack. Defaults to 0.
            horses_type (int, optional): The type of horses used (-1 for default). Defaults to -1.
            feathers (int, optional): Whether to use feathers to speed up the attack. Defaults to 0.
            slowdown (int, optional): The amount of slowdown applied. Defaults to 0.
            boosters (list[list[int]], optional): List of boosters applied to the attack. Defaults to an empty list.
            support_tools (list[int], optional): List of support tools used in the attack. Defaults to an empty list.
            final_wave (list[list[int]], optional): The composition of the final wave of the attack. Defaults to an empty list.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command(
                "cra",
                {
                    "SX": sx,
                    "SY": sy,
                    "TX": tx,
                    "TY": ty,
                    "KID": kingdom,
                    "LID": lord_id,
                    "WT": 0,
                    "HBW": horses_type,
                    "BPC": 0,
                    "ATT": 0,
                    "AV": 0,
                    "LP": 0,
                    "FC": 0,
                    "PTT": feathers,
                    "SD": slowdown,
                    "ICA": 0,
                    "CD": 99,
                    "A": army,
                    "BKS": boosters,
                    "AST": support_tools,
                    "RW": final_wave,
                    "ASCT": 0,
                },
            )
            if sync:
                response = self.wait_for_json_response("cra")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def get_presets(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Get the attack presets.

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
            self.send_json_command("gas", {})
            if sync:
                response = self.wait_for_json_response("gas")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def time_skip_npc_cooldown(self, kingdom: int, tx: int, ty: int, time_skip: str, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Skip the cooldown for the next attack using a time skip.

        Args:
            kingdom (int): The ID of the kingdom.
            tx (int): The x-coordinate of the target.
            ty (int): The y-coordinate of the target.
            time_skip (str): The type of time skip to use.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_json_command("msd", {"KID": kingdom, "X": tx, "Y": ty, "MID": -1, "NID": -1, "MST": time_skip})
            if sync:
                response = self.wait_for_json_response("msd")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def paid_skip_npc_cooldown(self, kingdom: int, tx: int, ty: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Skip the cooldown for the next attack using rubies.

        Args:
            kingdom (int): The ID of the kingdom.
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
            self.send_json_command("sdc", {"KID": kingdom, "X": tx, "Y": ty, "MID": -1, "NID": -1})
            if sync:
                response = self.wait_for_json_response("sdc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
