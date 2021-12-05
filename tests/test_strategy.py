import pytest
import json
import time
import brownie

def user(accounts):
    return accounts[9]

def test_deposit(sperax, weth, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    ) = sperax

    amount = int(9999)

    # deposit ETH into WETH contract to get WETH
    # short-circuit the real scenario by putting ETH
    # into vault_proxy contract instead of:
    # user -> vault_proxy -> strategy
    txn = weth.deposit(
        {'from': accounts[9].address, 'amount': amount}
    )
    # cast weth to its IERC20 interface in order to do the transfer
    weth_erc20 = brownie.interface.IERC20(weth.address)
    # transfer ETH to vault_proxy contract
    txn = weth_erc20.transfer(vault_proxy.address, amount, {'from': accounts[9]})
    assert txn.return_value == True
    # vault_proxy contract must have weth before it can deposit
    # it into the strategy contract
    txn = strategy_proxy.deposit(
        weth.address,
        amount,
        {'from': vault_proxy.address}
    )
    txn.events['Deposit']['_collateral'] == weth.address
    txn.events['Deposit']['_amount'] == amount