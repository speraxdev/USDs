#!/usr/bin/python3
import pytest
import brownie
from brownie.test import given, strategy

@given(amount=strategy('uint256', min_value=1, max_value=2**256-1))
@given(percent=strategy('uint256', min_value=1, max_value=100))
def test_valid_mint(usds, vault, accounts, amount, percent):
    print('amount: ', amount)
    # mint stablecoin
    usds.mint(accounts[2], amount, {'from': vault})
    assert usds.balanceOf(accounts[2]) == amount
    assert usds.totalSupply() == amount

    # approve transfer 
    usds.approve(accounts[3], amount, {'from': accounts[2]})
    txn = usds.transferFrom(accounts[2], accounts[4], amount, {'from': accounts[3]})
    assert True == txn.return_value
    assert txn.events['Transfer']['from'] == accounts[2]
    assert txn.events['Transfer']['to'] == accounts[4]
    assert txn.events['Transfer']['value'] == amount
    assert usds.balanceOf(accounts[4]) == amount
    assert usds.totalSupply() == amount

    # accounts[2] no longer owns the tokens. try to transfer
    with brownie.reverts():
        usds.transfer(accounts[5], amount, {'from': accounts[2]})
    
    # new owner transfers stablecoin
    usds.transfer(accounts[6], amount, {'from': accounts[4]})
    assert usds.balanceOf(accounts[6]) == amount
    assert usds.totalSupply() == amount

    # amount of stablecoins to burn
    amount_to_burn = (amount + percent - 1) // percent
    print('number of tokens to burn: ', amount_to_burn)
    # stablecoin owner cannot burn their own tokens
    with brownie.reverts():
        usds.burn(accounts[6], amount_to_burn, {'from': accounts[4]})

    # new owner stablecoins can only be burned by vault 
    usds.burn(accounts[6], amount_to_burn, {'from': vault})
    assert txn
    assert usds.totalSupply() == amount - amount_to_burn
