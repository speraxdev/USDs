#!/usr/bin/python3
import pytest
import brownie
from brownie import  Wei, Contract, reverts, SperaxTokenL2


def test_chi_redeem(sperax, owner_l2):
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

    core_proxy.chiRedeem(vault_proxy, {'from': owner_l2})

def test_mint_usds(sperax, owner_l2, accounts, weth):
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

    (
        usdt_strategy,
        wbtc_strategy,
        weth_strategy,
    ) = strategy_proxies

    (
        two_hops_buyback, 
        three_hops_buyback
    ) = buybacks

    

    invalid_coll = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    deadline = 1637632800 + brownie.chain.time()
    amount  = 100000
    slippage_collateral = 1000000000000000000000000000000
    slippage_spa = 1000000000000000000000000000000
    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_spa, {'from': accounts[5] })

    weth_erc20 = brownie.interface.IERC20(weth.address)
    weth_erc20.approve(vault_proxy.address, slippage_spa, {'from': accounts[5]})

    #collateral not addedd
    with reverts():
        vault_proxy.mintBySpecifyingUSDsAmt(
            invalid_coll,
            int(amount),
            slippage_collateral,
            slippage_spa,
            deadline,
            {'from': accounts[5]}
        )

    #zero amount
    with reverts("Amount needs to be greater than 0"):
        vault_proxy.mintBySpecifyingUSDsAmt(
            weth.address,
            0,
            slippage_collateral,
            slippage_spa,
            deadline,
            {'from': accounts[5]}
        )

    with reverts('Deadline expired'):
        vault_proxy.mintBySpecifyingUSDsAmt(
            weth.address,
            int(amount),
            slippage_collateral,
            slippage_spa,
            0,
            {'from': accounts[5]}
        )

    txn = vault_proxy.mintBySpecifyingUSDsAmt(
        weth.address,
        int(amount),
        slippage_collateral,
        slippage_spa,
        deadline,
        {'from': accounts[5]}
    )

    txn = vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
    vault_proxy.updateCollateralInfo(
        weth,
        weth_strategy,
        True,
        80,
        two_hops_buyback,
        True, {'from': owner_l2}
    )
    txn = vault_proxy.allocate({'from': owner_l2})
    txn = vault_proxy.allocate({'from': owner_l2})

    assert txn.events["CollateralAllocated"]["allocateAmount"] >  0

    vault_proxy.updateCollateralInfo(
        weth,
        weth_strategy,
        True,
        80,
        two_hops_buyback,
        True, {'from': owner_l2}
    )

    txn = vault_proxy.allocate({'from': owner_l2})

    vault_proxy.updateCollateralInfo(
        weth,
        weth_strategy,
        False,
        80,
        two_hops_buyback,
        True, {'from': owner_l2}
    )



    with reverts('Rebase paused'):
        txn = vault_proxy.rebase({'from': owner_l2})

    vault_proxy.updateRebasePermission(True, {'from': owner_l2})

    with reverts('Caller is not a rebaser'):
        vault_proxy.rebase({'from': owner_l2})


    vault_proxy.grantRole(vault_proxy.REBASER_ROLE(), owner_l2, {'from': owner_l2})
    txn = vault_proxy.rebase({'from': owner_l2})

    vault_proxy.revokeRole(vault_proxy.REBASER_ROLE(), owner_l2, {'from': owner_l2})
    with reverts('Caller is not a rebaser'):
        vault_proxy.rebase({'from': owner_l2})

    vault_proxy.renounceRole(vault_proxy.REBASER_ROLE(), owner_l2, {'from': owner_l2})

    core_proxy.chiRedeem(vault_proxy, {'from': owner_l2})



def test_mint_spa(sperax, weth, owner_l2, accounts):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    invalid_coll = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    deadline = 1637632800 + brownie.chain.time()
    amount  = 1000
    slippage_collateral = 1000000000000000000000000000000
    slippage_usds = 10

    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_collateral, {'from': accounts[5] })
    weth_erc20 = brownie.interface.IERC20(weth.address)
    weth_erc20.approve(vault_proxy.address, slippage_collateral, {'from': accounts[5]})

    with reverts():
        vault_proxy.mintBySpecifyingSPAamt(
            invalid_coll,
            int(amount),
            slippage_usds,
            slippage_collateral,
            deadline,
            {'from': accounts[5]}
        )

    with reverts("Amount needs to be greater than 0"):
        vault_proxy.mintBySpecifyingSPAamt(
            weth.address,
            0,
            slippage_usds,
            slippage_collateral,
            deadline,
            {'from': accounts[5]}
        )

    vault_proxy.mintBySpecifyingSPAamt(
        weth.address,
        int(amount),
        slippage_usds,
        slippage_collateral,
        deadline,
        {'from': accounts[5]}
    )


