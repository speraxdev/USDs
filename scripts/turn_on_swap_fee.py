import sys
import signal
import brownie
from brownie import (
    VaultCore,
    network,
    Contract,
    accounts
)

def signal_handler(signal, frame):
    sys.exit(0)

# this script configures the Uniswap pool addresses in Oracle
# Oracle use one pool (SPA-ETH) to get the price of SPA
# and the other (USDs-USDC) to get the price of USDs
# note: configure the pool for SPA first
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
    print(f"\nConfigure Uniswap pools on Oracle on {network.show_active()}:\n")
    vaultCore_address = input("Enter VaultCore address: ").strip()
    if len(vaultCore_address) == 0:
        print("\nMissing VaultCore address\n")
        return
    vaultCore = brownie.interface.IVaultCore(vaultCore_address)

    vaultCore = Contract.from_abi(
        "VaultCore",
        vaultCore_address,
        VaultCore.abi
    )
    vaultCore.updateSwapInOutFeePermission(True, True, {'from': owner})
