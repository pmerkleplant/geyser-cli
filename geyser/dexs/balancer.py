from decimal import Decimal
from typing import List

from web3.eth import Contract

from .dex import Dex
from ..types import LPPosition


class Balancer(Dex):
    """
    Dex class implementing the Balancer dex.
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
        pool_total_supply = pool_token.functions.totalSupply().call()

        # Balancer variables
        EXIT_FEE = pool.functions.EXIT_FEE().call()
        BONE = pool.functions.BONE().call()

        # Calculate the pool exit fee
        # See balancer-core/contracts/BNum.sol::bmul()
        c0 = EXIT_FEE * stake
        c1 = c0 + Decimal(BONE / 2)
        c2 = c1 / BONE

        pool_exit_fee = c2
        staked_after_fees = stake - pool_exit_fee

        # Calculate the ratio
        # See balancer-core/contracts/BNum.sol::bdiv()
        c0 = staked_after_fees * BONE
        c1 = c0 + Decimal(pool_total_supply / 2)
        c2 = Decimal(c1 / pool_total_supply)

        ratio = c2

        position: LPPosition = [
            (
                contract.address,
                contract.functions.symbol().call(),
                contract.functions.balanceOf(pool.address).call() * ratio
            )
            for contract in tokens
        ]

        return position
