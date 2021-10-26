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

    initial_balance = owner.balance()
    print('account balance: {initial_balance}\n')

    name = input("Enter name (Sperax USD): ") or "Sperax USD"
    symbol = input("Enter symbol (USDs): ") or "USDs"

    l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'
    price_feed_eth_arbitrum_testnet = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    weth_arbitrum_testnet = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'

    if network.show_active() == 'arbitrum-mainnet':
        l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'
        price_feed_eth_arbitrum_testnet = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
        weth_arbitrum_testnet = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'

    # deploy smart contracts
    bancor = BancorFormula.deploy(
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=False,
    )
    txn = bancor.init()

    core = VaultCoreLibrary.deploy(
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=False,
    )

    vault = VaultCore.deploy(
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=False,
    )

    oracle = Oracle.deploy(
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=False,
    )

    usds = USDsL2.deploy(
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=False,
    )

    spa = SperaxTokenL2.deploy(
        'Sperax',
        'SPA',
        l2_gateway,
        usds.address,
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=False,
    )

    txn = vault.initialize(
        spa.address,
        bancor.address,
        {'from': owner, 'gas_limit': 1000000000}
    )

    txn = oracle.initialize(
        price_feed_eth_arbitrum_testnet,
        spa.address,
        weth_arbitrum_testnet,
        {'from': owner, 'gas_limit': 1000000000}
    )

    l1_address = '0x377ff873b648b678608b216467ee94713116c4cd' # USDs address on layer 1 [rinkeby]
    txn = usds.initialize(
        name,
        symbol,
        vault.address,
        l2_gateway,
        l1_address,
        {'from': owner, 'gas_limit': 1000000000}
    )

    # configure VaultCore contract with USDs contract address
    txn = vault.updateUSDsAddress(
        usds,
        {'from': owner, 'gas_limit': 1000000000}
    )
    # configure VaultCore contract with Oracle contract address
    txn = vault.updateOracleAddress(
        oracle.address,
        {'from': owner, 'gas_limit': 1000000000}
    )
    # add collateral
    #vault.addCollateral(
    #    {'from': owner}
    #)

    print(f"\n{network.show_active()}:")
    print(f"Bancor Formula address: {bancor.address}\n")
    print(f"Vault Core Library address: {core.address}\n")
    print(f"Vault Core address: {vault.address}\n")
    print(f"Oracle address: {oracle.address}\n")
    print(f"USDs layer 2 address: {usds.address}\n")
    print(f"SPA layer 2 address: {spa.address}\n")

    final_balance = owner.balance()
    print('account balance: {final_balance}\n')
    gas_cost = initial_balance - final_balance
    print('gas cost: {gas_cost}\n')