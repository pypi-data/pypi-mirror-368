"""
Module for handling system-level operations in Goodgame Empire.

This module defines the `System` class, which provides methods for version checking, 
server login, auto-joining, round trips, pinging, and maintaining socket connectivity.
"""

from ..base_gge_socket import BaseGgeSocket

class System(BaseGgeSocket):
    """
    A class for handling system-level operations in Goodgame Empire.

    This class provides methods for checking the game version, logging into the server, 
    automatically joining a session, maintaining connections, and sending system-level commands.
    """

    def ver_check(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Perform a version check.

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
            self.send_xml_message("sys", "verChk", "0", "<ver v='166' />")
            if sync:
                response = self.wait_for_xml_response("sys", "apiOK", "0")
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def join_server(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Join the game server.

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
            self.send_xml_message("sys", "login", "0", 
                f"<login z='{self.server_header}'><nick><![CDATA[]]></nick><pword><![CDATA[1123010%fr%0]]></pword></login>")
            if sync:
                response = self.wait_for_json_response("nfo")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def auto_join(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Automatically join a server session.

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
            self.send_xml_message("sys", "autoJoin", "-1", "")
            if sync:
                response = self.wait_for_xml_response("sys", "joinOK", "1")
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def round_trip(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Perform a round trip request.

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
            self.send_xml_message("sys", "roundTrip", "1", "")
            if sync:
                response = self.wait_for_xml_response("sys", "roundTripRes", "1")
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def vck(self, build_number: int, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Perform a version check for a specific build number.

        Args:
            build_number (str): The build number to check.
            sync (bool, optional): If True, waits for a response and returns it. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_raw_command("vck", [build_number, "web-html5", "<RoundHouseKick>"])
            if sync:
                response = self.wait_for_json_response("vck")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def ping(self, quiet: bool = False) -> bool:
        """
        Send a ping to keep the connection alive.

        Args:
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            bool: True if the operation was successful, False if it failed and `quiet` is True.

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        try:
            self.send_raw_command("pin", ["<RoundHouseKick>"])
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def init_socket(self, sync: bool = True, quiet: bool = False) -> dict | bool:
        """
        Initialize the socket connection and join the server.

        Args:
            sync (bool, optional): If True, waits for responses. Defaults to True.
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.
        
        Returns:
            None

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        self.opened.wait()
        self.ver_check(sync=sync, quiet=quiet)
        self.join_server(sync=sync, quiet=quiet)
        self.auto_join(sync=sync, quiet=quiet)
        self.round_trip(sync=sync, quiet=quiet)

    def keep_alive(self, quiet: bool = False) -> bool:
        """
        Maintain the connection by sending periodic ping messages.

        Args:
            quiet (bool, optional): If True, suppresses exceptions and returns False on failure. Defaults to False.

        Returns:
            None

        Raises:
            Exception: If an error occurs and `quiet` is False.
        """
        self.opened.wait()
        while self.opened.is_set():
            closed = self.closed.wait(60)
            if not closed:
                self.ping(quiet=quiet)
