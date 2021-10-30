#!/usr/bin/python3
import pytest
import brownie
from brownie.test import given, strategy

#@given(amount=strategy('uint256', min_value=1, max_value=2**256-1))
@given(amount=strategy('uint256', min_value=1, max_value=100))
@given(percent=strategy('uint256', min_value=1, max_value=100))
def test_valid_mint(sperax, accounts, amount, percent):
    (spa, usds2, vault) = sperax

    print('amount: ', amount)
    first_owner = accounts[3]
    approver = accounts[4]
    second_owner = accounts[5]
    failed_owner = accounts[6]
    third_owner = accounts[7]
    # mint stablecoin
    usds2.mint(first_owner, amount, {'from': vault.address})
    assert usds2.balanceOf(first_owner) == amount
    assert usds2.totalSupply() == amount

    # approve transfer 
    usds2.approve(approver, amount, {'from': first_owner})
    txn = usds2.transferFrom(first_owner, second_owner, amount, {'from': approver})
    assert True == txn.return_value
    assert txn.events['Transfer']['from'] == first_owner 
    assert txn.events['Transfer']['to'] == second_owner
    assert txn.events['Transfer']['value'] == amount
    assert usds2.balanceOf(second_owner) == amount
    assert usds2.totalSupply() == amount

    # first_owner no longer owns the tokens. try to transfer
    with brownie.reverts():
        usds2.transfer(failed_owner, amount, {'from': first_owner})
    
    # new owner transfers stablecoin
    usds2.transfer(third_owner, amount, {'from': second_owner})
    assert usds2.balanceOf(third_owner) == amount
    assert usds2.totalSupply() == amount

    # amount of stablecoins to burn
    amount_to_burn = (amount + percent - 1) // percent
    print('number of tokens to burn: ', amount_to_burn)
    # stablecoin owner cannot burn their own tokens
    with brownie.reverts():
        usds2.burn(third_owner, amount_to_burn, {'from': second_owner})

    # new owner stablecoins can only be burned by vault 
    usds2.burn(third_owner, amount_to_burn, {'from': vault.address})
    assert txn
    assert usds2.totalSupply() == amount - amount_to_burn
