import pytest
from brownie import  Wei, Contract, reverts
from brownie.test import given, strategy
import time

@pytest.fixture(scope="module", autouse=True)
def buyback_single_no_pool(sperax, BuybackSingle, owner_l2):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    return BuybackSingle.deploy(
        spa.address, # token1
        vault_proxy.address,
        {'from': owner_l2}
    )


def test_swap(sperax, mock_token2, mock_token1, owner_l2):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    amount = 10000
    balance1 = mock_token1.balanceOf(vault_proxy.address)

    print("valut mock1 balance", mock_token2.balanceOf(vault_proxy.address))

    mock_token2.transfer(
        buyback.address, 
        amount, {'from': vault_proxy}
        )

    buyback.swap(
        mock_token2.address, 
        amount, 
        {'from': vault_proxy}
        )

    time.sleep(10)

    balance2 = mock_token1.balanceOf(vault_proxy.address)
    transferedBalance  = balance2 - balance1
    assert transferedBalance  > 0


def test_swap_unsuccesful_call_not_vault(sperax, mock_token2, mock_token1, owner_l2):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    amount = 10000
    balance1 = mock_token1.balanceOf(owner_l2.address)
    
    mock_token2.transfer(
        buyback.address, 
        amount, 
        {'from': vault_proxy}
        )

    with reverts("caller is not the vault"):
        buyback.swap(
            mock_token2.address, 
            amount, 
            {'from': owner_l2}
            )


def test_swap_unsuccesful_call_token_not_supported(sperax, mock_token2, mock_token1, owner_l2):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    amount = 10000
    balance1 = mock_token1.balanceOf(owner_l2.address)
    
    mock_token2.transfer(
        buyback.address, 
        amount, 
        {'from': vault_proxy}
        )

    with reverts("inputToken not supported"):
        buyback.swap(
            spa.address, 
            amount, 
            {'from': vault_proxy}
            )


def test_unsuccesful_swap_with_invalid_pool_fee(sperax,  mock_token2, owner_l2):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    failed = False
    amount = 10000
    pool_fee = 50000

    buyback.updateInputTokenInfo(
        mock_token2.address, 
        False, pool_fee, 
        {'from': owner_l2}
        )

    mock_token2.transfer(
        buyback.address, amount, 
        {'from': vault_proxy}
        )
    try:
        buyback.swap(
            mock_token2.address, 
            amount, 
            {"from": vault_proxy}
            )
        failed = True
    except Exception:
       failed = False
    assert failed == False


def test_unsuccesful_test_swap_with_no_pool(buyback_single_no_pool, sperax, mock_token2, owner_l2):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    failed = False
    amount = 10000
    pool_fee = 3000
    buyback_single_no_pool.updateInputTokenInfo(
        mock_token2.address, 
        True, # supported
        pool_fee,
        {'from': owner_l2}
    )

    mock_token2.transfer(buyback.address, amount, {'from': vault_proxy})
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
