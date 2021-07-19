from decimal import Decimal
from typing import Optional

from web3 import Web3

from .utils import _load_contract
from .constants import CHAINLINK_PRICE_FEEDS


class PriceOracle:
    """
    Provides current prices for ERC-20 tokens.
    The prices are fetched from Chainlink's on-chain price feeds.
    """

    def __init__(self, web3: Web3) -> None:
        """
        :param web3: Web3 instance
        """
        if web3:
            self.w3 = web3
        else:
            raise ValueError("No web3 instance given")

        # Initialize contracts
        self.contracts = {
            "ampl": _load_contract(self.w3, "chainlink",
                                   CHAINLINK_PRICE_FEEDS["ampl"]),
            "weth": _load_contract(self.w3, "chainlink",
                                   CHAINLINK_PRICE_FEEDS["weth"]),
            "wbtc": _load_contract(self.w3, "chainlink",
                                   CHAINLINK_PRICE_FEEDS["wbtc"])
        }

        # Fetch prices
        # NOTE: Prices are formatted!
        self.prices = {
            "ampl": self._get_formatted_price_of("ampl"),
            "usdc": Decimal(1),
            "wbtc": self._get_formatted_price_of("wbtc"),
            "weth": self._get_formatted_price_of("weth")
        }

    def _get_formatted_price_of(self, ticker: str) -> Optional[Decimal]:
        """
        :param ticker: Ticker for requested token price
        """
        feed = self.contracts[ticker]
        if not feed:
            return None

        # See https://docs.chain.link/docs/price-feeds-api-reference
        price = Decimal(feed.functions.latestRoundData().call()[1])
        decimals = Decimal(feed.functions.decimals().call())

        return price / (10 ** decimals)
