import pytest
from brownie import  Wei, Contract, reverts, interface
from brownie.test import given, strategy
import time

def test_swap(sperax, owner_l2, weth):
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
        two_hops_buyback, 
        three_hops_buyback
    ) = buybacks
    
    amount = 10000
    balance1 = usds_proxy.balanceOf(vault_proxy.address)
    weth_erc20 = interface.IERC20(weth.address)
    weth_erc20.approve(vault_proxy.address, amount, {'from': owner_l2})
    weth_erc20.transfer(vault_proxy.address, amount, {'from': owner_l2})

    weth_erc20.transfer(
        two_hops_buyback.address, 
        amount, {'from': vault_proxy}
    )

    two_hops_buyback.swap(
        weth_erc20.address, 
        amount, 
        {'from': vault_proxy}
    )

    time.sleep(10)

    balance2 = usds_proxy.balanceOf(vault_proxy.address)
    transferedBalance  = balance2 - balance1
    assert transferedBalance  > 0


def test_swap_unsuccesful_call_not_vault(sperax, owner_l2, weth):
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
        two_hops_buyback, 
        three_hops_buyback
    ) = buybacks

    amount = 10000

    weth_erc20 = interface.IERC20(weth.address)

    with reverts("Caller is not the Vault"):
        two_hops_buyback.swap(
            weth_erc20.address, 
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
        two_hops_buyback, 
        three_hops_buyback
    ) = buybacks

    amount = 10000
    with reverts("inputToken not supported"):
        two_hops_buyback.swap(
            spa.address, 
            amount, 
            {'from': vault_proxy}
            )