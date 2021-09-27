<h1 align=center><code>Geyser-cli</code></h1>

`geyser-cli` is an unofficial command line utility for checking the universal 
vault(s) of a set of addresses participating in Ampleforth's Geyser v2.

## Installation

`pip install geyser-cli`

## Setup

### Ethereum node

`geyser-cli` needs to talk to an Ethereum node. You can either use a local one
or a hosted service.
Anyway, set the node's URL as environment variable `$PROVIDER`.

Example: `$ export PROVIDER=https://mainnet.infura.io/v3/<INFURA-PROJECT-ID>`

## Commands

Checking the available commands with `$ geyser --help` outputs:
```
Usage: geyser [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  claimed    Get the already claimed tokens from the user's vault(s)
  locked     Get the tokens locked in the user's vault(s)
  positions  Get the user's LP positions held in their vault(s)
  status     Get the status of the user's vault(s)
```

The `status` command is the combined output of all other commands.

With it, you can check the current status for each vault held by set of 
addresses.

Example:
```
$ geyser status                            \
gov.merkleplant.eth                        \
0xa308de214e01c365834e3344c1088b0d2b97559c
```

Output:
```
gov.merkleplant.eth

No vault(s) found...

0xa308DE214e01c365834e3344C1088B0D2B97559c

Vault 0xa899bede339275dbd9f2c5a98e915be7f030f26f:

Locked tokens:

Ticker                             Balance
-------------------------------  ---------
ubAAMPL                            0.025
SLP                                0
UNI-V2                             0.00016
BAL-REBASING-SMART-V1-AMPL-USDC   15

Claimed tokens:

Ticker      Balance
--------  ---------
AMPL        7.85485

In Geyser Beehive:

Ticker      Balance
--------  ---------
AMPL      953.419
WETH        0.29912

In Geyser Pescadero:

Ticker      Balance
--------  ---------
AMPL       16.4279
WETH        0.00514

In Geyser Old Faithful:

Ticker      Balance
--------  ---------
AMPL        2.99358
USDC        5.91427
```

_Note that the output contains colors and other stylings not shown above._

## Support

If there are any question, don't hesitate to ask!

You can reach me at pascal [at] merkleplant.xyz or in the official Ampleforth
Discord.

## Contributions

Any kind of contribution is highly welcome!

## Acknowledgment

This project is heavily inspired by [uniswap-python](https://github.com/uniswap-python/uniswap-python).
