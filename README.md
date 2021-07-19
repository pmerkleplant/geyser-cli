<h1 align=center><code>Geyser-cli</code></h1>

Geyser-cli is an unofficial command line utility for checking the LP positions
of a set of addresses participating in Ampleforth's Geyser.

**NOTE: This project is in a very early stage!**

## Installation

The project is not yet downloadable from pip. Therefore there are some commands to
execute before it can be installed.

### Poetry

This project uses [poetry](https://python-poetry.org/) as package managing tool.
To install poetry, run `$ pip install poetry`.

Afterwards execute `$ poetry install` to install the projects dependencies.
Executing `$ poetry build` now builds the wheels archive. This archive will be used
by pip to install geyser-cli locally.

### Pip

Install geyser-cli locally with `$ pip install dist/geyser_cli-0.0.1-py3-none-any.whl`.

## Usage

### Ethereum node

Geyser-cli needs to talk to an Ethereum node. You can either use a local one or a hosted service.
Anyway, set the node's URL as environment variable `$PROVIDER`.

Example: `export PROVIDER=https://mainnet.infura.io/v3/<INFURA-PROJECT-ID`

### Commands

Checking the availale commands with `$ geyser --help` outputs:
```
Usage: geyser [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  status
```

As shown in the output, there is currently only one command supported: `status`.

With the `status` command you can check the current status for a set of
addresses.

Example: `$ geyser status gov.merkleplant.eth 0x6Ad0586E4350Bf0F4199d8A425fc646C485C3943`

Output:
```
Summary for 0x2292d4416A8Ff57619Cfa32Be4AA5a392496b260
  Old Faithful
    AMPL:  212.08345
    USDC:  300.08240

Summary for 0x6Ad0586E4350Bf0F4199d8A425fc646C485C3943
  Trinity
    AMPL:  195.50368
    WETH:  0.09874
    WBTC:  0.00590
```

As shown in the output, geyser-cli will print the current LP-positions for each
active Geyser in which the address is participating.

Also note that ENS resolution is supported.

## TODOs

- [ ] Calculate the interest earned per Geyser
- [ ] Implement a `history` command to see the information about finished
      Geysers

Any kind of contribution is highly welcome!

## Support

If there are any question, don't hesitate to ask!

You can reach me at pascal [at] merkleplant.xyz or in the official Ampleforth
Discord forum.

## Acknowledgment

This project is heavily inspired by [uniswap-python](https://github.com/uniswap-python/uniswap-python).
