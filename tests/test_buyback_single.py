import pytest
import eth_utils
import time


def test_swap_successful(buyback_single_spa_weth, user_account, weth_token, spa_token):
    balance1 = weth_token.balanceOf(user_account.address)

    allowance = spa_token.allowance(user_account.address, buyback_single_spa_weth.address)
    if(allowance <= 0):
        spa_token.approve(buyback_single_spa_weth.address, 10000000, {"from": user_account})

    buyback_single_spa_weth.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})

    time.sleep(10)

    balance2 = weth_token.balanceOf(user_account.address)
    transferedBalance  = balance2 - balance1
    assert transferedBalance > 0