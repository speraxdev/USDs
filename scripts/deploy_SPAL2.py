import signal
import click
from brownie import (
    SperaxTokenL2,
    accounts,
    network,
)
import eth_utils
from .constants import (
    mainnetAddresses,
    testnetAddresses,
    SPAL2_token_details
)
from .utils import (
    confirm,
    getAddressFromNetwork,
    signal_handler
)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    owner = accounts.load(
        click.prompt(
            "owner account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"contract owner account: {owner.address}\n")
    print(f"\nDeploying on {network.show_active()}:\n")
    
    spa_l1_address = getAddressFromNetwork(
        testnetAddresses.deploy.L1_wSPA,
        mainnetAddresses.deploy.L1_wSPA
    )

    l2_gateway = getAddressFromNetwork(
        testnetAddresses.third_party.l2_gateway,
        mainnetAddresses.third_party.l2_gateway
    )
    name = SPAL2_token_details.name
    symbol = SPAL2_token_details.symbol

    print(f"\nL1 SPA address: {spa_l1_address}\n")
    print(f"\nL2 Gateway address: {l2_gateway}\n")
    print(f"\nToken Name: {name}\n")
    print(f"\nToken Symbol: {symbol}\n")
    confirm("Are the above details correct?")
    

    spa = SperaxTokenL2.deploy(
        'Sperax',
        'SPA',
        l2_gateway,
        spa_l1_address,
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=True,
    )

    print(f"SPA layer 2 address: {spa.address}")