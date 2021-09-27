from enum import Enum
from decimal import Decimal
from typing import (
    List, 
    Optional, 
    Tuple,
    NewType,
)

from web3.eth import Contract
from web3.types import ChecksumAddress

# Tokens
Token = NewType("Token", ChecksumAddress)
Ticker = NewType("Ticker", str)
Balance = NewType("Balance", Decimal)
TokenBalance = NewType("TokenAmount", Tuple[Token, Balance])

LockedTokenBalance = NewType("LockedTokenBalance", List[TokenBalance])
ClaimedTokenBalance = NewType("ClaimedTokenBalance", List[TokenBalance])

# Universal Vault
VaultId = NewType("VaultId", str)
VaultContent = NewType("VaultContent", 
                       Tuple[ClaimedTokenBalance, LockedTokenBalance])

# User Positions
UserPosition = NewType("UserPosition", Tuple[Token, Ticker, Balance])
LPPosition = List[UserPosition]

# ENS
ENSName = str
ENSAddress = Tuple[Optional[ENSName], ChecksumAddress]


class GeyserInstance(Enum):
    BEEHIVE = "Beehive"
    PESCADERO = "Pescadero"
    OLD_FAITHFUL = "Old Faithful"
    TRINITY = "Trinity"
