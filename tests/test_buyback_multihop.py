import pytest
import json
import os
from brownie import  Wei, accounts, BuybackMultihop, Contract, reverts
import time



def test_swap_successful(sperax, user_account, weth, usds):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax

    balance1 = weth.balanceOf(user_account.address)

    allowance = usds.allowance(user_account.address, buyback_multihop.address)
    if(allowance <= 0):
        usds.approve(buyback_multihop.address, 10000000, {"from": user_account})

    buyback_multihop.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})

    time.sleep(10)

    balance2 = weth.balanceOf(user_account.address)
    transferedBalance  = balance2 - balance1
    assert transferedBalance > 0


def test_swap_with_no_pool(buyback_multihop_usdt_sol_weth, user_account, weth, usds):
    failed = False
    allowance = usds.allowance(user_account.address, buyback_multihop_usdt_sol_weth.address)
    if(allowance <= 0):
        usds.approve(buyback_multihop_usdt_sol_weth.address, 10000000, {"from": user_account})

    try:
        buyback_multihop_usdt_sol_weth.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False



def test_swap_insufficient_balance(sperax, user_account_with_no_balance, weth, usds):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    failed = False
    allowance = usds.allowance(user_account_with_no_balance.address, buyback_multihop.address)
    try:
        if(allowance <= 0):
            usds.approve(buyback_multihop.address, 1000, {"from": user_account_with_no_balance})

        with reverts("Insufficient funds"):
            buyback_multihop.swap(100000, {"from": user_account_with_no_balance, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False
  

def test_swap_invalid_pool_fee(buyback_multihop_usdt_spa_weth_pf50, user_account, weth_token, usds):
    failed = False
    allowance = usds.allowance(user_account.address, buyback_multihop_usdt_spa_weth_pf50.address)
    if(allowance <= 0):
        usds.approve(buyback_multihop_usdt_spa_weth_pf50.address, 10000000, {"from": user_account})

    try:
        buyback_multihop_usdt_spa_weth_pf50.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False

def test_swap_invalid_token(buyback_multihop_usdt_invalid_token_weth, user_account, weth_token, usds):
    failed = False
    allowance = usds.allowance(user_account.address, buyback_multihop_usdt_invalid_token_weth.address)
    if(allowance <= 0):
        usds.approve(buyback_multihop_usdt_invalid_token_weth.address, 10000000, {"from": user_account})

    try:
        buyback_multihop_usdt_invalid_token_weth.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False