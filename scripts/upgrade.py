import sys
import signal
import click
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

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    # proxy admin account
    admin = accounts.load(
        click.prompt(
            "admin account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"admin account: {admin.address}\n")

    # contract owner account
    owner = accounts.load(
        click.prompt(
            "owner account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"contract owner account: {owner.address}\n")

    # TODO: create a separate wallet for fee_vault account
    fee_vault = owner

    print("\nPress enter if you do not wish to upgrade a specific contract\n")
    usds_proxy_address = input("Enter USDs proxy address: ").strip()
    vault_proxy_address = input("Enter VaultCore proxy address: ").strip()
    oracle_proxy_address = input("Enter Oracle proxy address: ").strip()

    if len(oracle_proxy_address) > 0:
        # Arbitrum-one (mainnet):
        chainlink_eth_price_feed = '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612'
        weth_arbitrum = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
        chainlink_flags = '0x3C14e07Edd0dC67442FA96f1Ec6999c57E810a83'

        # Arbitrum rinkeby:
        if network.show_active() == 'arbitrum-rinkeby':
            l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'
            chainlink_eth_price_feed = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
            weth_arbitrum = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'
            chainlink_flags = '0x491B1dDA0A8fa069bbC1125133A975BF4e85a91b'

    initial_balance = admin.balance()

    # proxy admin contract
    proxy_admin = ProxyAdmin[-1]

    print(f"\n{network.show_active()}:\n")

    if len(vault_proxy_address) > 0:
        print("set mintRedeemAllowed to false to check that state changes:\n")
        vault_proxy = Contract.from_abi(
            "VaultCore",
            vault_proxy_address,
            VaultCore.abi
        )

        # set mintRedeemAllowed to false to check that state changes
        vault_proxy.updateMintBurnPermission(False, {'from': owner, 'gas_limit': 1000000000})
        print(f"mintRedeemAllowed is now: {vault_proxy.mintRedeemAllowed()}\n")

        print("upgrade Vault contract:\n")
        new_vault = VaultCoreV2.deploy(
            {'from': owner, 'gas_limit': 1000000000}
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
        print(f"Vault version: {new_vault_proxy.version()}")
        print(f"mintRedeemAllowed is still (should be false): {vault_proxy.mintRedeemAllowed()}\n")

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

        
        usds_proxy = Contract.from_abi(
            "USDsL2",
            usds_proxy_address,
            USDsL2.abi
        )

        # change vault address to verify state changes persist
        vitalik_address = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
        usds_proxy.changeVault(vitalik_address, {'from': owner, 'gas_limit': 1000000000})
        print(f"vaultAddress is now: {usds_proxy.vaultAddress()}\n")
        
        
        new_usds = USDsL2V2.deploy(
            {'from': owner, 'gas_limit': 1000000000}
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
        print(f"USDsL2 version: {new_usds_proxy.version()}")
        print(f"vaultAddress is still (should be 0xd8da6bf26964af9d7eed9e03e53415d37aa96045): {usds_proxy.vaultAddress()}\n")

    if len(oracle_proxy_address) > 0:
       
        
        oracle_proxy = Contract.from_abi(
            "Oracle",
            oracle_proxy_address,
            Oracle.abi
        )

        # change vault address to verify state changes persist
        vitalik_address = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
        oracle_proxy.updateVaultAddress(vitalik_address, {'from': owner, 'gas_limit': 1000000000})
        print(f"VaultAddr is now: {oracle_proxy.VaultAddr()}\n")

        print("upgrade Oracle contract:\n")
        new_oracle = OracleV2.deploy(
            {'from': owner, 'gas_limit': 1000000000}
        )

        proxy_admin.upgrade(
            oracle_proxy.address,
            new_oracle.address,
            {'from': admin, 'gas_limit': 1000000000}
        )
        new_oracle.initialize(
            chainlink_eth_price_feed,
            SperaxTokenL2[-1],
            weth_arbitrum,
            chainlink_flags,
            {'from': owner, 'gas_limit': 1000000000}
        )

        new_oracle_proxy = Contract.from_abi(
            "OracleV2",
            oracle_proxy.address,
            OracleV2.abi
        )
        print(f"original Oracle proxy address: {oracle_proxy.address}")
        print(f"upgraded Oracle proxy address: {new_oracle_proxy.address}")
        print(f"Oracle  version: {new_oracle_proxy.version()}")
        print(f"VaultAddr is still (should be 0xd8da6bf26964af9d7eed9e03e53415d37aa96045): {oracle_proxy.VaultAddr()}\n")


    if len(vault_proxy_address) > 0 and len(oracle_proxy_address) > 0:
        new_vault_proxy.updateOracleAddress(
            new_oracle_proxy.address,
            {'from': owner, 'gas_limit': 1000000000}
        )
        new_oracle_proxy.updateVaultAddress(
            new_vault_proxy.address,
            {'from': owner, 'gas_limit': 1000000000}
        )