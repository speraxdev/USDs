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
from . import constants, utils

def signal_handler(signal, frame):
    sys.exit(0)

vitalik_address = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
def vault_test_state_change(vault_proxy, owner):
    print("set mintRedeemAllowed to false to check that state changes:\n")
    # set mintRedeemAllowed to false to check that state changes
    vault_proxy.updateMintBurnPermission(False, {'from': owner, 'gas_limit': 1000000000})
    print(f"mintRedeemAllowed is now: {vault_proxy.mintRedeemAllowed()}\n")

def USDs_test_state_change(usds_proxy, owner):
    usds_proxy.changeVault(vitalik_address, {'from': owner, 'gas_limit': 1000000000})
    print(f"vaultAddress is now: {usds_proxy.vaultAddress()}\n")

def oracle_test_state_change(oracle_proxy, owner):
    oracle_proxy.updateVaultAddress(vitalik_address, {'from': owner, 'gas_limit': 1000000000})
    print(f"VaultAddr is now: {oracle_proxy.VaultAddr()}\n")

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

    usds_proxy_address = constants.testnetAddresses.upgrade.USDs_l2_proxy if network.show_active() == 'arbitrum-rinkeby' else constants.mainnetAddresses.upgrade.USDs_l2_proxy
    vault_proxy_address = constants.testnetAddresses.upgrade.vault_core_proxy if network.show_active() == 'arbitrum-rinkeby' else constants.mainnetAddresses.upgrade.vault_core_proxy
    oracle_proxy_address = constants.testnetAddresses.upgrade.oracle_proxy if network.show_active() == 'arbitrum-rinkeby' else constants.mainnetAddresses.upgrade.oracle_proxy

    usds_proxy_upgrade = utils.choice("Do you wish to upgrade USDs?")
    vault_proxy_upgrade = utils.choice("Do you wish to upgrade VaultCore?")
    oracle_proxy_upgrade = utils.choice("Do you wish to upgrade Oracle?")

  
    # initialize third party addresses
    chainlink_eth_price_feed = constants.testnetAddresses.third_party.chainlink_eth_price_feed if network.show_active() == 'arbitrum-rinkeby' else constants.mainnetAddresses.third_party.chainlink_eth_price_feed
    weth_arbitrum = constants.testnetAddresses.third_party.weth_arbitrum if network.show_active() == 'arbitrum-rinkeby' else constants.mainnetAddresses.third_party.weth_arbitrum
    chainlink_flags = constants.testnetAddresses.third_party.chainlink_flags if network.show_active() == 'arbitrum-rinkeby' else constants.mainnetAddresses.third_party.chainlink_flags

    initial_balance = admin.balance()

    # proxy admin contract
    proxy_admin = ProxyAdmin[-1]

    print(f"\n{network.show_active()}:\n")

    if vault_proxy_upgrade:
        utils.confirm(f"Confirm that the VaultCore's proxy address is {vault_proxy_address}")
        
        
        vault_proxy = Contract.from_abi(
            "VaultCore",
            vault_proxy_address,
            VaultCore.abi
        )
        
        # we only want to do these state changes in testnet
        utils.onlyTestnet(lambda: vault_test_state_change(vault_proxy, owner))

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
        utils.onlyTestnet(lambda: print(f"mintRedeemAllowed is still (should be false): {vault_proxy.mintRedeemAllowed()}\n"))

    if usds_proxy_upgrade:
        utils.confirm(f"Confirm that the USDs' proxy address is {usds_proxy_address}")
        utils.confirm(f"Confirm that the VaultCore's proxy address is {vault_proxy_address}")
        print("upgrade USDs contract:\n")
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

        # change vault address to verify state changes persist (only in testnet)
        utils.onlyTestnet(lambda: USDs_test_state_change(usds_proxy, owner))
        
        
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
        utils.onlyTestnet(lambda: print(f"vaultAddress is still (should be {vitalik_address}): {usds_proxy.vaultAddress()}\n"))

    if oracle_proxy_upgrade:
        utils.confirm(f"Confirm that the Oracle's proxy address is {oracle_proxy_address}")
        
        oracle_proxy = Contract.from_abi(
            "Oracle",
            oracle_proxy_address,
            Oracle.abi
        )

        # change vault address to verify state changes persist
        utils.onlyTestnet(lambda: oracle_test_state_change(oracle_proxy, owner))

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
        utils.onlyTestnet(lambda: print(f"VaultAddr is still (should be {vitalik_address}): {oracle_proxy.VaultAddr()}\n"))


    if vault_proxy_upgrade and oracle_proxy_upgrade:
        new_vault_proxy.updateOracleAddress(
            new_oracle_proxy.address,
            {'from': owner, 'gas_limit': 1000000000}
        )
        new_oracle_proxy.updateVaultAddress(
            new_vault_proxy.address,
            {'from': owner, 'gas_limit': 1000000000}
        )