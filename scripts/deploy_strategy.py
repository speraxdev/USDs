import sys
import signal
import click
from brownie import (
    ProxyAdmin,
    TransparentUpgradeableProxy,
    ThreePoolStrategy,
    BuybackSingle,
    BuybackMultihop,
    USDsL2,
    VaultCore,
    accounts,
    interface,
    network,
    Contract,
    convert
)
import eth_utils

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    # proxy admin account
    admin = accounts.load(
        click.prompt(
            "admin account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"admin account: {admin.address}\n")

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
    usds_proxy_address = input("Enter USDs L2 proxy address: ").strip()
    if len(usds_proxy_address) == 0:
        print("missing USDs L2 proxy address")
        return
    token1_address = input("Enter token address: ").strip()
    if len(token1_address) == 0:
        print("missing token address")
        return
    token2_address = input("Enter intermediate token address: ").strip()
    pool1_fee = int(input("Enter pool fee 1 (%): ").strip())
    pool2_fee = int(input("Enter pool fee 2 (%): ").strip())

    vault_proxy = Contract.from_abi(
        "VaultCore",
        vault_proxy_address,
        VaultCore.abi
    )

    usds_proxy = Contract.from_abi(
        "USDsL2",
        usds_proxy_address,
        USDsL2.abi
    )

    strategy = ThreePoolStrategy.deploy(
        {'from': owner},
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        strategy.address,
        ProxyAdmin[-1],
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin},
#        publish_source=True,
    )
    strategy_proxy = Contract.from_abi(
        "ThreePoolStrategy",
        proxy.address,
        ThreePoolStrategy.abi
    )
    strategy_proxy.initialize(
        '0xF97c707024ef0DD3E77a0824555a46B622bfB500', # platform address
        vault_proxy.address, # vault address
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978', # reward token address
        # assets
        # p tokens
        '0x97E2768e8E73511cA874545DC5Ff8067eB19B787', # crv gauge address
        interface.IWETH9('0x82af49447d8a07e3bd95bd0d56f35241523fbab1'), # arbitrum-one weth address
        {'from': owner},
    )

    # call multihop buyback contract if intermediate token is provided
    if len(token2_address) > 0:
        buyback = BuybackMultihop(
            usds_proxy.address,
            vault_proxy.address,
            {'from': owner},
    #        publish_source=True,
        )
        buyback.updateInputTokenInfo(
            token1_address,
            True, # supported
            token2_address, # intermediate token
            pool1_fee,
            pool2_fee,
            {'from': owner}
        )
        print(f"Multihop Buyback contract address: {buyback.address}")
    else:
        # deploy smart contracts
        buyback = BuybackSingle.deploy(
            usds_proxy.address,
            vault_proxy.address,
            {'from': owner},
    #        publish_source=True,
        )
        buyback.updateInputTokenInfo(
            token1_address,
            True, # supported
            pool1_fee,
            {'from': owner}
        )
        print(f"Single Buyback contract address: {buyback.address}")