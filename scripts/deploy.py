import os
import sys
import signal
from brownie import (
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

    if not os.environ.get('WEB3_INFURA_PROJECT_ID'):
        print("\nEnvironment variable WEB3_INFURA_PROJECT_ID is not set\n")
        return

    print("\nEnter account password:")
    try:
        owner = accounts.load(filename="niftmint.keystore")
    except ValueError:
        print("\nInvalid wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/niftmint.json")
        return

    print("\nUSDs layer 2\n")
    name = input("Enter name: ")
    if not name:
        print("\nMissing token name")
    symbol = input("Enter symbol: ")
    if not symbol:
        print("\nMissing token symbol")

    print(f"\ndeploying to {network.show_active()}:")

    # deploy smart contracts
    core = VaultCoreLibrary.deploy(
            {"from": owner},
            publish_source=True,
        )
    print("\nVault address: ", core.address)
    print("version: ", core.version())
    vault = VaultCore.deploy(
            {"from": owner},
            publish_source=True,
        )
    print("\nVault address: ", vault.address)
    print("version: ", vault.version())

    usdsl2 = USDsL2.deploy(
            {"from": owner},
            publish_source=False,
        )
    print("\nsmart contract address: ", usdsl2.address)
    print("version: ", usdsl2.version())
    usdsl2 = USDsL2.initialize(
            name,
            symbol,
            vault.address,
            {"from": owner}
        )