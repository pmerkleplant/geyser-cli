import os
from decimal import Decimal
from typing import (
    List,
    Dict
)

import click
from web3 import Web3
from tabulate import tabulate

from .vault import (
    get_vaults,
    get_vault_content
)
from .types import (
    Token,
    Balance,
    TokenBalance,
    LockedTokenBalance,
    ClaimedTokenBalance,
    VaultId,
    VaultContent,
    LPPosition,
    ENSName,
    ENSAddress,
    GeyserInstance
)
from .utils import (
    resolve_address,
    format_token_amount,
    get_token_symbol,
    send_subgraph_query,
    load_abi,
    load_contract,
    load_contract_erc20
)
from .dexs import (
    dex,
    balancer,
    uni_like
)

### Constants ###

TOKEN_ADDRESSES = {
    "ampl": Web3.toChecksumAddress("0xD46bA6D942050d489DBd938a2C909A5d5039A161"),
    "usdc": Web3.toChecksumAddress("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
    "wbtc": Web3.toChecksumAddress("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"),
    "weth": Web3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
}

DEX_ADDRESSES: Dict[GeyserInstance, Dict[str, Token]] = {
    GeyserInstance.BEEHIVE: {
        "geyser": Web3.toChecksumAddress("0x075Bb66A472AB2BBB8c215629C77E8ee128CC2Fc"),
        "pool": Web3.toChecksumAddress("0xc5be99a02c6857f9eac67bbce58df5572498f40c"),
        "token": Web3.toChecksumAddress("0xc5be99a02c6857f9eac67bbce58df5572498f40c")
    },
    GeyserInstance.PESCADERO: {
        "geyser": Web3.toChecksumAddress("0XC88BA3885995CE2714C14816A69A09880E1E518C"),
        "pool": Web3.toChecksumAddress("0xcb2286d9471cc185281c4f763d34a962ed212962"),
        "token": Web3.toChecksumAddress("0xcb2286d9471cc185281c4f763d34a962ed212962")
    },
    GeyserInstance.OLD_FAITHFUL: {
        "geyser": Web3.toChecksumAddress("0x42d3c21DF4a26C06d7084f6319aCBF9195a583C1"),
        "pool": Web3.toChecksumAddress("0x7860e28ebfb8ae052bfe279c07ac5d94c9cd2937"),
        "token": Web3.toChecksumAddress("0x49F2befF98cE62999792Ec98D0eE4Ad790E7786F")
    },
    GeyserInstance.TRINITY: {
        "geyser": Web3.toChecksumAddress("0xcF98862a8eC1271c9019D47715565a0Bf3a761B8"),
        "pool": Web3.toChecksumAddress("0xa751a143f8fe0a108800bfb915585e4255c2fe80"),
        "token": Web3.toChecksumAddress("0xa751a143f8fe0a108800bfb915585e4255c2fe80")
    },
}


### Commands ###

@click.group()
@click.pass_context
def main(ctx: click.Context):
    ctx.ensure_object(dict)

    # Setup web3 instance
    try:
        provider: str = os.environ["PROVIDER"]
    except KeyError:
        click.secho("Please set the $PROVIDER environment variable",
                    fg="red", bold=True)
        ctx.exit(-1)

    w3 = Web3(
        Web3.HTTPProvider(provider, request_kwargs={'timeout': 60})
    )

    # Initialize global modules
    contracts = init_contracts(w3)

    # Add w3 and global modules to click context object
    ctx.obj['w3'] = w3
    ctx.obj['contracts'] = contracts


@main.command()
@click.argument('addresses', nargs=-1)
@click.pass_context
def positions(ctx: click.Context, addresses: str) -> None:
    """
    Get the user's LP positions held in their vault(s)
    """
    output = cmd_positions(ctx, addresses)
    output_str = format_for_stdout(output)
    click.echo(output_str)


@main.command()
@click.argument('addresses', nargs=-1)
@click.pass_context
def claimed(ctx: click.Context, addresses: str) -> None:
    """
    Get the already claimed tokens from the user's vault(s)
    """
    output = cmd_claimed(ctx, addresses)
    output_str = format_for_stdout(output)
    click.echo(output_str)


@main.command()
@click.argument('addresses', nargs=-1)
@click.pass_context
def locked(ctx: click.Context, addresses: str) -> None:
    """
    Get the tokens locked in the user's vault(s)
    """
    output = cmd_locked(ctx, addresses)
    output_str = format_for_stdout(output)
    click.echo(output_str)


@main.command()
@click.argument("addresses", nargs=-1)
@click.pass_context
def status(ctx: click.Context, addresses: str) -> None:
    """
    Get the status of the user's vault(s)
    """
    # Call single cmd's
    positions = cmd_positions(ctx, addresses)
    locked = cmd_locked(ctx, addresses)
    claimed = cmd_claimed(ctx, addresses)

    # Merge cmd results 
    output: List[dict] = positions
    list_to_merge = [(locked, 'locked'), (claimed, 'claimed')]
    for (to_merge, index) in list_to_merge:
        for user_dict in to_merge:
            user = user_dict['user']

            # Find the same user_dict in output and get the index
            res = None
            for elem in output:
                if elem['user'] == user:
                    res = elem
                    break
            index_user = output.index(res)

            for vault in user_dict['vaults']:
                vault_id = vault['id']

                # Find the same vault_id for user in output and get the index
                res = None
                for elem in output[index_user]['vaults']:
                    if elem['id'] == vault_id:
                        res = elem
                        break
                index_vault = output[index_user]['vaults'].index(res)

                output[index_user]['vaults'][index_vault].update({
                    index: vault[index]
                })

    # Print formatted output
    output_str = format_for_stdout(output)
    click.echo(output_str)


### Command functions ###

def cmd_positions(ctx: click.Context, addresses: str) -> List[dict]:
    output: List[dict] = []

    # Get global modules
    w3 = ctx.obj['w3']
    contracts = ctx.obj['contracts']

    # Resolve addresses
    users: List[ENSAddress] = [resolve_address(w3, addr)
                               for addr in addresses]

    for user in users:
        output.append({
            'user': user,
            'vaults': []
        })

        (ens_name, account) = user

        vaults = get_vaults(account)
        if not vaults:
            continue

        contents: List[Tuple[Vault, VaultContent]] = list(filter(None, [
            (vault, get_vault_content(vault))
            for vault in vaults
        ]))

        locked: List[Tuple[Vault, TokenBalance]] = [
            (vault, l)
            for (vault, (claimed, l)) in contents
        ]

        vault_included = False
        vaults_len = 0
        for (vault, locked) in locked:
            if not vault_included:
                output[len(output) -1]['vaults'].append({
                    'id': vault
                })
                vault_included = True

            geyser_dict = {
                GeyserInstance.BEEHIVE: [],
                GeyserInstance.PESCADERO: [],
                GeyserInstance.OLD_FAITHFUL: [],
                GeyserInstance.TRINITY: []
            }
            for (token, balance) in locked:
                for instance in GeyserInstance:
                    if contracts[instance]['token'].address == token:

                        # Initialize Dex instance
                        dex: dex.Dex = None
                        if instance in [GeyserInstance.TRINITY, GeyserInstance.OLD_FAITHFUL]:
                            dex = balancer.Balancer()
                        else:
                            dex = uni_like.UniLike()

                        # Get the token contracts for this Geyser instance
                        dex_tokens = [
                            contracts['tokens'][token]
                            for token in contracts[instance]['tokens']
                        ]

                        # Get LP position
                        lp_position: LPPosition = dex.get_current_lp_position(
                                                    balance,
                                                    contracts[instance]['pool'],
                                                    contracts[instance]['token'],
                                                    dex_tokens
                                                  )

                        table = []
                        for (token, ticker, balance) in lp_position:
                            formatted_balance = format_token_amount(
                                w3,
                                token,
                                balance
                            )

                            # NOTE: The balances returned from a Balancer pool need to be
                            # converted again to ether.
                            if isinstance(dex, balancer.Balancer):
                                formatted_balance = Web3.fromWei(formatted_balance, "ether")

                            table.append({'token': ticker, 'balance': formatted_balance})
                        
                        geyser_dict[instance] = table
                
            output[len(output) -1]['vaults'][vaults_len].update({
                'lp_positions': geyser_dict
            })
            vaults_len += 1
                        
    return output


def cmd_claimed(ctx: click.Context, addresses: str) -> List[dict]:
    output: List[dict] = []

    # Get global modules
    w3 = ctx.obj['w3']
    contracts = ctx.obj['contracts']

    # Resolve addresses
    users: List[ENSAddress] = [resolve_address(w3, addr)
                               for addr in addresses]

    for user in users:
        output.append({
            'user': user,
            'vaults': []
        })

        (ens_name, account) = user

        vaults = get_vaults(account)
        if not vaults:
            continue

        contents: List[Tuple[Vault, VaultContent]] = list(filter(None, [
            (vault, get_vault_content(vault))
            for vault in vaults
        ]))

        claimed: List[Tuple[Vault, TokenBalance]] = [
            (vault, c)
            for (vault, (c, locked)) in contents
        ]

        vault_included = False
        vaults_len = 0
        for (vault, claimed) in claimed:
            if not vault_included: 
                output[len(output) -1]['vaults'].append({
                    'id': vault
                })
                vault_included = True

            table = []
            for (token, balance) in claimed:
                symbol = get_token_symbol(w3, token)
                formatted_balance = format_token_amount(w3, token, balance)
                table.append({'token': symbol, 'balance': formatted_balance})

            output[len(output) -1]['vaults'][vaults_len].update({
                'claimed': table
            })

            vaults_len += 1
    
    return output


def cmd_locked(ctx: click.Context, addresses: str) -> List[dict]:
    output: List[dict] = []

    # Get global modules
    w3 = ctx.obj['w3']
    contracts = ctx.obj['contracts']

    # Resolve addresses
    users: List[ENSAddress] = [resolve_address(w3, addr)
                               for addr in addresses]

    for user in users:
        output.append({
            'user': user,
            'vaults': []
        })

        (ens_name, account) = user

        vaults = get_vaults(account)
        if not vaults:
            continue

        contents: List[Tuple[Vault, VaultContent]] = list(filter(None, [
            (vault, get_vault_content(vault))
            for vault in vaults
        ]))

        locked: List[Tuple[Vault, TokenBalance]] = [
            (vault, l)
            for (vault, (claimed, l)) in contents
        ]

        vault_included = False
        vaults_len = 0
        for (vault, locked) in locked:
            if not vault_included: 
                output[len(output) -1]['vaults'].append({
                    'id': vault
                })
                vault_included = True

            table = []
            for (token, balance) in locked:
                symbol = get_token_symbol(w3, token)
                formatted_balance = format_token_amount(w3, token, balance)
                table.append({'token': symbol, 'balance': formatted_balance})

            output[len(output) -1]['vaults'][vaults_len].update({
                'locked': table
            })

            vaults_len += 1

    return output


### Helper functions ###

def format_for_stdout(to_format: List[dict]) -> str:
    """
    Returns a styled string to print to stdout.

    The input list must look like this:
    [
        {
            user: ENSAddress,
            vaults: [ 
                { 
                    id: VaultId,
                    locked: [
                        {
                            token: Ticker,
                            balance: Balance
                        }
                    ],
                    claimed: [
                        { 
                            token: Ticker,
                            balance: Balance
                        }
                    ],
                    lp_positions: {
                        GeyserInstance.Pescadero: [
                            {token: Ticker, balance: Balance}
                        ],
                        ...
                    }
                }
            ]
        }
    ]

    :param to_format: List of dicts with user's vault informations
    :return:          Styled string to print to stdout
    """
    output: str = ''

    for user_info in to_format:
        (ens_name, account) = user_info['user']
        output_name = click.style(f'{ens_name if ens_name else account}',
                                  underline=True, bold=True)
        output = click.style(f'{output}{output_name}\n\n')

        vaults = user_info['vaults']
        if not vaults:
            output = click.style(f'{output}No vault(s) found...\n\n')
            continue

        for vault in vaults:
            vault_id = vault['id']
            vault_id_styled = click.style(f'{vault_id}', fg='blue')
            output = click.style(f'{output}Vault {vault_id_styled}:\n\n')

            # Locked tokens in vault
            locked = vault.get('locked')
            if locked:
                output = click.style(f'{output}Locked tokens:\n\n')
                table = [
                    [token_balance['token'], f"{token_balance['balance']: .5f}"]
                    for token_balance in locked
                ]

                table_styled = tabulate(table, headers=['Ticker', 'Balance'])
                output = click.style(f'{output}{table_styled}\n\n')

            # Already claimed tokens by vault
            claimed = vault.get('claimed')
            if claimed:
                output = click.style(f'{output}Claimed tokens:\n\n')
                table = [
                    [token_balance['token'], f"{token_balance['balance']: .5f}"]
                    for token_balance in claimed
                ]

                table_styled = tabulate(table, headers=['Ticker', 'Balance'])
                output = click.style(f'{output}{table_styled}\n\n')

            # LP positions held in vault
            lp_positions = vault.get('lp_positions')
            if lp_positions:
                for geyser_instance, position in lp_positions.items():
                    if not position:
                        continue

                    geyser_instance_str = click.style(f'{geyser_instance.value}', 
                                                      italic=True, underline=True)
                    output = click.style(f'{output}In Geyser {geyser_instance_str}:\n\n')
                    table = [
                        [token_balance['token'], f"{token_balance['balance']: .5f}"]
                        for token_balance in position
                    ]

                    table_styled = tabulate(table, headers=['Ticker', 'Balance'])
                    output = click.style(f'{output}{table_styled}\n\n')

    return output


def init_contracts(w3: Web3) -> dict:
    """
    Returns a dict of initialized contracts.

    :param w3: Web3 instance
    :return:   Dict of contracts
    """
    return {
        'tokens': {
            'ampl': load_contract_erc20(w3, TOKEN_ADDRESSES['ampl']),
            'weth': load_contract_erc20(w3, TOKEN_ADDRESSES['weth']),
            'usdc': load_contract_erc20(w3, TOKEN_ADDRESSES['usdc']),
            'wbtc': load_contract_erc20(w3, TOKEN_ADDRESSES['wbtc'])
        },
        GeyserInstance.BEEHIVE: {
            'pool': load_contract(w3, 'unipool', DEX_ADDRESSES[GeyserInstance.BEEHIVE]['pool']),
            'token': load_contract_erc20(w3, DEX_ADDRESSES[GeyserInstance.BEEHIVE]['token']),
            'tokens': ['ampl', 'weth']
        },
        GeyserInstance.PESCADERO: {
            'pool': load_contract(w3, 'unipool', DEX_ADDRESSES[GeyserInstance.PESCADERO]['pool']),
            'token': load_contract_erc20(w3, DEX_ADDRESSES[GeyserInstance.PESCADERO]['token']),
            'tokens': ['ampl', 'weth']
        },
        GeyserInstance.OLD_FAITHFUL: {
            'pool': load_contract(w3, 'bpool', DEX_ADDRESSES[GeyserInstance.OLD_FAITHFUL]['pool']),
            'token': load_contract_erc20(w3, DEX_ADDRESSES[GeyserInstance.OLD_FAITHFUL]['token']),
            'tokens': ['ampl', 'usdc']
        },
        GeyserInstance.TRINITY: {
            'pool': load_contract(w3, 'bpool', DEX_ADDRESSES[GeyserInstance.TRINITY]['pool']),
            'token': load_contract_erc20(w3, DEX_ADDRESSES[GeyserInstance.TRINITY]['token']),
            'tokens': ['ampl', 'weth', 'wbtc']
        },
    }
