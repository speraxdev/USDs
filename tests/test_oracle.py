import pytest
import json
import time
import brownie


def user(accounts):
    return accounts[9]

def test_update_USDs_Address(sperax,owner_l2):
    (   
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax
    tx=oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
        )
    print(tx.events)

def test_get_SPA_price(sperax,owner_l2):
    (   
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax


    tx=oracle_proxy.getSPAprice(
        {'from': owner_l2.address}
        )
    print(tx.events)
    