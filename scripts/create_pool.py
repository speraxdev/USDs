import sys
import signal
import click
import brownie
import math
from brownie import (
    VaultCore,
    SperaxTokenL2,
    USDsL2,
    network,
    Contract,
    accounts
)

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    # contract owner account
    owner = accounts.load(
        click.prompt(
            "admin account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"contract owner account: {owner.address}\n")

    vault_proxy_address = input("Enter VaultCore proxy address: ").strip()
    if len(vault_proxy_address) == 0:
        print("missing VaultCore proxy address")
        return
    spa_proxy_address = input("Enter SPA address: ").strip()
    if len(spa_proxy_address) == 0:
        print("missing SPA address")
        return
    usds_proxy_address = input("Enter USDs L2 proxy address: ").strip()
    if len(usds_proxy_address) == 0:
        print("missing USDs L2 proxy address")
        return

    vault_proxy = Contract.from_abi(
        "VaultCore",
        vault_proxy_address,
        VaultCore.abi
    )

    spa = Contract.from_abi(
        "SperaxTokenL2",
        spa_proxy_address,
        SperaxTokenL2.abi
    )

    usds_proxy = Contract.from_abi(
        "USDsL2",
        usds_proxy_address,
        USDsL2.abi
    )

    mint_usds(amount, mock_token, spa, vault_proxy, owner)

    create_uniswap_v3_pool(
        usds_proxy, # token1: USDS
        amount, # amount1
        mock_token, # token2
        mock_token.balanceOf(owner), # amount2
        owner
    )

def mint_usds(mock_token_amount, mock_token, spa, vault_proxy, owner):
    # put owner into the mintableGroup of SPA
    txn = spa.setMintable(
        owner,
        True,
        {'from': owner}
    )
    assert txn.events['Mintable']['account'] == owner

    spa.approve(
        vault_proxy.address,
        2**256-1, # large number
        {'from': owner}
    )
    mock_token.approve(
        vault_proxy.address,
        2**256-1, # large number
        {'from': owner}
    )

    deadline = 1637632800 + brownie.chain.time() # deadline: 2 hours
    # mint USDs by specifying amount of SPA to burn
    txn = vault_proxy.mintWithColla(
        mock_token.address,
        mock_token_amount,
        0, # USDs slippage
        1, # collateral slippage
        deadline,
        {'from': owner}
    )
    assert txn.events['USDsMinted']['wallet'] == owner
    assert txn.events['USDsMinted']['USDsAmt'] == mock_token_amount


# create pool for pair tokens (input parameters) on Arbitrum-one
# To obtain the interface to INonfungiblePositionManager required
# copying the following files from @uniswap-v3-periphery@1.3.0:
#
# - contracts/interface/IERC721Permit.sol
# - contracts/interface/INonfungiblePositionManager.sol
# - contracts/interface/IPeripheryImmutableState.sol
# - contracts/interface/IPeripheryPayments.sol
# - contracts/interface/IPoolInitializer.sol
# - contracts/libraries/PoolAddress.sol
def create_uniswap_v3_pool(
    token1,
    amount1,
    token2,
    amount2,
    owner
):
    position_mgr_address = '0xC36442b4a4522E871399CD717aBDD847Ab11FE88'
    position_mgr = brownie.interface.INonfungiblePositionManager(position_mgr_address)

    # approve uniswap's non fungible position manager to transfer our tokens
    token1.approve(position_mgr.address, amount1, {'from': owner})
    token2.approve(position_mgr.address, amount2, {'from': owner})

    # create a transaction pool
    fee = 3000
    txn = position_mgr.createAndInitializePoolIfNecessary(
        token1,
        token2,
        fee,
        encode_price(amount1, amount2),
        {'from': owner}
    )
    # newly created pool address
    pool = txn.return_value
    print(f"pool: {pool.address}")
    
    # provide initial liquidity
    deadline = 1637632800 + brownie.chain.time() # deadline: 2 hours
    params = [
        token1,
        token2,
        fee,
        get_lower_tick(), # tickLower
        get_upper_tick(), # tickUpper
        amount1,
        amount2,
        0, # minimum amount of token1 expected
        0, # minimum amount of token2 expected
        owner,
        deadline
    ]
    txn = position_mgr.mint(
        params,
        {'from': owner}
    )
    print(txn.return_value)

def get_lower_tick():
    return math.ceil(-887272 / 60) * 60

def get_upper_tick():
    return math.floor(887272 / 60) * 60

def encode_price(n1, n2):
    return math.trunc(math.sqrt(int(n1)/int(n2)) * 2**96)