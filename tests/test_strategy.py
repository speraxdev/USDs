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
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    amount = int(9999)

    # deposit ETH into WETH contract to get WETH
    # short-circuit the real scenario by putting ETH
    # into strategy_proxy contract instead of:
    # user -> vault_proxy -> strategy_proxy
    txn = weth.deposit(
        {'from': accounts[9].address, 'amount': amount}
    )
    # cast weth to its IERC20 interface in order to do the transfer
    weth_erc20 = brownie.interface.IERC20(weth.address)
    # transfer weth to strategy_proxy contract
    txn = weth_erc20.transfer(strategy_proxy.address, amount, {'from': accounts[9]})
    assert txn.return_value == True
    # strategy_proxy contract must have weth before it can deposit
    # it into the Curve 3Pool
    txn = strategy_proxy.deposit(
        weth.address,
        amount,
        {'from': vault_proxy.address}
    )
    assert txn.events['Deposit']['_asset'] == weth.address
    assert txn.events['Deposit']['_amount'] == amount

def test_withdraw(sperax, weth, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    amount = int(1000000000)

    # deposit ETH into WETH contract to get WETH
    # short-circuit the real scenario by putting ETH
    # into strategy_proxy contract instead of:
    # user -> vault_proxy -> strategy_proxy
    txn = weth.deposit(
        {'from': accounts[9].address, 'amount': amount}
    )
    # cast weth to its IERC20 interface in order to do the transfer
    weth_erc20 = brownie.interface.IERC20(weth.address)
    # transfer weth to strategy_proxy contract
    txn = weth_erc20.transfer(strategy_proxy.address, amount, {'from': accounts[9]})
    assert txn.return_value == True
    # strategy_proxy contract must have weth before it can deposit
    # it into the Curve 3Pool
    txn = strategy_proxy.deposit(
        weth.address,
        amount,
        {'from': vault_proxy.address}
    )
    assert txn.events['Deposit']['_asset'] == weth.address
    assert txn.events['Deposit']['_amount'] == amount

    # withdraw 1/10 of the previous deposit
    txn = strategy_proxy.withdraw(
        accounts[8],
        weth.address,
        (amount/10),
        {'from': vault_proxy.address}
    )
