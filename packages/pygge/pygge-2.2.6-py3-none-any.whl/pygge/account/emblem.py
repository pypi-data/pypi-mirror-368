"""
This module contains the class for interacting with the Goodgame Empire API's emblem-related functions.

The `Emblem` class provides methods for changing the emblem of a castle. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Emblem(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's emblem-related functions.

    This class provides methods for changing the emblem of a castle. It is a subclass of `BaseGgeSocket`.
    """

    def change_emblem(
        self,
        bg_type: int,
        bg_color_1: int,
        bg_color_2: int,
        icons_type: int,
        icon_id_1: int,
        icon_color_1: int,
        icon_id_2: int,
        icon_color_2: int,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Change the emblem of a castle.

        Args:
            bg_type (int): The type of background.
            bg_color_1 (int): The first background color. It should be an integer color code.
            bg_color_2 (int): The second background color. It should be an integer color code.
            icons_type (int): The type of icons.
            icon_id_1 (int): The ID of the first icon.
            icon_color_1 (int): The color of the first icon. It should be an integer color code.
            icon_id_2 (int): The ID of the second icon.
            icon_color_2 (int): The color of the second icon. It should be an integer color code.
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
                "cem",
                {
                    "CAE": {
                        "BGT": bg_type,
                        "BGC1": bg_color_1,
                        "BGC2": bg_color_2,
                        "SPT": icons_type,
                        "S1": icon_id_1,
                        "SC1": icon_color_1,
                        "S2": icon_id_2,
                        "SC2": icon_color_2,
                    }
                },
            )
            if sync:
                response = self.wait_for_json_response("cem")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
