import sys
import signal
from brownie import (
    ProxyAdmin,
    VaultCoreTools,
    SperaxTokenL2,
    USDsL2,
    USDsL2V2,
    Oracle,
    OracleV2,
    VaultCore,
    VaultCoreV2,
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

    print("\nEnter admin account password:")
    try:
        admin = accounts.load(filename="admin.keystore")
    except ValueError:
        print("\nInvalid admin wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/admin.json")
        return

    print("\nEnter contract owner account password:")
    try:
        owner = accounts.load(filename="minter.keystore")
    except ValueError:
        print("\nInvalid contract owner wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/minter.json")
        return

    # TODO: create a separate wallet for fee_vault account
    fee_vault = owner

    print("\nPress enter if you do not wish to upgrade a specific contract\n")
    usds_proxy_address = input("Enter USDs proxy address: ").strip()
    vault_proxy_address = input("Enter VaultCore proxy address: ").strip()
    oracle_proxy_address = input("Enter Oracle proxy address: ").strip()

    if len(oracle_proxy_address) > 0:
        if network.show_active() == 'arbitrum-rinkeby':
            # Arbitrum rinkeby:
            price_feed_eth_arbitrum = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
            weth_arbitrum = '0xB47e6A5f8b33b3F17603C83a0535A9dcD7E32681'
        else:
            # Arbitrum mainnet:
            price_feed_eth_arbitrum = '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612'
            weth_arbitrum = ''

    initial_balance = admin.balance()

    # proxy admin contract
    proxy_admin = ProxyAdmin[-1]

    print(f"\n{network.show_active()}:\n")

    if len(vault_proxy_address) > 0:
        print("upgrade Vault contract:\n")
        new_vault = VaultCoreV2.deploy(
            {'from': owner, 'gas_limit': 1000000000}
        )
        vault_proxy = Contract.from_abi(
            "VaultCore",
            vault_proxy_address,
            VaultCore.abi
        )
        proxy_admin.upgrade(
            vault_proxy.address,
            new_vault.address,
            {'from': admin, 'gas_limit': 1000000000}
        )
        new_vault.initialize(
            SperaxTokenL2[-1],
            VaultCoreTools[-1],
            fee_vault,
            {'from': owner, 'gas_limit': 1000000000}
        )

        new_vault_proxy = Contract.from_abi(
            "VaultCoreV2",
            vault_proxy.address,
            VaultCoreV2.abi
        )
        print(f"original Vault proxy address: {vault_proxy.address}")
        print(f"upgraded Vault proxy address: {new_vault_proxy.address}")
        print(new_vault_proxy.version())

    if len(usds_proxy_address) > 0:
        print("upgrade USDs contract:\n")
        if len(vault_proxy_address) == 0:
            vault_proxy_address = input("Enter VaultCore proxy address: ").strip()
            if len(vault_proxy_address) == 0:
                print("\nMissing Vault proxy address\n")
                return

        vault_proxy = Contract.from_abi(
            "VaultCore",
            vault_proxy_address,
            VaultCore.abi
        )

        new_usds = USDsL2V2.deploy(
            {'from': owner, 'gas_limit': 1000000000}
        )
        usds_proxy = Contract.from_abi(
            "USDsL2",
            usds_proxy_address,
            USDsL2.abi
        )
        proxy_admin.upgrade(
            usds_proxy.address,
            new_usds.address,
            {'from': admin, 'gas_limit': 1000000000}
        )
        new_usds.initialize(
            usds_proxy.name(),
            usds_proxy.symbol(),
            vault_proxy.address,
            usds_proxy.l2Gateway(),
            usds_proxy.l1Address(),
            {'from': owner, 'gas_limit': 1000000000}
        )

        new_usds_proxy = Contract.from_abi(
            "USDsL2V2",
            usds_proxy.address,
            VaultCoreV2.abi
        )
        print(f"original USDsL2 proxy address: {usds_proxy.address}")
        print(f"upgraded USDsL2 proxy address: {new_usds_proxy.address}")
        print(new_usds_proxy.version())

    if len(oracle_proxy_address) > 0:
        print("upgrade Oracle contract:\n")
        new_oracle = OracleV2.deploy(
            {'from': owner, 'gas_limit': 1000000000}
        )
        oracle_proxy = Contract.from_abi(
            "Oracle",
            oracle_proxy_address,
            Oracle.abi
        )
        proxy_admin.upgrade(
            oracle_proxy.address,
            new_oracle.address,
            {'from': admin, 'gas_limit': 1000000000}
        )
        new_oracle.initialize(
            price_feed_eth_arbitrum,
            SperaxTokenL2[-1],
            weth_arbitrum,
            {'from': owner, 'gas_limit': 1000000000}
        )

        new_oracle_proxy = Contract.from_abi(
            "OracleV2",
            oracle_proxy.address,
            OracleV2.abi
        )
        print(f"original Oracle proxy address: {oracle_proxy.address}")
        print(f"upgraded Oracle proxy address: {new_oracle_proxy.address}")
        print(new_oracle_proxy.version())


    if len(vault_proxy_address) > 0 and len(oracle_proxy_address) > 0:
        new_vault_proxy.updateOracleAddress(
            new_oracle_proxy.address,
            {'from': owner, 'gas_limit': 1000000000}
        )
        new_oracle_proxy.updateVaultAddress(
            new_vault_proxy.address,
            {'from': owner, 'gas_limit': 1000000000}
        )