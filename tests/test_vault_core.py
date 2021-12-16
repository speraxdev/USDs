#!/usr/bin/python3
import pytest
import brownie
from brownie import  Wei, Contract, reverts, SperaxTokenL2


def test_mint_usds(sperax, mock_token4, owner_l2, accounts, mock_token2):
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
    amount  = 1000000
    slippage_collateral = 1000000000000000000000000000000
    slippage_spa = 1000000000000000000000000000000
    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_spa, {'from': accounts[5] })
    mock_token4.approve(vault_proxy.address, slippage_spa, {'from': accounts[5] })

    #collateral not addedd
    with reverts():
        vault_proxy.mintBySpecifyingUSDsAmt(
            mock_token2.address,
            int(amount),
            slippage_collateral,
            slippage_spa,
            deadline,
            {'from': accounts[5]}
        )

    #zero amount 
    with reverts("Amount needs to be greater than 0"):
        vault_proxy.mintBySpecifyingUSDsAmt(
            mock_token4.address,
            0,
            slippage_collateral,
            slippage_spa,
            deadline,
            {'from': accounts[5]}
        )

    with reverts('Deadline expired'):
        vault_proxy.mintBySpecifyingUSDsAmt(
            mock_token4.address,
            int(amount),
            slippage_collateral,
            slippage_spa,
            0,
            {'from': accounts[5]}
        )

    vault_proxy.mintBySpecifyingUSDsAmt(
        mock_token4.address,
        int(amount),
        slippage_collateral,
        slippage_spa,
        deadline,
        {'from': accounts[5]}
    )


def test_mint_spa(sperax, weth, owner_l2, accounts, mock_token4):
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
    amount  = 100000
    slippage_collateral = 1000000000000000000000000000000
    slippage_usds = 10

    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_collateral, {'from': accounts[5] })
    mock_token4.approve(vault_proxy.address, slippage_collateral, {'from': accounts[5] })

    with reverts():
        vault_proxy.mintBySpecifyingSPAamt(
            weth.address,
            int(amount),
            slippage_usds,
            slippage_collateral,
            deadline,
            {'from': accounts[5]}
        )

    with reverts("Amount needs to be greater than 0"):
        vault_proxy.mintBySpecifyingSPAamt(
            mock_token4.address,
            0,
            slippage_usds,
            slippage_collateral,
            deadline,
            {'from': accounts[5]}
        )

    vault_proxy.mintBySpecifyingSPAamt(
        mock_token4.address,
        int(amount),
        slippage_usds,
        slippage_collateral,
        deadline,
        {'from': accounts[5]}
    )


def test_mint_collateral(sperax, weth, owner_l2, accounts, mock_token4):
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
    slippage_collateral = 10
    slippage_coll = 1000000000000000000000000000000

    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_coll, {'from': accounts[5] })
    mock_token4.approve(vault_proxy.address, slippage_coll, {'from': accounts[5] })

    with reverts():
        vault_proxy.mintBySpecifyingCollateralAmt(
            weth.address,
            int(amount),
            slippage_collateral,
            slippage_coll,
            deadline,
            {'from': accounts[5]}
        )

    with reverts("Amount needs to be greater than 0"):
        vault_proxy.mintBySpecifyingCollateralAmt(
            mock_token4.address,
            0,
            slippage_collateral,
            slippage_coll,
            deadline,
            {'from': accounts[5]}
        )

    vault_proxy.mintBySpecifyingCollateralAmt(
        mock_token4.address,
        int(amount),
        slippage_collateral,
        slippage_coll,
        deadline,
        {'from': accounts[5]}
    )



def test_allow_allocate(sperax, accounts, owner_l2):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax


    txn = vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
    assert txn.events["AllocationPermssionChanged"]["permission"] == True


def test_vault_core_allocate(sperax, accounts, owner_l2):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax
    txn = vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
    txn = vault_proxy.allocate({'from': owner_l2})



def test_vault_core_fail_allocate(sperax, accounts, owner_l2):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    with reverts('Allocate paused'):
        txn = vault_proxy.allocate({'from': owner_l2})

    with reverts('Ownable: caller is not the owner'):
        txn = vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
        txn = vault_proxy.allocate({'from': accounts[5]})



