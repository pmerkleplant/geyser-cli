import os
import json
import requests
import functools
from decimal import Decimal

from web3 import Web3
from web3.types import ChecksumAddress
from web3.eth import Contract

from .types import ENSAddress


def resolve_address(w3: Web3.HTTPProvider, addr: str) -> ENSAddress:
    """
    Resolves the given address string to an ENSAddress type.

    :param w3:   Web3 instance
    :param addr: The address string to resolve
    :return:     An ENSAddress type
    """
    if addr.endswith(".eth"):
        resolved = w3.ens.address(addr)
        if resolved is None:
            raise ValueError(f"Invalid ENS domain {addr}")
        else:
            return addr, resolved
    else:
        if Web3.isAddress(addr):
            return None, Web3.toChecksumAddress(addr)
        else:
            raise ValueError(f"Invalid Ethereum address {addr}")


def format_token_amount(
    w3: Web3.HTTPProvider, 
    token: ChecksumAddress, 
    amount: Decimal
) -> Decimal:
    """
    Returns the formatted amount of given ERC20 token.

    :param w3:     Web3 instance
    :param token:  The token's contract address
    :param amount: The unformatted amount of tokens
    :return:       Formatted amount of tokens
    """
    contract = load_contract_erc20(w3, token)
    decimals = Decimal(contract.functions.decimals().call())

    return amount / (10 ** decimals)


def get_token_symbol(
    w3: Web3.HTTPProvider,
    token: ChecksumAddress
) -> str:
    """
    Return the tokens symbol/ticker.

    :param w3:    Web3 instance
    :param token: The token's contract address
    :return:      The token's symbol/ticker
    """
    contract = load_contract_erc20(w3, token)
    ticker = contract.functions.symbol().call()

    return ticker


def send_subgraph_query(query: str) -> dict:
    """
    Send given query to Ampleforth's Token Geyser v2 subgraph.

    :param query: The GraphQL query
    :return:      JSON parsed response's payload
    """
    # TODO: Move to constants
    subgraph_host = 'https://api.thegraph.com/subgraphs/name/aalavandhan/amplgeyserv2'

    resp = requests.post(subgraph_host, json={'query': query})
    return json.loads(resp.text)


# Following functions are copied from uniswap-python, see https://github.com/uniswap-python/uniswap-python

def load_abi(name: str) -> str:
    path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/"
    with open(os.path.abspath(path + f"{name}.abi")) as f:
        abi: str = json.load(f)
    return abi


@functools.lru_cache()
def load_contract(
    w3: Web3,
    abi_name: str,
    address: ChecksumAddress
) -> Contract:
    address = Web3.toChecksumAddress(address)
    return w3.eth.contract(address=address, abi=load_abi(abi_name))


def load_contract_erc20(w3: Web3, address: ChecksumAddress) -> Contract:
    return load_contract(w3, "erc20", address)
