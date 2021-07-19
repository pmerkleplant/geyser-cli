import os
import json
import functools

from web3 import Web3
from web3.types import ChecksumAddress
from web3.eth import Contract

# Copied from uniswap-python
# https://github.com/uniswap-python/uniswap-python


def _load_abi(name: str) -> str:
    path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/"
    with open(os.path.abspath(path + f"{name}.abi")) as f:
        abi: str = json.load(f)
    return abi


@functools.lru_cache()
def _load_contract(w3: Web3,
                   abi_name: str,
                   address: ChecksumAddress) -> Contract:
    address = Web3.toChecksumAddress(address)
    return w3.eth.contract(address=address, abi=_load_abi(abi_name))


def _load_contract_erc20(w3: Web3, address: ChecksumAddress) -> Contract:
    return _load_contract(w3, "erc20", address)
