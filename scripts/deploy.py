import os
import sys
import signal
from brownie import (
    Oracle,
    BancorFormula,
    SperaxTokenL2,
    VaultCoreLibrary,
    VaultCore,
    USDsL2,
    accounts,
    network,
)

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    #if not os.environ.get('WEB3_INFURA_PROJECT_ID'):
    #    print("\nEnvironment variable WEB3_INFURA_PROJECT_ID is not set\n")
    #    return

    print("\nEnter minter account password:")
    try:
        owner = accounts.load(filename="minter.keystore")
    except ValueError:
        print("\nInvalid wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/minter.json")
        return

    print('account balance: {owner.balance()}\n')

    name = input("Enter name (Sperax USD): ") or "Sperax USD"
    symbol = input("Enter symbol (USDs): ") or "USDs"

    print(f"\ndeploying to {network.show_active()}:")

    # deploy smart contracts
    bancor = BancorFormula.deploy(
        {"from": owner},
#        publish_source=False,
    )
    print(f"Bancor Formula address: {bancor.address}\n")
    bancor.init()

    spa = SperaxTokenL2.deploy(
        'Sperax',
        'SPA',
        {"from": owner},
#        publish_source=False,
    )
    print(f"SPA layer 2 address: {spa.address}\n")

    core = VaultCoreLibrary.deploy(
            {"from": owner},
            publish_source=False,
        )
    print(f"Vault Core Library address: {core.address}\n")

    vault = VaultCore.deploy(
        {"from": owner},
#        publish_source=False,
    )
    print(f"Vault Core address: {vault.address}\n")
    vault.initialize(
        spa.address,
        bancor.address,
        {"from": owner}
    )

    oracle = Oracle.deploy(
        {"from": owner},
#        publish_source=False,
    )
    print(f"Oracle address: {oracle.address}\n")

    price_feed_eth_arbitrum_testnet = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    weth_arbitrum_testnet = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'

    oracle.initialize(
        price_feed_eth_arbitrum_testnet,
        spa.address,
        weth_arbitrum_testnet,
        {"from": owner}
    )

    usds = USDsL2.deploy(
            {"from": owner},
    #        publish_source=False,
        )
    print(f"USDs layer 2 address: {usds.address}\n")
    usds.initialize(
        name,
        symbol,
        vault.address,
        {"from": owner}
    )

    # configure VaultCore contract with USDs contract address
    vault.updateUSDsAddress(
        usds,
        {'from': owner}
    )
    # configure VaultCore contract with Oracle contract address
    vault.updateOracleAddress(
        oracle.address,
        {'from': owner}
    )
    # add collateral
    #vault.addCollateral(
    #    {'from': owner}
    #)