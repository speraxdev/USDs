import signal
import click
from brownie import (
    SperaxTokenL1,
    accounts,
    network,
    Contract,
)
import os
from .constants import (
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

    print(f"\nDeploying on {network.show_active()}:\n")
    spa_l1 = getAddressFromNetwork(
        testnet_L1_addresses.L1_SPA,
        mainnet_L1_addresses.L1_SPA
    )
    bridge = getAddressFromNetwork(
        testnet_L1_addresses.bridge,
        mainnet_L1_addresses.bridge
    )
    router = getAddressFromNetwork(
        testnet_L1_addresses.router,
        mainnet_L1_addresses.router
    )
    print(f"\nL1 SPA address: {spa_l1}")
    print(f"L1 Bridge address: {bridge}")
    print(f"L1 Router address: {router}\n")
    confirm("Are the above addresses correct?")

    name = wSPAL1_token_details.name
    symbol = wSPAL1_token_details.symbol
    print(f"\nToken Name: {name}")
    print(f"Token Symbol: {symbol}\n")
    confirm("Are the above details correct?")
    print('\n')

    wSPAL1 = SperaxTokenL1.deploy(
        name,
        symbol,
        spa_l1,
        bridge,
        router,
        {'from': owner, 'gas_limit': 10000000}
#        publish_source=True,
    )

    cwd = os.getcwd()
    filepath = cwd + '/supporting_contracts/SperaxTokenABI.json'
    with open(filepath) as f:
        abi = json.load(f)

    sperax_token = Contract.from_abi(
        'SperaxToken',
        spa_l1,
        abi
    )
    
    print(f"\nAllowing wSPAL1 to mint Sperax\n")
    
    sperax_token.setMintable(
        wSPAL1.address, 
        True, 
        {'from': owner, 'gas_limit': 10000000}
    )

    mint_amount = getNumber("How much wSPA would you like to mint? ")
    confirm(f"Are you sure you want to mint {mint_amount} wSPA?")

    allowance = sperax_token.allowance(
        owner.address,
        wSPAL1.address
    )

    if allowance < mint_amount:
        choice("You haven't approved wSPAL1 to burn enough of your Sperax to mint wrapped Sperax. Do you want to approve now?")
        print(f"\nAllowing {owner.address} to transfer {mint_amount} Sperax to wSPAL1\n")
        sperax_token.approve(
            wSPAL1.address,
            mint_amount,
            {'from': owner, 'gas_limit': 10000000}
        )

    wSPAL1.mint(
        mint_amount,
        {'from': owner, 'gas_limit': 10000000}
    )
    
    print(f"\nwSPA layer 1 address:  {wSPAL1.address}\n")