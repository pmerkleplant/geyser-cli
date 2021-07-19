import os
import click
from decimal import Decimal
from typing import List, Tuple

from web3 import Web3
from web3.types import (
    ChecksumAddress
)
from tabulate import tabulate

from .geyser import Geyser
from .price_oracle import PriceOracle
from .status import Status
from .formatting import format_token


@click.group()
@click.pass_context
def main(ctx: click.Context):
    ctx.ensure_object(dict)

    # Setup web3 instance
    provider = os.environ["PROVIDER"]
    if not provider:
        raise ValueError("Please set the $PROVIDER environment variable")

    w3 = Web3(
        Web3.HTTPProvider(provider, request_kwargs={"timeout": 60})
    )
    ctx.obj["w3"] = w3

    # Initialize global modules
    ctx.obj["Geyser"] = Geyser(w3)
    ctx.obj["PriceOracle"] = PriceOracle(w3)


@main.command()
@click.argument("addresses", nargs=-1)
@click.pass_context
def status(ctx: click.Context, addresses: str) -> None:
    # Resolve addresses
    # TODO: Save ENS name for better output
    addrs = [_resolve_address_(ctx.obj["w3"], addr)
             for addr in addresses]

    # Get the status of each Geyser for each address
    geyser: Geyser = ctx.obj["Geyser"]
    summaries: List[Tuple[ChecksumAddress, List[Status]]] = [
        (addr, geyser.get_summary(addr)) for addr in addrs
    ]

    # Print the summary for each address
    for (addr, summary) in summaries:
        if not summary:
            continue

        addr_out = click.style(f"{addr}", bold=True)
        click.echo(f"== {addr_out} ==========")
        click.echo()
        [_print_status_of_geyser_instance(status, ctx.obj["PriceOracle"])
         for status in summary]


def _print_status_of_geyser_instance(status: Status, price_oracle: PriceOracle):
    click.secho("" + status.geyser_instance, fg="blue", bold=True)

    table = []
    total_value = Decimal(0)

    for (ticker, balance) in status.balances:
        adjusted_balance = format_token(ticker, balance)

        # NOTE: The balances returned from a Balancer pool need to be
        # converted again to ether.
        if status.geyser_instance in ["Old Faithful", "Trinity"]:
            adjusted_balance = Web3.fromWei(adjusted_balance, "ether")

        # Get $-value of current balance
        value = price_oracle.prices[ticker.lower()] * adjusted_balance
        total_value += value

        table.append(
            [ticker, f"{adjusted_balance: .5f}", value]
        )

    table.append([
        click.style("$$$", bold=True),
        "",
        click.style(f"{total_value: .2f}", bold=True)
    ])
    click.echo(tabulate(table, headers=["Token", "Balance", "Value in $"]))
    click.echo()


def _resolve_address_(w3: Web3.HTTPProvider, addr: str) -> ChecksumAddress:
    """
    Returns the checksum address of given ENS domain or address string.

    :param w3: Web3 instance
    :param addr: The address string to resolve
    """
    if addr.endswith(".eth"):
        resolved = w3.ens.address(addr)
        if resolved is None:
            raise ValueError(
                "Please provide a valid Ethereum address or ENS domain"
            )
        else:
            return resolved
    else:
        if Web3.isAddress(addr):
            return Web3.toChecksumAddress(addr)
        else:
            raise ValueError(
                "Please provide a valid Ethereum address or ENS domain"
            )
