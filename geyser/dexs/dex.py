from decimal import Decimal
from typing import List

from web3.eth import Contract

from ..types import LPPosition


class Dex:
    """
    Abstract class implemented by each Dex instance.
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
        raise NotImplementedError("Dex: function get_current_lp_position not implemented")
