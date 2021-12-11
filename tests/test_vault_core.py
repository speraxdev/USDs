#!/usr/bin/python3
import pytest
import brownie
from brownie import  Wei, Contract, reverts

def test_mint_usds(sperax, usdt, owner_l2, accounts):
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

    deadline = 1637632800 + brownie.chain.time() 
    amount  = 10000
    slippage_collateral = 0
    slippage_collateral = amount - amount * slippage_collateral * 100
    slippage_spa = 0
    slippage_spa = amount - amount * slippage_spa * 100

    vault_proxy.mintWithUSDs(
        usdt.address,
        int(amount),
        slippage_collateral,
        slippage_spa,
        deadline,
        {'from': accounts[10]}
    )

def test_mint_collateral_not_added(sperax, weth, owner_l2, accounts ):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    deadline = 1637632800 + brownie.chain.time() 
    amount  = 10000
    slippage_collateral = 0
    slippage_collateral = amount - amount * slippage_collateral * 100
    slippage_spa = 0
    slippage_spa = amount - amount * slippage_spa * 100

    with reverts("Collateral not added"):
        vault_proxy.mintWithUSDs(
            weth.address,
            int(amount),
            slippage_collateral,
            slippage_spa,
            deadline,
            {'from': accounts[10]}
        )

def test_mint_usds_wth_zero_amount(sperax, usdt, owner_l2, accounts):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    deadline = 1637632800 + brownie.chain.time() 
    amount  = 0
    slippage_collateral = 0
    slippage_collateral = amount - amount * slippage_collateral * 100
    slippage_spa = 0
    slippage_spa = amount - amount * slippage_spa * 100

    with reverts("Amount needs to be greater than 0"):
        vault_proxy.mintWithUSDs(
            usdt.address,
            int(amount),
            slippage_collateral,
            slippage_spa,
            deadline,
            {'from': accounts[10]}
        )


