"""
This module contains the class for interacting with the Goodgame Empire API's settings-related functions.

The `Settings` class provides methods for changing various settings in the game. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket


class Settings(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's settings-related functions.

    This class provides methods for changing various settings in the game. It is a subclass of `BaseGgeSocket`.
    """

    def show_animations(
        self, show: bool = True, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Show or hide animations in the game.

        Args:
            show (bool, optional): If True, show animations. If False, hide animations. Defaults to True.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("ani", {"ANI": show})
            if sync:
                response = self.wait_for_json_response("ani")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def show_small_attacks(
        self, show: bool = True, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Show or hide small incoming attacks in the game.

        Args:
            show (bool, optional): If True, show small incoming attacks. If False, hide small incoming attacks. Defaults to True.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("mvf", {"FID": 0, "ACT": not show})
            if sync:
                response = self.wait_for_json_response("mvf")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def show_small_attacks_alliance(
        self, show: bool = True, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Show or hide small incoming attacks on alliance members in the game.

        Args:
            show (bool, optional): If True, show small incoming attacks on alliance members. If False, hide small incoming attacks on alliance members. Defaults to True.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("mvf", {"FID": 1, "ACT": not show})
            if sync:
                response = self.wait_for_json_response("mvf")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def show_resource_carts(
        self, show: bool = True, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Show or hide resource carts in the game.

        Args:
            show (bool, optional): If True, show resource carts. If False, hide resource carts. Defaults to True.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("mvf", {"FID": 2, "ACT": not show})
            if sync:
                response = self.wait_for_json_response("mvf")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def set_misc_settings(
        self,
        show_vip_banners: int = 1,
        offline_for_friends: int = 0,
        ruby_purchase_confirmation_thr: int = -1,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Set miscellaneous settings in the game.

        Args:
            show_vip_banners (int, optional): Show VIP banners. 1 to show, 0 to hide. Defaults to 1.
            offline_for_friends (int, optional): Appear offline for friends. 1 to appear offline, 0 to appear online. Defaults to 0.
            ruby_purchase_confirmation_thr (int, optional): Ruby purchase confirmation threshold. If set to a positive integer, a confirmation dialog will be shown when using rubies over the threshold. Defaults to -1.
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
                "opt",
                {
                    "SVF": show_vip_banners,
                    "OFF": offline_for_friends,
                    "CC2T": ruby_purchase_confirmation_thr,
                },
            )
            if sync:
                response = self.wait_for_json_response("opt")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def set_hospital_settings(
        self,
        kingdom: int,
        castle_id: int,
        accept_ruby_units: int = -1,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Set hospital settings for a castle.

        Args:
            kingdom (int): The kingdom number where the castle is located.
            castle_id (int): The ID of the castle.
            accept_ruby_units (int, optional): Whether to accept ruby units in the hospital. 1 to accept, 0 to reject, -1 to keep the current setting. Defaults to -1.
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
                "hfl", {"KID": kingdom, "AID": castle_id, "HRF": accept_ruby_units}
            )
            if sync:
                response = self.wait_for_json_response("hfl")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
