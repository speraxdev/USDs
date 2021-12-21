import pytest
import json
from brownie import  Wei, Contract, reverts
import time


@pytest.fixture(scope="module", autouse=True)
def buyback_single_no_pool(sperax, weth, BuybackSingle, owner_l2):
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

    return BuybackSingle.deploy(
        weth.address, # token1
        vault_proxy.address,
        {'from': owner_l2}
    )

def test_swap(sperax, mock_token2, owner_l2):
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
    print("spa mock1 balance", spa.balanceOf(owner_l2))

    spa.approve(vault_proxy.address, amount, {'from': owner_l2})
    spa.transfer(vault_proxy.address, amount, {'from': owner_l2})

    balance1 = mock_token2.balanceOf(vault_proxy.address)
    print("valut mock1 balance", spa.balanceOf(vault_proxy.address))

    spa.transfer(
        buyback.address, 
        amount, {'from': vault_proxy}
        )

    buyback.swap(
        spa.address, 
        amount, 
        {'from': vault_proxy}
        )

    time.sleep(10)

    balance2 = mock_token2.balanceOf(vault_proxy.address)
    transferedBalance  = balance2 - balance1
    assert transferedBalance  > 0


def test_swap_unsuccesful_call_not_vault(sperax, mock_token2, owner_l2):
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

    spa.transfer(
        buyback.address, 
        amount, 
        {'from': vault_proxy}
        )

    with reverts("caller is not the vault"):
        buyback.swap(
            spa.address, 
            amount, 
            {'from': owner_l2}
            )


def test_swap_unsuccesful_call_token_not_supported(sperax, mock_token2, weth, owner_l2):
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
    balance1 = spa.balanceOf(owner_l2.address)
    
    spa.approve(vault_proxy.address, amount, {'from': owner_l2})
    spa.transfer(vault_proxy.address, amount, {'from': owner_l2})
    spa.transfer(
        buyback.address, 
        amount, 
        {'from': vault_proxy}
        )

    with reverts("inputToken not supported"):
        buyback.swap(
            weth.address, 
            amount, 
            {'from': vault_proxy}
            )


def test_unsuccesful_test_swap_with_no_pool(buyback_single_no_pool, sperax, mock_token2, owner_l2):
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
    failed = False
    amount = 10000
    pool_fee = 3000


    buyback_single_no_pool.updateInputTokenInfo(
        mock_token2.address, 
        True, # supported
        pool_fee,
        {'from': owner_l2}
    )

    mock_token2.approve(vault_proxy.address, amount, {'from': owner_l2})
    mock_token2.transfer(vault_proxy.address, amount, {'from': owner_l2})

    try:
        buyback_single_no_pool.swap(
            mock_token2.address, 
            amount, 
            {"from": vault_proxy}
            )
        failed = True
    except Exception:
       failed = False
    assert failed == False