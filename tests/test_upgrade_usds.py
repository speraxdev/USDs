#!/usr/bin/python3
import pytest
import brownie

#
# DON'T USE accounts[0-4]. 0-4 ARE RESERVED BY conftest.py
#

def test_upgrade_usds(sperax, USDsL2V2, proxy_admin, Contract, admin, owner_l2, accounts):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    ) = sperax

    print("upgrade USDsL2 contract:\n")
    # test case requires duplicating the contract, USDsL2.sol, renamed as USDsL2V2.sol
    new_usds = USDsL2V2.deploy(
        {'from': owner_l2}
    )

    # test against wrong owner
    with brownie.reverts():
        proxy_admin.upgrade(
            usds_proxy.address,
            new_usds.address,
            {'from': owner_l2}
        )

    txn = proxy_admin.upgrade(
        usds_proxy.address,
        new_usds.address,
        {'from': admin}
    )

    new_usds.initialize(
        usds_proxy.name(),
        usds_proxy.symbol(),
        vault_proxy.address,
        usds_proxy.l2Gateway(),
        usds_proxy.l1Address(),
        {'from': owner_l2}
    )

    new_usds_proxy = Contract.from_abi(
        "USDsL2V2",
        usds_proxy.address,
        USDsL2V2.abi
    )

    print(f"USDsL2 v2 proxy address: {new_usds_proxy.address}")
    # requires duplicating USDsL2.sol contract. The duplicate contract should
    # be called USDsL2V2.sol. This version 2 contract must expose a new function 
    # called version() that returns the string "USDsL2 v.2"
    assert new_usds_proxy.version() == "USDsL2 v.2"