import pytest
import json
import os
from brownie import  Wei, accounts, BuybackMultihop, Contract, reverts
import time



@pytest.fixture(scope="module")
def user_account_with_no_balance():
    EMPTY_WALLET_PRIVATE_KEY = os.environ.get('EMPTY_WALLET_PRIVATE_KEY')
    return accounts.add(EMPTY_WALLET_PRIVATE_KEY)

@pytest.fixture(scope="module")
def invaild_toke():
    INVALID_TOKEN = "0x07de306FF27a2B630B1141956844eB1552B956B6"
    return INVALID_TOKEN


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


def test_swap_with_no_pool(sperax, user_account, weth, usds, solana):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax

    failed = False
    buyback_multihop.updateInputTokenInfo(solana.address, False, weth.address, 3000, 3000)

    allowance = solana.allowance(user_account.address, buyback_multihop.address)
    if(allowance <= 0):
        solana.approve(buyback_multihop.address, 10000000, {"from": user_account})

    try:
        buyback_multihop.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
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
  

def test_swap_invalid_pool_fee(sperax, user_account, weth, usds):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    failed = False
    buyback_multihop.updateInputTokenInfo(usds.address, False, weth.address, 50000, 50000)
    allowance = usds.allowance(user_account.address, buyback_multihop.address)
    if(allowance <= 0):
        usds.approve(buyback_multihop.address, 10000000, {"from": user_account})

    try:
        buyback_multihop.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False

def test_swap_invalid_token(sperax, user_account, weth, inavalid_token):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop) = sperax
    failed = False
    buyback_multihop.updateInputTokenInfo(inavalid_token.address, False, weth.address, 50000, 50000)
    allowance = inavalid_token.allowance(user_account.address, inavalid_token.address)
    if(allowance <= 0):
        inavalid_token.approve(inavalid_token.address, 10000000, {"from": user_account})

    try:
        inavalid_token.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False
