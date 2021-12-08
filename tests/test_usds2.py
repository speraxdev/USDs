#!/usr/bin/python3
import pytest
import brownie
from brownie.test import given, strategy

#
# DON'T USE accounts[0-4]. 0-4 ARE RESERVED BY conftest.py
#

@given(amount=strategy('uint256', min_value=1, max_value=2**256-1))
def test_valid_mint(sperax, accounts, amount):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    ) = sperax

    print('amount: ', amount)
    first_owner = accounts[5]
    approver = accounts[6]
    second_owner = accounts[7]
    failed_owner = accounts[8]
    third_owner = accounts[9]
    # mint stablecoin
    usds_proxy.mint(first_owner, amount, {'from': vault_proxy.address})
    assert usds_proxy.balanceOf(first_owner) == amount
    assert usds_proxy.totalSupply() == amount

    # approve transfer 
    usds_proxy.approve(approver, amount, {'from': first_owner})
    txn = usds_proxy.transferFrom(first_owner, second_owner, amount, {'from': approver})
    assert txn.events['Transfer']['from'] == first_owner 
    assert txn.events['Transfer']['to'] == second_owner
    assert txn.events['Transfer']['value'] == amount
    assert usds_proxy.balanceOf(second_owner) == amount
    assert usds_proxy.totalSupply() == amount

    # first_owner no longer owns the tokens. try to transfer
    with brownie.reverts():
        usds_proxy.transfer(failed_owner, amount, {'from': first_owner})
    
    # new owner transfers stablecoin
    usds_proxy.transfer(third_owner, amount, {'from': second_owner})
    assert usds_proxy.balanceOf(third_owner) == amount
    assert usds_proxy.totalSupply() == amount

    # amount of stablecoins to burn
    amount_to_burn = amount - (amount // 2)
    print('number of tokens to burn: ', amount_to_burn)
    # stablecoin owner cannot burn their own tokens
    with brownie.reverts():
        usds_proxy.burn(third_owner, amount_to_burn, {'from': second_owner})

    # new owner stablecoins can only be burned by vault 
    usds_proxy.burn(third_owner, amount_to_burn, {'from': vault_proxy.address})
    assert usds_proxy.totalSupply() == amount - amount_to_burn
