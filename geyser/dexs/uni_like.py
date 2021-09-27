from decimal import Decimal
from typing import List

from web3.eth import Contract

from .dex import Dex
from ..types import LPPosition


class UniLike(Dex):
    """
    Dex class implementing the Uniswap V2 dex and their forks.
    """

    def get_current_lp_position(
        self,
        stake: Decimal,
        pool: Contract,
        pool_token: Contract,
        tokens: List[Contract]
    ) -> LPPosition:
        """
        Returns the LP position for given stake in pool.

        :param stake:      The stake hold in the pool
        :param pool:       The pool contract
        :param pool_token: The pool's token contract
        :param tokens:     The tokens contained in the pool
        """
        pool_total_supply = pool.functions.totalSupply().call()

        position: LPPosition = []
        for contract in tokens:
            ticker = contract.functions.symbol().call()

            balance_pool = contract.functions.balanceOf(pool.address).call()
            balance_user = (stake * balance_pool) / pool_total_supply

            position.append((contract.address, ticker, balance_user))

        return position
