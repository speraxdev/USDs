import pytest
import json
from brownie import  Wei, Contract, reverts
import time

def test_swap_succesful(sperax, weth_token, user_account):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback) = sperax
    erc20_weth = weth_token

    balance1 = erc20_weth.balanceOf(user_account.address)

    allowance = spa.allowance(user_account.address, buyback.address)
    if(allowance <= 0):
        spa.approve(buyback.address, 10000000, {"from": user_account})

    buyback.swap(100000, {"from": user_account})

    time.sleep(10)

    balance2 = erc20_weth.balanceOf(user_account.address)

    transferedBalance  = balance2 - balance1
    assert transferedBalance > 0

def test_swap_unsuccesful(sperax, weth_token, user_account):
    (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback) = sperax
    erc20_weth = weth_token
