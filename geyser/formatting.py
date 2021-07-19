from decimal import Decimal

from web3 import Web3


def format_token(ticker: str, balance: Decimal) -> Decimal:
    if ticker == "AMPL":
        return _format_AMPL(balance)
    elif ticker == "WBTC":
        return _format_WBTC(balance)
    elif ticker == "USDC":
        return _format_USDC(balance)
    elif ticker == "WETH":
        return _format_WETH(balance)
    else:
        raise ValueError("Unknown ticker: {}".format(ticker))


def _format_AMPL(balance: Decimal) -> Decimal:
    # NOTE: gwei = 1e9
    return Web3.fromWei(balance, "gwei")


def _format_WBTC(balance: Decimal) -> Decimal:
    decimals = 10 ** 8
    return balance // decimals


def _format_USDC(balance: Decimal) -> Decimal:
    # NOTE: mwei = 1e6
    return Web3.fromWei(balance, "mwei")


def _format_WETH(balance: Decimal) -> Decimal:
    return Web3.fromWei(balance, "ether")
