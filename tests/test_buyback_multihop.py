import pytest
import json
from brownie import  Wei, Contract, reverts
import time

def test_swap_succesful(sperax, mock_token2, mock_token3, owner_l2):
    (   spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
        
    ) = sperax

    amount = 10000
    spa.approve(vault_proxy.address, amount, {'from': owner_l2})
    spa.transfer(vault_proxy.address, amount, {'from': owner_l2})
    
    balance1 = mock_token3.balanceOf(vault_proxy.address)

    spa.transfer(
        buyback_multihop.address, 
        amount, {'from': vault_proxy}
        )

    buyback_multihop.swap(
        spa.address, 
        amount, 
        {'from': vault_proxy}
        )

    time.sleep(10)

    balance2 = mock_token3.balanceOf(vault_proxy.address)
    transferedBalance  = balance2 - balance1
    assert transferedBalance  > 0

def test_swap_unsuccesful_call_not_vault(sperax, mock_token2, mock_token3, owner_l2):
    (   spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax

    amount = 10000
    balance1 = mock_token3.balanceOf(owner_l2.address)

    spa.approve(vault_proxy.address, amount, {'from': owner_l2})
    spa.transfer(vault_proxy.address, amount, {'from': owner_l2})

    spa.transfer(
        buyback_multihop.address, 
        amount, 
        {'from': vault_proxy}
        )

    with reverts("Caller is not the Vault"):
        buyback_multihop.swap(
            spa.address, 
            amount, 
            {'from': owner_l2}
            )

def test_swap_unsuccesful_call_token_not_supported(sperax, weth, mock_token3, owner_l2):
    (   spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax

    amount = 10000
    balance1 = mock_token3.balanceOf(owner_l2.address)

    spa.approve(vault_proxy.address, amount, {'from': owner_l2})
    spa.transfer(vault_proxy.address, amount, {'from': owner_l2})

    spa.transfer(
        buyback_multihop.address, 
        amount, 
        {'from': vault_proxy}
        )

    with reverts("inputToken not supported"):
        buyback_multihop.swap(
            weth.address, 
            amount, 
            {'from': vault_proxy}
            )
