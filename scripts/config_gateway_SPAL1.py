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
    credit_back_address = input("Enter credit back address: ").strip()
    if len(credit_back_address) == 0:
        print("\nMissing credit back address\n")
        return

    if network.show_active() == 'rinkeby':
        l1_gateway = '0x917dc9a69F65dC3082D518192cd3725E1Fa96cA2'
        l1_router = '0x70C143928eCfFaf9F5b406f7f4fC28Dc43d68380'


    spa_l1 = Contract.from_abi(
        "SperaxTokenL1",
        spa_l1_address,
        SperaxTokenL1.abi
    )

    txn = spa_l1.changeArbToken(
        l1_gateway,
        l1_router,
        {'from': owner, 'gas_limit': 5000381, 'allow_revert' : True}
    )

    txn = spa_l1.registerTokenOnL2(
        spa_l2_address, # l2CustomTokenAddress
        33406636145, # maxSubmissionCostForCustomBridge
        33406636145, # maxSubmissionCostForRouter
        1000000, # maxGas
        25319114, # gasPriceBid
        credit_back_address, # creditBackAddress
        {'from': owner, 'gas_limit': 5000381, 'allow_revert' : True}
    )