def test_upgrage_collateral(sperax, mock_token4, accounts, owner_l2, weth):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax
   
    collateralAddr = mock_token4.address
    defaultStrategyAddr = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    allocationAllowed = True
    allocatePercentage = 0
    buyBackAddr = buyback.address
    rebaseAllowed = True

    with reverts('Ownable: caller is not the owner'):
        vault_proxy.updateCollateralInfo(
            collateralAddr, 
            defaultStrategyAddr, 
            allocationAllowed, 
            allocatePercentage, 
            buyBackAddr, 
            rebaseAllowed, {'from': accounts[5]})

    with reverts('Collateral not added'):
        vault_proxy.updateCollateralInfo(
            weth, 
            defaultStrategyAddr, 
            allocationAllowed, 
            allocatePercentage, 
            buyBackAddr, 
            rebaseAllowed, {'from': owner_l2})

    txn = vault_proxy.updateCollateralInfo(
            collateralAddr, 
            defaultStrategyAddr, 
            allocationAllowed, 
            allocatePercentage, 
            buyBackAddr, 
            rebaseAllowed, {'from': owner_l2})

    assert txn.events["CollateralChanged"]["collateralAddr"] == collateralAddr
    assert txn.events["CollateralChanged"]["addded"] == True



def test_vault_core_add_collatral(sperax, mock_token4, accounts, owner_l2, weth):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    collateralAddr = mock_token4.address
    defaultStrategyAddr = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    allocationAllowed = True
    allocatePercentage = 0
    buyBackAddr = buyback.address
    rebaseAllowed = True

    with reverts('Collateral added'):
        vault_proxy.addCollateral(
            collateralAddr, 
            defaultStrategyAddr, 
            allocationAllowed, 
            allocatePercentage, 
            buyBackAddr, 
            rebaseAllowed, {'from': owner_l2})



def test_add_strategy(sperax, mock_token4, accounts, owner_l2, weth):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    txn = vault_proxy.addStrategy(strategy_proxy, {'from': owner_l2})
    assert txn.events["StrategyAdded"]["added"] == True


    with reverts('Strategy added'):
        vault_proxy.addStrategy(strategy_proxy, {'from': owner_l2})



def test_update_strategy_rwd_buyback_addr(sperax, owner_l2):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    with reverts('Strategy not added'):
        txn = vault_proxy.updateStrategyRwdBuybackAddr(
            strategy_proxy,
            buyback,
        {'from': owner_l2})
    
    vault_proxy.addStrategy(strategy_proxy, {'from': owner_l2})
    txn = vault_proxy.updateStrategyRwdBuybackAddr(
            strategy_proxy,
            buyback,
        {'from': owner_l2})

    assert txn.events["StrategyRwdBuyBackUpdateded"]["strategyAddr"]  == strategy_proxy.address
    assert txn.events["StrategyRwdBuyBackUpdateded"]["buybackAddr"]  == buyback.address


def test_rebase(sperax, owner_l2):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    with reverts('Rebase paused'):
        txn = vault_proxy.rebase({'from': owner_l2})

    vault_proxy.updateRebasePermission(True, {'from': owner_l2})

    with reverts('Caller is not a rebaser'):
        vault_proxy.rebase({'from': owner_l2})

    vault_proxy.grantRole(vault_proxy.REBASER_ROLE(), owner_l2, {'from': owner_l2})
    txn = vault_proxy.rebase({'from': owner_l2})

    print('SPA price', txn.events["SPAprice"]["SPAprice"])
    print('USDs price', txn.events["USDsPrice"]["USDsPrice"])
    print('old supply', txn.events["SPAprice"]["SPAprice"])
    print('new supply', txn.events["Rebase"]["newSupply"])

    assert txn.events["SPAprice"]["SPAprice"] > 0
    assert txn.events["USDsPrice"]["USDsPrice"] > 0

    assert txn.events["Rebase"]["oldSupply"]  > 0
    assert txn.events["Rebase"]["newSupply"] == 0

def test_reedem(sperax, accounts, mock_token4, owner_l2, weth):
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
    amount  = 1000000
    slippage_collateral = 10
    slippage_spa = 10


    slippage_collateral_mint = 1000000000000000000000000000000
    slippage_spa_mint = 1000000000000000000000000000000

    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_collateral_mint, {'from': accounts[5] })
    mock_token4.approve(vault_proxy.address, slippage_collateral_mint, {'from': accounts[5] })

    txn = vault_proxy.mintBySpecifyingUSDsAmt(
        mock_token4.address,
        int(amount),
        slippage_collateral_mint,
        slippage_spa_mint,
        deadline,
        {'from': accounts[5]}
    )

    with reverts('Amount needs to be greater than 0'):
        vault_proxy.redeem(mock_token4.address, 0, slippage_collateral, slippage_spa, deadline, {'from': accounts[5]})
    
    with reverts():
        vault_proxy.redeem(weth.address, amount, slippage_collateral, slippage_spa, deadline, {'from': accounts[5]})
    
    txn = spa.setMintable(
        vault_proxy,
        True,
        {'from': owner_l2}
    )

    txn = vault_proxy.redeem(mock_token4.address, amount, slippage_collateral, slippage_spa, deadline, {'from': accounts[5]})
    assert txn.events["SPAprice"]["SPAprice"] > 0





