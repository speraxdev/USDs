import pytest
from brownie import  Wei, Contract, reverts, interface
from brownie.test import given, strategy
import time

def test_swap(sperax, owner_l2, usdc):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategies,
        buybacks,
        bancor
    ) = sperax

    (
        single_hop_buyback,
        two_hops_buyback,
        three_hops_buyback
    ) = buybacks

    amount = 1000000
    balance1 = usds_proxy.balanceOf(vault_proxy.address)

    usdc.approve(vault_proxy.address, amount, {'from': owner_l2})
    usdc.transfer(vault_proxy.address, amount, {'from': owner_l2})

    usdc.transfer(
        single_hop_buyback.address,
        amount, {'from': vault_proxy}
    )

    single_hop_buyback.swap(
        usdc.address,
        amount,
        {'from': vault_proxy}
    )

    time.sleep(10)

    balance2 = usds_proxy.balanceOf(vault_proxy.address)
    transferedBalance  = balance2 - balance1
    assert transferedBalance  > 0


def test_swap_unsuccesful_call_not_vault(sperax, owner_l2, usdc):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategies,
        buybacks,
        bancor
    ) = sperax
    (
        single_hop_buyback,
        two_hops_buyback,
        three_hops_buyback
    ) = buybacks

    amount = 10000


    with reverts("caller is not the vault"):
        single_hop_buyback.swap(
            usdc.address,
            amount,
            {'from': owner_l2}
            )


def test_swap_unsuccesful_call_token_not_supported(sperax):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategies,
        buybacks,
        bancor
    ) = sperax
    (
        single_hop_buyback,
        two_hops_buyback,
        three_hops_buyback
    ) = buybacks

    amount = 10000
    with reverts("inputToken not supported"):
        single_hop_buyback.swap(
            spa.address,
            amount,
            {'from': vault_proxy}
            )