def test_mint_collateral(sperax, weth, owner_l2, accounts):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    invalid_coll = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    deadline = 1637632800 + brownie.chain.time()
    amount  = 10000
    slippage_collateral = 10
    slippage_coll = 1000000000000000000000000000000

    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_coll, {'from': accounts[5] })
    weth_erc20 = brownie.interface.IERC20(weth.address)
    weth_erc20.approve(vault_proxy.address, slippage_coll, {'from': accounts[5]})

    with reverts():
        vault_proxy.mintBySpecifyingCollateralAmt(
            invalid_coll,
            int(amount),
            slippage_collateral,
            slippage_coll,
            deadline,
            {'from': accounts[5]}
        )

    with reverts("Amount needs to be greater than 0"):
        vault_proxy.mintBySpecifyingCollateralAmt(
            weth.address,
            0,
            slippage_collateral,
            slippage_coll,
            deadline,
            {'from': accounts[5]}
        )

    vault_proxy.mintBySpecifyingCollateralAmt(
        weth.address,
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
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax


    txn = vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
    assert txn.events["AllocationPermssionChanged"]["permission"] == True


def test_vault_core_fail_allocate(sperax, accounts, owner_l2):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    with reverts('Allocate paused'):
        txn = vault_proxy.allocate({'from': owner_l2})

    with reverts('Ownable: caller is not the owner'):
        txn = vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
        txn = vault_proxy.allocate({'from': accounts[5]})



def test_upgrage_collateral(sperax, accounts, owner_l2, weth):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    (two_hops_buyback, three_hops_buyback) = buybacks

    collateralAddr = weth.address
    defaultStrategyAddr = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    invalid_coll = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    allocationAllowed = True
    allocatePercentage = 0
    buyBackAddr = two_hops_buyback.address
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
            invalid_coll,
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



def test_vault_core_add_collatral(sperax, accounts, owner_l2, weth):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    collateralAddr = weth.address
    defaultStrategyAddr = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    allocationAllowed = True
    allocatePercentage = 0
    buyBackAddr = (two_hops_buyback, three_hops_buyback) = buybacks
    rebaseAllowed = True

    with reverts('Collateral added'):
        vault_proxy.addCollateral(
            collateralAddr,
            defaultStrategyAddr,
            allocationAllowed,
            allocatePercentage,
            two_hops_buyback,
            rebaseAllowed, {'from': owner_l2})



def test_add_strategy(sperax, accounts, owner_l2, weth):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax


    (
        usdt_strategy,
        wbtc_strategy,
        weth_strategy,
    ) = strategy_proxies

    defaultStrategyAddr = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    txn = vault_proxy.addStrategy(defaultStrategyAddr, {'from': owner_l2})
    assert txn.events["StrategyAdded"]["added"] == True


    with reverts('Strategy added'):
        vault_proxy.addStrategy(defaultStrategyAddr, {'from': owner_l2})



def test_update_strategy_rwd_buyback_addr(sperax, owner_l2):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    (
        usdt_strategy,
        wbtc_strategy,
        weth_strategy,
    ) = strategy_proxies

    (
        two_hops_buyback, 
        three_hops_buyback
    ) = buybacks

    defaultStrategyAddr = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    with reverts('Strategy not added'):
        txn = vault_proxy.updateStrategyRwdBuybackAddr(
            defaultStrategyAddr,
            two_hops_buyback,
        {'from': owner_l2})

    vault_proxy.addStrategy(defaultStrategyAddr, {'from': owner_l2})
    txn = vault_proxy.updateStrategyRwdBuybackAddr(
            defaultStrategyAddr,
            two_hops_buyback,
        {'from': owner_l2})

    assert txn.events["StrategyRwdBuyBackUpdateded"]["strategyAddr"]  == defaultStrategyAddr
    assert txn.events["StrategyRwdBuyBackUpdateded"]["buybackAddr"]  == two_hops_buyback.address




def test_reedem(sperax, accounts, owner_l2, weth):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    deadline = brownie.chain.time() + 2000
    amount  = 1000000
    invalid_coll = brownie.convert.to_address('0x0000000000000000000000000000000000000000')

    slippage_collateral_mint = 1000000000000000000000000000000
    slippage_spa_mint = 1000000000000000000000000000000

    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_collateral_mint, {'from': accounts[5] })

    weth_erc20 = brownie.interface.IERC20(weth.address)
    weth_erc20.approve(vault_proxy.address, slippage_collateral_mint, {'from': accounts[5]})

    txn = vault_proxy.mintBySpecifyingUSDsAmt(
        weth.address,
        int(amount),
        slippage_collateral_mint,
        slippage_spa_mint,
        deadline,
        {'from': accounts[5]}
    )

    amount  = 10000
    slippage_collateral = 10
    slippage_spa = 10
    with reverts('Amount needs to be greater than 0'):
        vault_proxy.redeem(weth.address, 0, slippage_collateral, slippage_spa, deadline, {'from': accounts[5]})

    with reverts():
        vault_proxy.redeem(invalid_coll, amount, slippage_collateral, slippage_spa, deadline, {'from': accounts[5]})


    txn = spa.setMintable(
        vault_proxy,
        True,
        {'from': owner_l2}
    )

    expired_deadline = brownie.chain.time() - 200

    with reverts('Deadline expired'):
       vault_proxy.redeem(weth.address, amount, slippage_collateral, slippage_spa, expired_deadline, {'from': accounts[5]})

    txn = vault_proxy.redeem(weth.address, amount, slippage_collateral, slippage_spa, deadline, {'from': accounts[5]})


