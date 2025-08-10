"""
Module for handling espionage operations in Goodgame Empire.

This module defines the `Spy` class, which provides a method to send spies for reconnaissance 
with various options including spy count, precision, and movement modifiers.
"""

from ..base_gge_socket import BaseGgeSocket


class Spy(BaseGgeSocket):
    """
    A class for handling espionage operations in Goodgame Empire.

    This class provides a method to send spies to a target location with adjustable
    parameters such as spy count, precision, and movement speed modifications.
    """

    def send_spy(
        self,
        kingdom: int,
        source_id: int,
        tx: int,
        ty: int,
        spy_count: int = 1,
        precision: int = 50,
        spy_type: int = 0,
        horses_type: int = -1,
        feathers: int = 0,
        slowdown: int = 0,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Send spies to a target location for reconnaissance.

        Args:
            kingdom (int): The ID of the kingdom where the spying occurs.
            source_id (int): The ID of the source from which spies are sent.
            tx (int): The x-coordinate of the target.
            ty (int): The y-coordinate of the target.
            spy_count (int, optional): The number of spies to send. Defaults to 1.
            precision (int, optional): The precision level of the spies (0-100). Defaults to 50.
            spy_type (int, optional): The type of spying operation (0 = standard). Defaults to 0.
            horses_type (int, optional): The type of horses used (-1 for default). Defaults to -1.
            feathers (int, optional): Whether to use feathers to speed up the spies. Defaults to 0.
            slowdown (int, optional): The amount of slowdown applied to the spies. Defaults to 0.
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
                "csm",
                {
                    "SID": source_id,
                    "TX": tx,
                    "TY": ty,
                    "SC": spy_count,
                    "ST": spy_type,
                    "SE": precision,
                    "HBW": horses_type,
                    "KID": kingdom,
                    "PTT": feathers,
                    "SD": slowdown,
                },
            )
            if sync:
                response = self.wait_for_json_response("csm")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
