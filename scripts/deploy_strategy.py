import sys
import signal
from brownie import (
    BuybackSingle,
    BuybackMultihop,
    USDsL2,
    VaultCore,
    accounts,
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

    print("\nEnter contract owner account password:")
    try:
        owner = accounts.load(filename="minter.keystore")
    except ValueError:
        print("\nInvalid owner wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/minter.json")
        return

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