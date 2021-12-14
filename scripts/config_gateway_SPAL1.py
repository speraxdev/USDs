import sys
import signal
import click
from brownie import (
    SperaxTokenL1,
    network,
    Contract,
    accounts
)
import os
from .constants import (
    mainnetAddresses,
    testnetAddresses,
    testnet_L1_addresses,
    mainnet_L1_addresses,
    wSPAL1_token_details
)
from .utils import (
    confirm,
    choice,
    getAddressFromNetwork,
    getNumber,
    signal_handler
)
import json

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    # contract owner account
    owner = accounts.load(
        click.prompt(
            "owner account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"contract owner account: {owner.address}\n")

    print(f"\nConfigure Arbitrum gateway on {network.show_active()}:\n")
    wspa_l1 = getAddressFromNetwork(
        testnetAddresses.deploy.L1_wSPA,
        mainnetAddresses.deploy.L1_wSPA
    )
    bridge = getAddressFromNetwork(
        testnet_L1_addresses.bridge,
        mainnet_L1_addresses.bridge
    )
    router = getAddressFromNetwork(
        testnet_L1_addresses.router,
        mainnet_L1_addresses.router
    )
    spa_l2 = getAddressFromNetwork(
        testnetAddresses.deploy.L2_SPA,
        mainnetAddresses.deploy.L2_SPA
    )

    print("\nSuggesting gas price bid: arb-rinkeby (20351396) arb-mainnet (1462799366)\n")
    print("\nPlease check the lastest gas price")
    gasPriceBid = getNumber("Enter L2 gas price bid: ")
    maxSubmissionCostForCustomBridge = 1000000000000
    maxSubmissionCostForRouter = 1000000000000
    maxGas = 1000000
    value = maxSubmissionCostForCustomBridge + maxSubmissionCostForRouter + 2 * (maxGas*gasPriceBid) + 100;


    # spa_l2_address = input("Enter L2 SPA address: ").strip()
    # if len(spa_l2_address) == 0:
    #     print("\nMissing L2 SPA address\n")
    #     return
    print(f"\nL1 wSPA address: {wspa_l1}")
    print(f"\nL2 SPA address: {spa_l2}")
    print(f"L1 Bridge address: {bridge}")
    print(f"L1 Router address: {router}\n")
    confirm("Are the above addresses correct?")
    credit_back_address = owner.address;

    wspa_l1_contract = Contract.from_abi(
        "SperaxTokenL1",
        wspa_l1,
        SperaxTokenL1.abi
    )

    txn = wspa_l1_contract.registerTokenOnL2(
        spa_l2, # l2CustomTokenAddress
        maxSubmissionCostForCustomBridge, # maxSubmissionCostForCustomBridge
        maxSubmissionCostForRouter, # maxSubmissionCostForRouter
        maxGas, # maxGas
        gasPriceBid, # gasPriceBid
        maxSubmissionCostForCustomBridge,
        maxSubmissionCostForRouter,
        credit_back_address, # creditBackAddress
        {'from': owner, 'gas_limit': 500000, 'allow_revert' : True, 'amount': value}
        # amount: at least maxSubmissionCostForRouter + maxSubmissionCostForCustomBridge + 2*(maxGas * gaspricebid)
    )
    print(f"wSPA {wspa_l1} and SperaxToeken L2 {spa_l2} linked up on {network.show_active()}")
