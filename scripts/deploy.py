import os
import sys
import signal
from brownie import (
    TransparentUpgradeableProxy,
    ProxyAdmin,
    Oracle,
    BancorFormula,
    SperaxTokenL2,
    VaultCoreLibrary,
    VaultCore,
    USDsL2,
    accounts,
    network,
    Contract,
)
import eth_utils

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    #if not os.environ.get('WEB3_INFURA_PROJECT_ID'):
    #    print("\nEnvironment variable WEB3_INFURA_PROJECT_ID is not set\n")
    #    return

    print("\nEnter admin account password:")
    try:
        admin = accounts.load(filename="admin.keystore")
    except ValueError:
        print("\nInvalid admin wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/admin.json")
        return

    print("\nEnter owner account password:")
    try:
        owner = accounts.load(filename="minter.keystore")
    except ValueError:
        print("\nInvalid owner wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/minter.json")
        return

    initial_balance = owner.balance()
    print('account balance: {initial_balance}\n')

    name = input("Enter name (Sperax USD): ") or "Sperax USD"
    symbol = input("Enter symbol (USDs): ") or "USDs"
    print('\n')

    # Arbitrum rinkeby:
    l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'
    price_feed_eth_arbitrum_testnet = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    weth_arbitrum_testnet = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'
    l1_address = '0x377ff873b648b678608b216467ee94713116c4cd' # USDs address on layer 1 [rinkeby]

    if network.show_active() == 'arbitrum-mainnet':
        l2_gateway = ''
        price_feed_eth_arbitrum_testnet = ''
        weth_arbitrum_testnet = ''
        l1_address = '' # USDs address on layer 1 [rinkeby]

    # admin contract
    proxy_admin = ProxyAdmin.deploy(
        {'from': owner, 'gas_limit': 1000000000},
    )

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
    proxy = TransparentUpgradeableProxy.deploy(
        vault.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': owner, 'gas_limit': 1000000000},
    )
    vault_proxy = Contract.from_abi("VaultCore", proxy.address, VaultCore.abi)

    oracle = Oracle.deploy(
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=False,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        oracle.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': owner, 'gas_limit': 1000000000},
    )
    oracle_proxy = Contract.from_abi("Oracle", proxy.address, Oracle.abi)

    usds = USDsL2.deploy(
        name,
        symbol,
        vault_proxy.address,
        l2_gateway,
        l1_address,
        {'from': owner, 'gas_limit': 1000000000}
    )

    spa = SperaxTokenL2.deploy(
        'Sperax',
        'SPA',
        l2_gateway,
        usds.address,
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=False,
    )

    txn = oracle_proxy.initialize(
        price_feed_eth_arbitrum_testnet,
        spa.address,
        weth_arbitrum_testnet,
        {'from': owner, 'gas_limit': 1000000000}
    )

    txn = vault_proxy.initialize(
        spa.address,
        bancor.address,
        {'from': owner, 'gas_limit': 1000000000}
    )

    # configure VaultCore contract with USDs contract address
    txn = vault_proxy.updateUSDsAddress(
        usds,
        {'from': owner, 'gas_limit': 1000000000}
    )
    # configure VaultCore contract with Oracle contract address
    txn = vault_proxy.updateOracleAddress(
        oracle_proxy.address,
        {'from': owner, 'gas_limit': 1000000000}
    )

    print(f"\n{network.show_active()}:\n")
    print(f"Bancor Formula address: {bancor.address}")
    print(f"Vault Core Library address: {core.address}")

    print(f"Vault Core:")
    print(f"\taddress: {vault.address}")
    print(f"\tproxy address: {vault_proxy.address}")

    print(f"Oracle:")
    print(f"\taddress: {oracle.address}")
    print(f"\tproxy address: {oracle_proxy.address}")

    print(f"USDs layer 2 address: {usds.address}")
    print(f"SPA layer 2 address: {spa.address}")

    final_balance = owner.balance()
    print(f'\naccount balance: {final_balance}')
    gas_cost = initial_balance - final_balance
    gas_cost = "{:,}".format(gas_cost) # format with comma delimiters
    print(f'gas cost: {gas_cost} gwei\n')