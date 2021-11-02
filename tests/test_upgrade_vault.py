#!/usr/bin/python3
import pytest
import brownie

#
# DON'T USE accounts[0-3]. 0-3 ARE RESERVED BY conftest.py
#

def test_upgrade_vault(sperax, VaultCoreV2, Contract, admin, owner_l2, accounts):
    (proxy_admin, spa, usds2, vault_core_tools, vault_proxy, oracle_proxy) = sperax
    print("upgrade Vault contract:\n")
    new_vault = VaultCoreV2.deploy(
        {'from': owner_l2}
    )

    with brownie.reverts():
        proxy_admin.upgrade(
            vault_proxy.address,
            new_vault.address,
            {'from': owner_l2}
        )

    txn = proxy_admin.upgrade(
        vault_proxy.address,
        new_vault.address,
        {'from': admin}
    )

    fee_vault = accounts[5]
    new_vault.initialize(
        spa.address,
        vault_core_tools.address,
        fee_vault,
        {'from': owner_l2}
    )

    new_vault_proxy = Contract.from_abi(
        "VaultCoreV2",
        vault_proxy.address,
        VaultCoreV2.abi
    )

    print(f"Vault v2 proxy address: {new_vault_proxy.address}")
    new_vault_proxy.version() == "Vault v.2"

    new_vault_proxy.updateUSDsAddress(
        usds2.address,
        {'from': owner_l2}
    )
    new_vault_proxy.updateOracleAddress(
        oracle_proxy.address,
        {'from': owner_l2}
    )

    # admin cannot call base contract functions
    with brownie.reverts():
        new_vault_proxy.updateUSDsAddress(
            usds2.address,
            {'from': admin}
        )
        new_vault_proxy.updateOracleAddress(
            oracle_proxy.address,
            {'from': admin}
        )