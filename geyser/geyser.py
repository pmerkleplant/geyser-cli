from typing import Optional, List
from decimal import Decimal

from web3 import Web3
from web3.types import ChecksumAddress

from .status import Status
from .constants import TOKEN_ADDRESSES, GEYSER_ADDRESSES
from .utils import (
    _load_contract,
    _load_contract_erc20,
)


class Geyser:
    """
    Wrapper for the Geyser contracts.
    """

    def __init__(
        self,
        web3: Web3
    ) -> None:
        """
        :param web3: Web3 instance
        """
        if web3:
            self.w3 = web3
        else:
            raise ValueError("No web3 instance given")

        self.__init_contracts()

    def get_summary(self, address: ChecksumAddress) -> List[Status]:
        result = [
            self.get_status_for("old_faithful", address),
            self.get_status_for("trinity", address),
            self.get_status_for("beehive", address),
            self.get_status_for("pescadero", address)
        ]

        return list(filter(None, result))

    def get_status_for(self,
                       geyser_name: str,
                       address: ChecksumAddress) -> Optional[Status]:
        """
        :param address: Wallet address
        :param geyser_name: Name of the Geyser instance
        """
        if geyser_name.lower() == "beehive":
            return self.__get_status_beehive(address)
        elif geyser_name.lower() == "pescadero":
            return self.__get_status_pescadero(address)
        elif geyser_name.lower() == "old_faithful":
            return self.__get_status_old_faithful(address)
        elif geyser_name.lower() == "trinity":
            return self.__get_status_trinity(address)
        else:
            return None

    def __get_status_old_faithful(self, address: ChecksumAddress) -> Optional[Status]:
        """
        Old Faithful uses a Balancer v1 Smart Pool with AMPL/USDC.
        The ratio changes every 24 hours.

        The calculations are based on balancer-core, BPool.sol, exitPool().

        :param address: Wallet address
        """
        geyser = self.contracts["old_faithful"]["geyser"]
        pool = self.contracts["old_faithful"]["pool"]
        pool_token = self.contracts["old_faithful"]["token"]
        ampl = self.contracts["tokens"]["ampl"]
        usdc = self.contracts["tokens"]["usdc"]

        staked = geyser.functions.totalStakedFor(address).call()
        if staked == 0:
            return None

        token_total_supply = pool_token.functions.totalSupply().call()

        # Balancer variables
        EXIT_FEE = pool.functions.EXIT_FEE().call()
        BONE = pool.functions.BONE().call()

        # Calculate the pool exit fee
        # See balancer-core, BNum.sol, bmul()
        c0 = EXIT_FEE * staked
        c1 = c0 + (BONE / 2)
        c2 = c1 / BONE

        pool_exit_fee = c2
        staked_after_fees = staked - pool_exit_fee

        # Calculate the ratio
        # See balancer-core, BNum.sol, bdiv()
        c0 = staked_after_fees * BONE
        c1 = c0 + (token_total_supply / 2)
        c2 = c1 / token_total_supply

        ratio = c2

        # Get the balance of each token in pool
        balance_pool_ampl = ampl.functions.balanceOf(pool.address).call()
        balance_pool_usdc = usdc.functions.balanceOf(pool.address).call()

        # Calculate user's balances
        balance_user_ampl = balance_pool_ampl * ratio
        balance_user_usdc = balance_pool_usdc * ratio

        # TODO: Calc Geyser interest
        interest = Decimal(0)

        return Status("Old Faithful", interest, [("AMPL", balance_user_ampl),
                                                 ("USDC", balance_user_usdc)])

    def __get_status_trinity(self, address: ChecksumAddress) -> Optional[Status]:
        """
        Trinity uses a Balancer v1 pool with WBTC/WETH/AMPL.

        The calculations are based on balancer-core, BPool.sol, exitPool().

        :param address: Wallet address
        """
        geyser = self.contracts["trinity"]["geyser"]
        pool = self.contracts["trinity"]["pool"]
        ampl = self.contracts["tokens"]["ampl"]
        weth = self.contracts["tokens"]["weth"]
        wbtc = self.contracts["tokens"]["wbtc"]

        staked = geyser.functions.totalStakedFor(address).call()
        if staked == 0:
            return None

        pool_total_supply = pool.functions.totalSupply().call()

        # Balancer variables
        EXIT_FEE = pool.functions.EXIT_FEE().call()
        BONE = pool.functions.BONE().call()

        # Calculate the pool exit fee
        # See balancer-core, BNum.sol, bmul()
        c0 = EXIT_FEE * staked
        c1 = c0 + (BONE / 2)
        c2 = c1 / BONE

        pool_exit_fee = c2
        staked_after_fees = staked - pool_exit_fee

        # Calculate the ratio
        # See balancer-core, BNum.sol, bdiv()
        c0 = staked_after_fees * BONE
        c1 = c0 + (pool_total_supply / 2)
        c2 = c1 / pool_total_supply

        ratio = c2

        # Get balance of each token in pool
        balance_pool_ampl = ampl.functions.balanceOf(pool.address).call()
        balance_pool_weth = weth.functions.balanceOf(pool.address).call()
        balance_pool_wbtc = wbtc.functions.balanceOf(pool.address).call()

        # Calculate user's balances
        balance_user_ampl = balance_pool_ampl * ratio
        balance_user_weth = balance_pool_weth * ratio
        balance_user_wbtc = balance_pool_wbtc * ratio

        # TODO: Calc Geyser interest
        interest = Decimal(0)

        return Status("Trinity", interest, [("AMPL", balance_user_ampl),
                                            ("WETH", balance_user_weth),
                                            ("WBTC", balance_user_wbtc)])

    def __get_status_pescadero(self, address: ChecksumAddress) -> Optional[Status]:
        """
        Pescadero uses a SushiSwap pool with AMPL/WETH.
        Calculations are based on the Uniswap v2 code, see
        https://github.com/Uniswap/uniswap-v2-core/blob/master/contracts/UniswapV2Pair.sol#L134

        :param address: Wallet address
        """
        geyser = self.contracts["pescadero"]["geyser"]
        pool = self.contracts["pescadero"]["pool"]
        weth = self.contracts["tokens"]["weth"]
        ampl = self.contracts["tokens"]["ampl"]

        staked = geyser.functions.totalStakedFor(address).call()
        if staked == 0:
            return None

        pool_total_supply = pool.functions.totalSupply().call()

        # Get balance of each token in pool
        balance_pool_weth = weth.functions.balanceOf(pool.address).call()
        balance_pool_ampl = ampl.functions.balanceOf(pool.address).call()

        # Calc user's balances
        balance_user_weth = (staked * balance_pool_weth) / pool_total_supply
        balance_user_ampl = (staked * balance_pool_ampl) / pool_total_supply

        # TODO: Get interest earned
        interest = Decimal(0)

        return Status("Pescadero", interest, [("AMPL", balance_user_ampl),
                                              ("WETH", balance_user_weth)])

    def __get_status_beehive(self, address: ChecksumAddress) -> Optional[Status]:
        """
        Beehive uses an Uniswap v2 pool with AMPL/WETH.
        Calculations are based on their code, see
        https://github.com/Uniswap/uniswap-v2-core/blob/master/contracts/UniswapV2Pair.sol#L134

        :param address: Wallet address
        """
        geyser = self.contracts["beehive"]["geyser"]
        pool = self.contracts["beehive"]["pool"]
        weth = self.contracts["tokens"]["weth"]
        ampl = self.contracts["tokens"]["ampl"]

        staked = geyser.functions.totalStakedFor(address).call()
        if staked == 0:
            return None

        pool_total_supply = pool.functions.totalSupply().call()

        # Get balance of each token in pool
        balance_pool_weth = weth.functions.balanceOf(pool.address).call()
        balance_pool_ampl = ampl.functions.balanceOf(pool.address).call()

        # Calc user's balances
        balance_user_weth = (staked * balance_pool_weth) / pool_total_supply
        balance_user_ampl = (staked * balance_pool_ampl) / pool_total_supply

        # TODO: Get interest earned
        interest = Decimal(0)

        return Status("Beehive", interest, [("AMPL", balance_user_ampl),
                                            ("WETH", balance_user_weth)])

    def __init_contracts(self):
        self.contracts = {
            # ERC-20 tokens
            "tokens": {
                "ampl": _load_contract_erc20(self.w3, TOKEN_ADDRESSES["ampl"]),
                "weth": _load_contract_erc20(self.w3, TOKEN_ADDRESSES["weth"]),
                "usdc": _load_contract_erc20(self.w3, TOKEN_ADDRESSES["usdc"]),
                "wbtc": _load_contract_erc20(self.w3, TOKEN_ADDRESSES["wbtc"])
            },
            # Uniswap-like Geysers
            "beehive": {
                "geyser": _load_contract(self.w3,
                                         "geyser",
                                         GEYSER_ADDRESSES["beehive"]["geyser"]),
                "pool": _load_contract(self.w3,
                                       "unipool",
                                       GEYSER_ADDRESSES["beehive"]["pool"])
            },
            "pescadero": {
                "geyser": _load_contract(self.w3,
                                         "geyser",
                                         GEYSER_ADDRESSES["pescadero"]["geyser"]),
                "pool": _load_contract(self.w3,
                                       "unipool",
                                       GEYSER_ADDRESSES["pescadero"]["pool"])
            },
            # Balancer Geysers
            "old_faithful": {
                "geyser": _load_contract(self.w3,
                                         "geyser",
                                         GEYSER_ADDRESSES["old_faithful"]["geyser"]),
                "pool": _load_contract(self.w3,
                                       "bpool",
                                       GEYSER_ADDRESSES["old_faithful"]["pool"]),
                "token": _load_contract_erc20(self.w3,
                                              GEYSER_ADDRESSES["old_faithful"]["token"])
            },
            "trinity": {
                "geyser": _load_contract(self.w3,
                                         "geyser",
                                         GEYSER_ADDRESSES["trinity"]["geyser"]),
                "pool": _load_contract(self.w3,
                                       "bpool",
                                       GEYSER_ADDRESSES["trinity"]["pool"])
            }
        }
