from typing import (
    Tuple,
    List,
    Optional,
    NewType,
)
from decimal import Decimal

from web3 import Web3
from web3.types import ChecksumAddress

from .types import (
    LockedTokenBalance,
    ClaimedTokenBalance,
    VaultId,
    VaultContent,
)
from .utils import send_subgraph_query


def get_vault_content(id: VaultId) -> Optional[VaultContent]:
    """
    Fetch claimed and locked tokens for given vault.

    :param id: The vault's id
    :return:   (claimed tokens, locked tokens)
    """
    query = '''query{
        vault(id: "''' + id + '''") {
	        claimedReward {
                token,
                amount
            },
	        locks {
                token,
                amount,
                stakeUnits
            }
        }
    }'''

    resp = send_subgraph_query(query)
    result = resp['data']['vault']
    if not result:
        # No vault information found
        return None

    claimed_tokens: ClaimedTokenBalance = []
    for claimed in result['claimedReward']:
        token = Web3.toChecksumAddress(claimed['token'])
        amount = Decimal(claimed['amount'])

        claimed_tokens.append(
            (token, amount)
        )
        
    locked_tokens: LockedTokenBalance = []
    for locked in result['locks']:
        token = Web3.toChecksumAddress(locked['token'])
        amount = Decimal(locked['amount'])

        locked_tokens.append(
            (token, amount)
        )

    return claimed_tokens, locked_tokens


def get_vaults(user: ChecksumAddress) -> Optional[List[VaultId]]:
    """
    Fetch all vaults associated with given user.

    :param user: The user's ETH address
    :return:     List of VaulId's or None
    """
    # TheGraph expects addresses in lowercase
    user = user.lower()

    query = '''query {
        user(id: "''' + user + '''") {
            vaults {
                id
            }
        }
    }'''

    resp = send_subgraph_query(query)
    if not resp['data']['user']:
        # No vault found for this user
        return None

    vaults: List[VaultId] = []

    for vault in resp['data']['user']['vaults']:
        vaults.append(vault['id'])

    return vaults
