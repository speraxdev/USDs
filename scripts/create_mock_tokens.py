import sys
import signal
import click
from brownie import (
    MockToken,
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

    mock_usdt = MockToken.deploy(
        'Mock USDT',
        'MockUSDT',
        6,
        {'from': owner},
    )
    mock_wbtc = MockToken.deploy(
        'Mock WBTC',
        'MockWBTC',
        8,
        {'from': owner},
    )
    mock_dai = MockToken.deploy(
        'Mock Dai',
        'MockDAI',
        18,
        {'from': owner},
    )
