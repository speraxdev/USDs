import signal
import click
import importlib
import brownie
from .constants import (
    mainnetAddresses,
    testnetAddresses,
)
from .utils import (
    confirm,
    choice,
    onlyDevelopment,
    getAddressFromNetwork,
    getContractToUpgrade,
    signal_handler
)

accounts = brownie.accounts
network = brownie.network
Contract = brownie.Contract
VaultCore = brownie.VaultCore
ProxyAdmin = brownie.ProxyAdmin
SperaxTokenL2 = brownie.SperaxTokenL2
VaultCoreTools = brownie.VaultCoreTools
USDsL2 = brownie.USDsL2
Oracle = brownie.Oracle

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

    usds_proxy_address = getAddressFromNetwork(
        testnetAddresses.upgrade.USDs_l2_proxy, 
        mainnetAddresses.upgrade.USDs_l2_proxy
    )
    vault_tools_proxy_address = getAddressFromNetwork(
        testnetAddresses.upgrade.vault_core_tools_proxy,
        mainnetAddresses.upgrade.vault_core_tools_proxy
    )
    bancor_formula_address = getAddressFromNetwork(
        testnetAddresses.upgrade.bancor_formula_address,
        mainnetAddresses.upgrade.bancor_formula_address
    )

    vault_proxy_address = getAddressFromNetwork(
        testnetAddresses.upgrade.vault_core_proxy,
        mainnetAddresses.upgrade.vault_core_proxy
    )
    oracle_proxy_address = getAddressFromNetwork(
        testnetAddresses.upgrade.oracle_proxy,
        mainnetAddresses.upgrade.oracle_proxy
    )

    bancor_formula = "BancorFormula"
    vault_core_tools = "VaultCoreTools"
    vault_core = "VaultCore"
    USDs = "USDsL2"
    oracle = "Oracle"
    
    vault_tools_proxy_upgrade = choice(f"Do you wish to upgrade {vault_core_tools}?")
    vault_proxy_upgrade = choice(f"Do you wish to upgrade {vault_core}?")
    usds_proxy_upgrade = choice(f"Do you wish to upgrade {USDs}?")
    oracle_proxy_upgrade = choice(f"Do you wish to upgrade {oracle}?")
    # TODO: add vault tools upgrade flow
  
    # initialize third party addresses
    chainlink_eth_price_feed = getAddressFromNetwork(
        testnetAddresses.third_party.chainlink_eth_price_feed,
        mainnetAddresses.third_party.chainlink_eth_price_feed
    )
    weth_arbitrum = getAddressFromNetwork(
        testnetAddresses.third_party.weth_arbitrum,
        mainnetAddresses.third_party.weth_arbitrum
    )
    chainlink_flags = getAddressFromNetwork(
        testnetAddresses.third_party.chainlink_flags,
        mainnetAddresses.third_party.chainlink_flags
    )

    initial_balance = admin.balance()

    # proxy admin contract
    proxy_admin = ProxyAdmin[-1]

    print(f"\n{network.show_active()}:\n")

    if vault_tools_proxy_upgrade:
        confirm(f"Confirm that the {vault_core_tools}' proxy address is {vault_tools_proxy_address}")
        confirm(f"Confirm that the {bancor_formula} contract's address is {bancor_formula_address}")
        vault_tools_proxy = Contract.from_abi(
            vault_core_tools,
            vault_tools_proxy_address,
            VaultCoreTools.abi
        )

        version_contract_name, version_contract =  getContractToUpgrade(vault_core_tools)

        # Note: we cannot *easily* test state changes because there are no setters in VaultCoreTools
        # the version check and checks in other functions should suffice

        print(f"upgrade {vault_core} contract:\n")
        new_vault_tools = version_contract.deploy(
            {'from': owner, 'gas_limit': 1000000000}
        )

        proxy_admin.upgrade(
            vault_tools_proxy.address,
            new_vault_tools.address,
            {'from': admin, 'gas_limit': 1000000000}
        )

        new_vault_tools.initialize(bancor_formula_address, {'from': owner})

        new_vault_tools_proxy = Contract.from_abi(
            version_contract_name,
            vault_tools_proxy.address,
            version_contract.abi
        )

        print(f"original {vault_core_tools} proxy address: {vault_tools_proxy.address}")
        print(f"upgraded {vault_core_tools} proxy address: {new_vault_tools_proxy.address}")
        print(f"{vault_core_tools} version: {new_vault_tools_proxy.version()}")

    if vault_proxy_upgrade:
        confirm(f"Confirm that the {vault_core}'s proxy address is {vault_proxy_address}")
        
        vault_proxy = Contract.from_abi(
            vault_core,
            vault_proxy_address,
            VaultCore.abi
        )
        
        version_contract_name, version_contract =  getContractToUpgrade(vault_core)
        
        # we only want to do these state changes in testnet
        onlyDevelopment(lambda: vault_test_state_change(vault_proxy, owner))
       
        print(f"upgrade {vault_core} contract:\n")
        new_vault = version_contract.deploy(
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
            version_contract_name,
            vault_proxy.address,
            version_contract.abi
        )
        print(f"original {vault_core} proxy address: {vault_proxy.address}")
        print(f"upgraded {vault_core} proxy address: {new_vault_proxy.address}")
        print(f"{vault_core} version: {new_vault_proxy.version()}")
        onlyDevelopment(lambda: print(f"mintRedeemAllowed is still (should be false): {vault_proxy.mintRedeemAllowed()}\n"))

    if usds_proxy_upgrade:
        confirm(f"Confirm that the {USDs}' proxy address is {usds_proxy_address}")
        confirm(f"Confirm that the {vault_core}'s proxy address is {vault_proxy_address}")
        print(f"upgrade {USDs} contract:\n")
        vault_proxy = Contract.from_abi(
            vault_core,
            vault_proxy_address,
            VaultCore.abi
        )
   
        usds_proxy = Contract.from_abi(
            USDs,
            usds_proxy_address,
            USDsL2.abi
        )
        
        version_contract_name, version_contract =  getContractToUpgrade(USDs)

        # change vault address to verify state changes persist (only in testnet)
        onlyDevelopment(lambda: USDs_test_state_change(usds_proxy, owner))
        
        new_usds = version_contract.deploy(
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
            version_contract_name,
            usds_proxy.address,
            version_contract.abi
        )
        print(f"original {USDs} proxy address: {usds_proxy.address}")
        print(f"upgraded {USDs} proxy address: {new_usds_proxy.address}")
        print(f"{USDs} version: {new_usds_proxy.version()}")
        onlyDevelopment(lambda: print(f"vaultAddress is still (should be {vitalik_address}): {usds_proxy.vaultAddress()}\n"))

    if oracle_proxy_upgrade:
        confirm(f"Confirm that the {oracle}'s proxy address is {oracle_proxy_address}")
        
        oracle_proxy = Contract.from_abi(
            oracle,
            oracle_proxy_address,
            Oracle.abi
        )

        version_contract_name, version_contract =  getContractToUpgrade(oracle)
        # change vault address to verify state changes persist
        onlyDevelopment(lambda: oracle_test_state_change(oracle_proxy, owner))

        print(f"upgrade {oracle} contract:\n")
        new_oracle = version_contract.deploy(
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
            version_contract_name,
            oracle_proxy.address,
            version_contract.abi
        )
        print(f"original {oracle} proxy address: {oracle_proxy.address}")
        print(f"upgraded {oracle} proxy address: {new_oracle_proxy.address}")
        print(f"{oracle}  version: {new_oracle_proxy.version()}")
        onlyDevelopment(lambda: print(f"VaultAddr is still (should be {vitalik_address}): {oracle_proxy.VaultAddr()}\n"))


    if vault_proxy_upgrade and oracle_proxy_upgrade:
        new_vault_proxy.updateOracleAddress(
            new_oracle_proxy.address,
            {'from': owner, 'gas_limit': 1000000000}
        )
        new_oracle_proxy.updateVaultAddress(
            new_vault_proxy.address,
            {'from': owner, 'gas_limit': 1000000000}
        )