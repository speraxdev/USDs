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



def test_deposit_invalid_amount(sperax, weth, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    ) = sperax

    amount = int(0)

    with brownie.reverts("Must deposit something"):
        txn = strategy_proxy.deposit(
            weth.address,
            amount,
            {'from': vault_proxy.address}
        )


def test_deposit_invalid_assets(sperax, weth, accounts, mock_token2):
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

    with brownie.reverts("Invalid 3pool asset"):
        txn = strategy_proxy.deposit(
            mock_token2.address,
            amount,
            {'from': vault_proxy.address}
        )

def test_withdraw(sperax, weth, accounts):

    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    ) = sperax

    amount = int(999)

    strategy_proxy.withdraw(
        accounts[9],
        weth.address,
        amount,
        {'from': vault_proxy.address}
    )

def test_withdraw_invalid_recipient(sperax, weth, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    ) = sperax
    amount  = int(999)
    invalid_address = ""

    with brownie.reverts('Invalid recipient'):
        strategy_proxy.withdraw(
        invalid_address,
        weth.address,
        amount,
        {'from': vault_proxy.address}
    )


def test_withdraw_invalid_amount(sperax, weth, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    ) = sperax
    amount  = int(999)

    with brownie.reverts('Invalid amount'):
        strategy_proxy.withdraw(
        accounts[9],
        weth.address,
        amount,
        {'from': vault_proxy.address}
    )
