import sys
import signal
from brownie import (
    SperaxTokenL1,
    network,
    Contract,
    accounts
)

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

    print(f"\nConfigure Arbitrum gateway on {network.show_active()}:\n")
    spa_l1_address = input("Enter L1 SPA address: ").strip()
    if len(spa_l1_address) == 0:
        print("\nMissing L1 SPA address\n")
        return
    spa_l2_address = input("Enter L2 SPA address: ").strip()
    if len(spa_l2_address) == 0:
        print("\nMissing L2 SPA address\n")
        return


    if network.show_active() == 'arbitrum-rinkeby':
        l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'


    spa_l2 = Contract.from_abi(
        "SperaxTokenL2",
        spa_l2_address,
        SperaxTokenL1.abi
    )

    txn = spa_l2.changeArbToken(
        l2_gateway,
        spa_l1_address,
        {'from': owner, 'gas_limit': 5000381, 'allow_revert' : True}
    )
