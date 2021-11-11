import sys
import signal
from brownie import (
    SperaxTokenL1,
    network,
    Contract,
)

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

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

    spa_l1 = Contract.from_abi(
        "SperaxTokenL1",
        spa_l1_address,
        SperaxTokenL1.abi
    )

    txn = spa_l1.registerTokenOnL2(
        spa_l2_address, # l2CustomTokenAddress
        33406636145, # maxSubmissionCostForCustomBridge
        33406636145, # maxSubmissionCostForRouter
        100000, # maxGas
        25319114, # gasPriceBid
        credit_back_address # creditBackAddress
    )
    print(txn.events)