def test_reedem_collateral_from_strategy(sperax, accounts, owner_l2, weth):
    (   spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    deadline = brownie.chain.time() + 2000
    amount  = 10000

    slippage_collateral_mint = 1000000000000000000000000000000
    slippage_spa_mint = 1000000000000000000000000000000

    spa.approve(accounts[5].address, amount, {'from': owner_l2})
    spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    spa.approve(vault_proxy.address, slippage_collateral_mint, {'from': accounts[5] })


    weth_erc20 = brownie.interface.IERC20(weth.address)
    weth_erc20.approve(vault_proxy.address, slippage_collateral_mint, {'from': accounts[5]})

    txn = vault_proxy.mintBySpecifyingUSDsAmt(
        weth.address,
        int(amount),
        slippage_collateral_mint,
        slippage_spa_mint,
        deadline,
        {'from': accounts[5]}
    )

    amount  = 100000
    slippage_collateral = 10
    slippage_spa = 10

    txn = spa.setMintable(
        vault_proxy,
        True,
        {'from': owner_l2}
    )

    with reverts():
        txn = vault_proxy.redeem(weth.address, amount, slippage_collateral, slippage_spa, deadline, {'from': accounts[5]})

def test_vault_core_allocate(sperax, owner_l2):
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

    txn = vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
    txn = vault_proxy.allocate({'from': owner_l2})



def test_vault_core_tools_spa_amount_calculator(sperax, owner_l2):
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

    with reverts('invalid valueType'):
        txn = core_proxy.SPAAmountCalculator(1, 10000, vault_proxy, 3000,{'from': owner_l2})

    amount = core_proxy.SPAAmountCalculator.call(0, 10000, vault_proxy, 3000,{'from': owner_l2})
    assert amount  == 0

    amount = core_proxy.SPAAmountCalculator.call(0, 10000, vault_proxy, 0,{'from': owner_l2})
    assert amount == 0 


def test_usds_amount_calculator(sperax, owner_l2, weth):
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

    amt = core_proxy.USDsAmountCalculator.call(2, 10000, vault_proxy, weth, 3000,{'from': owner_l2})
    assert amt > 0
    txn = core_proxy.USDsAmountCalculator.call(2, 10000, vault_proxy, weth, 0,{'from': owner_l2})
    assert amt > 0

    with reverts('invalid valueType'):
        amt = core_proxy.USDsAmountCalculator.call(0, 10000, vault_proxy, weth, 3000,{'from': owner_l2})

    amt = core_proxy.USDsAmountCalculator.call(1, 10000, vault_proxy, weth, 3000,{'from': owner_l2})
    assert amt > 0


def test_colla_dept_amount_calculator(sperax, owner_l2, weth):
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

    amt = core_proxy.collaDeptAmountCalculator.call(1, 10000, vault_proxy, weth, 3000,{'from': owner_l2})
    assert amt > 0

    amt = core_proxy.collaDeptAmountCalculator.call(1, 10000, vault_proxy, weth, 0,{'from': owner_l2})
    assert amt > 0

    amt = core_proxy.collaDeptAmountCalculator.call(0, 10000, vault_proxy, weth, 3000,{'from': owner_l2})
    assert amt > 0

    amt = core_proxy.collaDeptAmountCalculator.call(0, 10000, vault_proxy, weth, 0,{'from': owner_l2})
    assert amt > 0

    amt = core_proxy.collaDeptAmountCalculator.call(1, 10000, vault_proxy, weth, 3000,{'from': owner_l2})
    assert amt > 0



def test_calculate_swapfeein(sperax, owner_l2):
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

    txn = vault_proxy.updateSwapInOutFeePermission(True, False, {'from': owner_l2})
    fee = core_proxy.calculateSwapFeeIn.call(vault_proxy, {'from': owner_l2})

    assert fee > 0


def test_calculate_swapfeeout(sperax, owner_l2):
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

    txn = vault_proxy.updateSwapInOutFeePermission(False, True, {'from': owner_l2})
    fee = core_proxy.calculateSwapFeeOut.call(vault_proxy, {'from': owner_l2})
    fee > 0


def test_chi_target(sperax, owner_l2):
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

    core_proxy.chiTarget(10, 1000, 1000000, vault_proxy, {'from':owner_l2 })
    core_proxy.chiTarget(10, 100000, 10000, vault_proxy, {'from':owner_l2 })
