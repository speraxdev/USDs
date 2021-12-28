#!/usr/bin/python3
import pytest
import brownie
from brownie.test import given, strategy

#
# DON'T USE accounts[0-4]. 0-4 ARE RESERVED BY conftest.py
#

def test_rebase(sperax, accounts):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    first_user = accounts[5]
    contract_holder = oracle_proxy.address
    second_user = accounts[6]
    # mint stablecoin
    amount = 10000000000000
    slippage = 10
    usds_proxy.mint(first_user, amount, {'from': vault_proxy.address})
    usds_proxy.mint(oracle_proxy.address, amount, {'from': vault_proxy.address})
    assert usds_proxy.balanceOf(first_user) == amount
    assert usds_proxy.totalSupply() == amount*2

    # rebase when one user and one contract
    print('double totalSupply:')
    print('first_user\'s balance should increase')
    print('contract_holder\'s balance should stay roughly the same')
    contract_holder_balance = usds_proxy.balanceOf(contract_holder)
    usds_proxy.changeSupply(usds_proxy.totalSupply()*2, {'from': vault_proxy.address})
    assert usds_proxy.totalSupply() == amount*4
    assert usds_proxy.balanceOf(contract_holder) > contract_holder_balance-slippage
    assert usds_proxy.balanceOf(contract_holder) < contract_holder_balance+slippage
    assert usds_proxy.balanceOf(first_user) == usds_proxy.totalSupply() - usds_proxy.balanceOf(contract_holder)

    # rebase when two users one contractm second user opt out
    print('mint for second_user')
    usds_proxy.mint(second_user, amount, {'from': vault_proxy.address})
    assert usds_proxy.balanceOf(second_user) > amount-slippage
    assert usds_proxy.balanceOf(second_user) < amount+slippage
    first_user_balance = usds_proxy.balanceOf(first_user)
    contract_holder_balance = usds_proxy.balanceOf(contract_holder)
    second_user_balance = usds_proxy.balanceOf(contract_holder)
    usds_proxy.rebaseOptOut(second_user,  {'from': usds_proxy.owner()})
    usds_proxy.changeSupply(usds_proxy.totalSupply()*2, {'from': vault_proxy.address})
    assert usds_proxy.balanceOf(first_user) > first_user_balance+10
    assert usds_proxy.balanceOf(contract_holder) > contract_holder_balance-slippage
    assert usds_proxy.balanceOf(contract_holder) < contract_holder_balance+slippage
    assert usds_proxy.balanceOf(second_user) > second_user_balance-slippage
    assert usds_proxy.balanceOf(second_user) < second_user_balance+slippage
    contract_holder_balance = usds_proxy.balanceOf(contract_holder)
    usds_proxy.rebaseOptIn(contract_holder,  {'from': usds_proxy.owner()})
    usds_proxy.changeSupply(usds_proxy.totalSupply()*2, {'from': vault_proxy.address})
    assert usds_proxy.balanceOf(contract_holder) > contract_holder_balance+slippage



@given(amount=strategy('uint256', min_value=1, max_value=2**128-1))
def test_valid_mint(sperax, accounts, amount):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    print('amount: ', amount)
    first_user = accounts[5]
    approver = accounts[6]
    second_user = accounts[7]
    failed_user = accounts[8]
    third_user = accounts[9]
    # mint stablecoin
    usds_proxy.mint(first_user, amount, {'from': vault_proxy.address})
    assert usds_proxy.balanceOf(first_user) == amount
    assert usds_proxy.totalSupply() == amount

    # approve transfer
    usds_proxy.approve(approver, amount, {'from': first_user})
    txn = usds_proxy.transferFrom(first_user, second_user, amount, {'from': approver})
    assert txn.events['Transfer']['from'] == first_user
    assert txn.events['Transfer']['to'] == second_user
    assert txn.events['Transfer']['value'] == amount
    assert usds_proxy.balanceOf(second_user) == amount
    assert usds_proxy.totalSupply() == amount

    # first_user no longer owns the tokens. try to transfer
    with brownie.reverts():
        usds_proxy.transfer(failed_user, amount, {'from': first_user})

    # new user transfers stablecoin
    usds_proxy.transfer(third_user, amount, {'from': second_user})
    assert usds_proxy.balanceOf(third_user) == amount
    assert usds_proxy.totalSupply() == amount

    # amount of stablecoins to burn
    amount_to_burn = amount - (amount // 2)
    print('number of tokens to burn: ', amount_to_burn)
    # stablecoin user cannot burn their own tokens
    with brownie.reverts():
        usds_proxy.burn(third_user, amount_to_burn, {'from': second_user})

    # new user stablecoins can only be burned by vault
    usds_proxy.burn(third_user, amount_to_burn, {'from': vault_proxy.address})
    assert usds_proxy.totalSupply() == amount - amount_to_burn
