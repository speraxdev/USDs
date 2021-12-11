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
   

def test_deposit_invalid_amount(sperax, weth):
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
        buyback,
        buyback_multihop
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
        buyback,
        buyback_multihop
    ) = sperax
    amount = int(1000000000)
    # testing the validity of recipient.
    zero_address = "0x0000000000000000000000000000000000000000"
    with brownie.reverts("Invalid recipient"):
        txn = strategy_proxy.withdraw(
            zero_address, 
            weth.address,
             (amount),
            {'from': vault_proxy.address}
        )

    txn = weth.deposit(
        {'from': accounts[9].address, 'amount': amount}
    )

    weth_erc20 = brownie.interface.IERC20(weth.address)
    txn = weth_erc20.transfer(strategy_proxy.address, amount, {'from': accounts[9]})
    assert txn.return_value == True
    txn = strategy_proxy.deposit(
        weth.address,
        amount,
        {'from': vault_proxy.address}
    )
    assert txn.events['Deposit']['_asset'] == weth.address
    assert txn.events['Deposit']['_amount'] == amount

    # withdraw 1/10 of the previous deposit
    txn = strategy_proxy.withdraw(
        accounts[9],
        weth.address,
        (amount/10),
        {'from': vault_proxy.address}
    )
    # assert txn.events['Withdrawal']['_asset'] == weth.address
    # assert txn.events['Withdrawal']['_amount']==amount/10

def test_withdraw_invalid_assets(sperax, mock_token2, accounts):
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

    amount = int(9999)

    with brownie.reverts("Invalid 3pool asset"):
        txn = strategy_proxy.withdraw(
            accounts[8],
            mock_token2.address,
            (amount/10),
            {'from': vault_proxy.address})



def test_withdraw_invalid_amount(sperax, weth, accounts):
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

    amount = int(0)

    with brownie.reverts("Invalid amount"):
        txn = strategy_proxy.withdraw(
            accounts[8],
            weth.address,
            (amount),
            {'from': vault_proxy.address}
        )

def test_withdraw_interest(sperax, weth, accounts):
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
    # testing the validity of the recepient
    zero_address = "0x0000000000000000000000000000000000000000"
   
    with brownie.reverts("Invalid recipient"):
          txn = strategy_proxy.withdrawInterest(
            zero_address, 
            weth.address,
            {'from': vault_proxy.address}
        )

    txn = weth.deposit(
        {'from': accounts[9].address, 'amount': amount}
    )

    weth_erc20 = brownie.interface.IERC20(weth.address)
    txn = weth_erc20.transfer(strategy_proxy.address, amount, {'from': accounts[9]})
    assert txn.return_value == True
    txn = strategy_proxy.deposit(
        weth.address,
        amount,
        {'from': vault_proxy.address}
    )
    assert txn.events['Deposit']['_asset'] == weth.address
    assert txn.events['Deposit']['_amount'] == amount
    print ("Amount Deposited: ", amount)

    # withdraw 1/10 of the previous deposit
    txn = strategy_proxy.withdraw(
        accounts[9],
        weth.address,
        (amount/10),
        {'from': vault_proxy.address}
    )
    interest = strategy_proxy.checkInterestEarned(weth.address, {'from': vault_proxy.address})

    assert txn.events['Withdrawal']['_asset'] == weth.address
    print("Amount Received: ",txn.events['Withdrawal']['_amount'])

    if(interest > 0):
        txn = strategy_proxy.withdrawInterest(
            accounts[8],
            weth.address,
            {'from': vault_proxy.address}
        )


def test_check_balance(sperax, weth):
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

    balance = strategy_proxy.checkBalance(weth, {'from': vault_proxy.address})

    assert  balance ==0

    

def test_withdraw_to_vault_amount(sperax, weth,owner_l2):
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

    amount = int(0)

    with brownie.reverts("Invalid amount"):
          txn = strategy_proxy.withdrawToVault(
            weth.address,
            (amount),
            {'from': owner_l2.address}
        )


def test_withdraw_to_vault_invalid_assets(sperax, mock_token2, owner_l2):
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

    amount = int(9999)

    with brownie.reverts("Invalid 3pool asset"):
        txn = strategy_proxy.withdrawToVault(
            mock_token2.address,
            (amount/10),
            {'from': owner_l2.address})

