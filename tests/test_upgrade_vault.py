#!/usr/bin/python3
import pytest
import brownie

#
# DON'T USE accounts[0-3]. 0-3 ARE RESERVED BY conftest.py
#

def test_upgrade_vault(sperax, VaultCoreV2, Contract, admin, owner_l2, accounts):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback) = sperax

    print("upgrade Vault contract:\n")
    # test case requires duplicating the contract, VaulCore.sol, renamed as VaultCoreV2.sol
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
    # requires duplicating VaultCore.sol contract. The duplicate contract should
    # be called VaultCoreV2.sol. This version 2 contract must expose a new function 
    # called version() that returns the string "Vault v.2"
    assert new_vault_proxy.version() == "Vault v.2"

    new_vault_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )
    new_vault_proxy.updateOracleAddress(
        oracle_proxy.address,
        {'from': owner_l2}
    )

    # admin cannot call base contract functions
    with brownie.reverts():
        new_vault_proxy.updateUSDsAddress(
            usds_proxy.address,
            {'from': admin}
        )
        new_vault_proxy.updateOracleAddress(
            oracle_proxy.address,
            {'from': admin}
        )

    # configure collateral 
    collaterals = [
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', # USDC
        '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', # USDT
        '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1', # DAI
        '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f', # WBTC
    ]
    # equivalent to address(0) in solidity
    zero_address = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    for collateral in collaterals:
        txn = vault_proxy.addCollateral(
            collateral, # address of: USDC, USDT, DAI or WBTC
            zero_address, # _defaultStrategyAddr: CURVE, AAVE, etc
            False, # _allocationAllowed
            0, # _allocatePercentage
            zero_address, # _buyBackAddr
            False, # _rebaseAllowed
            {'from': owner_l2}
        )