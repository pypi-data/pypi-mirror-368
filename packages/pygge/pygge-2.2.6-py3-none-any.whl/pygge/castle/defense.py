"""
This module contains the class for interacting with the Goodgame Empire API's defense-related functions.

The `Defense` class provides methods for changing the defense of a castle. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Defense(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's defense-related functions.

    This class provides methods for changing the defense of a castle. It is a subclass of `BaseGgeSocket`.
    """

    def get_castle_defense(
        self, x: int, y: int, castle_id: int, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Get the defense of a castle.

        Args:
            x (int): The X-coordinate of the castle.
            y (int): The Y-coordinate of the castle.
            castle_id (int): The ID of the castle.
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
                "dfc", {"CX": x, "CY": y, "AID": castle_id, "KID": -1, "SSV": 0}
            )
            if sync:
                response = self.wait_for_json_response("dfc")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def change_defense_keep(
        self,
        x: int,
        y: int,
        castle_id: int,
        min_units_to_consume_tools: int,
        melee_percentage: int,
        tools: list[list[int]],
        support_tools: list[list[int]],
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Change the defense of a castle's keep.

        Args:
            x (int): The X-coordinate of the castle.
            y (int): The Y-coordinate of the castle.
            castle_id (int): The ID of the castle.
            min_units_to_consume_tools (int): The minimum number of enemy units to consume tools.
            melee_percentage (int): The percentage of melee units.
            tools (list[list[int]]): The tools to use.
            support_tools (list[list[int]]): The support tools to use.
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
                "dfk",
                {
                    "CX": x,
                    "CY": y,
                    "AID": castle_id,
                    "MAUCT": min_units_to_consume_tools,
                    "UC": melee_percentage,
                    "S": tools,
                    "STS": support_tools,
                },
            )
            if sync:
                response = self.wait_for_json_response("dfk")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def change_defense_wall(
        self,
        x: int,
        y: int,
        castle_id: int,
        left_tools: list[list[int]],
        left_unit_percentage: int,
        left_melee_percentage: int,
        middle_tools: list[list[int]],
        middle_unit_percentage: int,
        middle_melee_percentage: int,
        right_tools: list[list[int]],
        right_unit_percentage: int,
        right_melee_percentage: int,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Change the defense of a castle's wall.

        Args:
            x (int): The X-coordinate of the castle.
            y (int): The Y-coordinate of the castle.
            castle_id (int): The ID of the castle.
            left_tools (list[list[int]]): The tools for the left side.
            left_unit_percentage (int): The percentage of units for the left side.
            left_melee_percentage (int): The percentage of melee units for the left side.
            middle_tools (list[list[int]]): The tools for the middle.
            middle_unit_percentage (int): The percentage of units for the middle.
            middle_melee_percentage (int): The percentage of melee units for the middle.
            right_tools (list[list[int]]): The tools for the right side.
            right_unit_percentage (int): The percentage of units for the right side.
            right_melee_percentage (int): The percentage of melee units for the right side.
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
                "dfw",
                {
                    "CX": x,
                    "CY": y,
                    "AID": castle_id,
                    "L": {
                        "S": left_tools,
                        "UP": left_unit_percentage,
                        "UC": left_melee_percentage,
                    },
                    "M": {
                        "S": middle_tools,
                        "UP": middle_unit_percentage,
                        "UC": middle_melee_percentage,
                    },
                    "R": {
                        "S": right_tools,
                        "UP": right_unit_percentage,
                        "UC": right_melee_percentage,
                    },
                },
            )
            if sync:
                response = self.wait_for_json_response("dfw")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def change_defense_moat(
        self,
        x: int,
        y: int,
        castle_id: int,
        left_tools: list[list[int]],
        middle_tools: list[list[int]],
        right_tools: list[list[int]],
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Change the defense of a castle's moat.

        Args:
            x (int): The X-coordinate of the castle.
            y (int): The Y-coordinate of the castle.
            castle_id (int): The ID of the castle.
            left_tools (list[list[int]]): The tools for the left side.
            middle_tools (list[list[int]]): The tools for the middle.
            right_tools (list[list[int]]): The tools for the right side.
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
                "dfm",
                {
                    "CX": x,
                    "CY": y,
                    "AID": castle_id,
                    "LS": left_tools,
                    "MS": middle_tools,
                    "RS": right_tools,
                },
            )
            if sync:
                response = self.wait_for_json_response("dfm")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
