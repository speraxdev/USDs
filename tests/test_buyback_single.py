import pytest
import json
from brownie import  Wei, Contract, reverts
import time

def test_swap_succesful(sperax, weth, user_account):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback) = sperax

    balance1 = weth.balanceOf(user_account.address)

    allowance = spa.allowance(user_account.address, buyback.address)
    if(allowance <= 0):
        spa.approve(buyback.address, 10000000, {'from': user_account})

    buyback.swap(100000, {'from': vault_proxy.address})

    time.sleep(10)

    balance2 = weth.balanceOf(user_account.address)

    transferedBalance  = balance2 - balance1
    assert transferedBalance > 0

def test_swap_unsuccesful(sperax, weth, user_account):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback) = sperax



def test_swap_with_no_pool(buyback_single_sol_spa, user_account, weth, spa):
    failed = False
    allowance = spa.allowance(user_account.address, buyback_single_sol_spa.address)
    if(allowance <= 0):
        spa.approve(buyback_single_sol_spa.address, 10000000, {"from": user_account})

    try:
        buyback_single_sol_spa.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False



def test_swap_insufficient_balance(buyback_single, user_account_with_no_balance, weth, spa):
    failed = False
    allowance = spa.allowance(user_account_with_no_balance.address, buyback_single.address)
    try:
        if(allowance <= 0):
            spa.approve(buyback_single.address, 1000, {"from": user_account_with_no_balance})

        with reverts("Insufficient funds"):
            buyback_single.swap(100000, {"from": user_account_with_no_balance, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False
  

def test_swap_invalid_pool_fee(buyback_single_spa_weth_pf05, user_account, weth, spa):
    failed = False
    allowance = spa.allowance(user_account.address, buyback_single_spa_weth_pf05.address)
    if(allowance <= 0):
        spa.approve(buyback_single_spa_weth_pf05.address, 10000000, {"from": user_account})

    try:
        buyback_single_spa_weth_pf05.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False
