from decimal import Decimal

from typing import Tuple, List


class Status:
    """
    Represents the current status of an address in a Geyser instance.
    """

    def __init__(self,
                 geyser_instance: str,
                 interest_earned: Decimal,
                 balances: List[Tuple[str, Decimal]]) -> None:
        """
        :param geyser_instance: Name of the Geyser instance
        :param interest_earned: Unclaimed AMPL interest earned
        :param balances: List of token ticker's and their corresponding
                         balances
        """
        self.geyser_instance = geyser_instance
        self.interest_earned = interest_earned
        self.balances = balances
