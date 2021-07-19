from web3 import Web3

TOKEN_ADDRESSES = {
    "ampl": Web3.toChecksumAddress("0xD46bA6D942050d489DBd938a2C909A5d5039A161"),
    "usdc": Web3.toChecksumAddress("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
    "wbtc": Web3.toChecksumAddress("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"),
    "weth": Web3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
}

GEYSER_ADDRESSES = {
    "beehive": {
        "geyser": Web3.toChecksumAddress("0x075Bb66A472AB2BBB8c215629C77E8ee128CC2Fc"),
        "pool": Web3.toChecksumAddress("0xc5be99a02c6857f9eac67bbce58df5572498f40c")
    },
    "pescadero": {
        "geyser": Web3.toChecksumAddress("0XC88BA3885995CE2714C14816A69A09880E1E518C"),
        "pool": Web3.toChecksumAddress("0xcb2286d9471cc185281c4f763d34a962ed212962")
    },
    "old_faithful": {
        "geyser": Web3.toChecksumAddress("0x42d3c21DF4a26C06d7084f6319aCBF9195a583C1"),
        "pool": Web3.toChecksumAddress("0x7860e28ebfb8ae052bfe279c07ac5d94c9cd2937"),
        "token": Web3.toChecksumAddress("0x49F2befF98cE62999792Ec98D0eE4Ad790E7786F")
    },
    "trinity": {
        "geyser": Web3.toChecksumAddress("0xcF98862a8eC1271c9019D47715565a0Bf3a761B8"),
        "pool": Web3.toChecksumAddress("0xa751a143f8fe0a108800bfb915585e4255c2fe80")
    },
}

CHAINLINK_PRICE_FEEDS = {
    "ampl": Web3.toChecksumAddress("0xe20CA8D7546932360e37E9D72c1a47334af57706"),
    # NOTE: wbtc price feed is actually btc's
    "wbtc": Web3.toChecksumAddress("0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c"),
    # NOTE: weth price feed is actually eth's
    "weth": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"
}
