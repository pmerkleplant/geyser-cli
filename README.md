<h1 align=center><code>Geyser-cli</code></h1>

`geyser-cli` is an unofficial command line utility for checking the LP positions
as well as the current value, denominated in USD, of a set of addresses
participating in Ampleforth's Geyser.

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
  status
```

As shown in the output, there is currently only one command supported: `status`.

With the `status` command you can check the current status for a set of
addresses.

Example:
```
$ geyser status                            \
gov.merkleplant.eth                        \
0x6ad0586e4350bf0f4199d8a425fc646c485c3943 \
0xaE6dCd07fac9D7CccC98509120c1071048cDD8a1 \
0x31d6E97282e76450f04E91c13bfc47F1Fb27B0B6
```

Output:
```
== gov.merkleplant.eth ==========

Old Faithful
Token    Balance      Value in $
-------  ---------  ------------
AMPL     211.54216       199.542
USDC     295.20488       295.205
$$$                      494.75

== 0x6Ad0586E4350Bf0F4199d8A425fc646C485C3943 ==========

Trinity
Token    Balance      Value in $
-------  ---------  ------------
AMPL     193.64992       182.664
WETH     0.09840         178.163
WBTC     0.00582         178.294
$$$                      539.12

== 0xaE6dCd07fac9D7CccC98509120c1071048cDD8a1 ==========

Beehive
Token    Balance       Value in $
-------  ----------  ------------
AMPL     2005.61831       1891.84
WETH     1.01921          1845.33
$$$                       3737.17

== 0x31d6E97282e76450f04E91c13bfc47F1Fb27B0B6 ==========

Pescadero
Token    Balance        Value in $
-------  -----------  ------------
AMPL     15826.63873       14928.8
WETH     8.04035           14557.4
$$$                        29486.2
```

As shown in the example, `geyser-cli` will print the current LP-positions for
each active Geyser in which the address is participating as well as the current
USD denominated value.
The current value is fetched from Chainlink's on-chain price feeds.

Addresses which do not participate in a current Geyser will not be printed.

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
