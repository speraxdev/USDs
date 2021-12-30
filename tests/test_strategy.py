import pytest
import json
import time
import brownie



@pytest.fixture(scope="module", autouse=True)
def invalid_collateral(usdt):
    return usdt.address


def user(accounts):
    return accounts[9]
def test_collect_interest_pTokens(sperax, usdt, accounts,owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1]
    # manually get some LP tokens (3CRV) and transfer them to strategy_proxy;
    # strategy_proxy will mistake these LP tokens (after being covert back to
    # collertal) as earned interest
    amount = int(999)
    # txn = usdt.deposit(
    #     {'from': accounts[9].address, 'amount': amount}
    # )
    curvePool = brownie.interface.ICurve3Pool(
        '0x960ea3e3C7FB317332d990873d354E18d7645590')
    amounts = [0, 0, amount]
    brownie.interface.IERC20(usdt.address).approve(
        curvePool.address, amount, {'from': owner_l2})
    curvePool.add_liquidity(amounts, 0, {'from': owner_l2})
    lpToken = brownie.interface.IERC20(
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2')
    weth_erc20 = brownie.interface.IERC20(usdt.address)
    print("lp token balance: ",lpToken.balanceOf(owner_l2))
    tx = lpToken.transfer(
        strategy_proxy, 500,  {'from': owner_l2})
    print("lp tx:", tx.events)

    txn = weth_erc20.transfer(strategy_proxy.address, amount/10, {'from': owner_l2})
    txn = strategy_proxy.deposit(
        usdt.address,
        amount/10,
        {'from': vault_proxy.address}
    )
    txn = strategy_proxy._getTotalPTokens({'from': vault_proxy.address})
    print("contract ptokens: ", txn)
    interest = strategy_proxy.checkInterestEarned(
        usdt.address, {'from': vault_proxy.address})
    print("interest: ", interest)
    assert interest > 0
    assert strategy_proxy.allocatedAmt(usdt.address) == 0
    
    strategy_proxy.collectInterest(
        vault_proxy.address,
        usdt.address,
        {'from': vault_proxy.address}
    )
    assert strategy_proxy.allocatedAmt(usdt.address) == 0
    assert weth_erc20.balanceOf(vault_proxy.address) > 0

def test_collect_interest(sperax, weth, accounts,owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1]
    # manually get some LP tokens (3CRV) and transfer them to strategy_proxy;
    # strategy_proxy will mistake these LP tokens (after being covert back to
    # collertal) as earned interest
    amount = int(1000000000)
    txn = weth.deposit(
        {'from': owner_l2.address, 'amount': amount}
    )
    curvePool = brownie.interface.ICurve3Pool(
        '0x960ea3e3C7FB317332d990873d354E18d7645590')
    amounts = [0, 0, amount]
    brownie.interface.IERC20(weth.address).approve(
        curvePool.address, amount, {'from': owner_l2})
    curvePool.add_liquidity(amounts, 0, {'from': owner_l2})
    lpToken = brownie.interface.IERC20(
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2')
    weth_erc20 = brownie.interface.IERC20(weth.address)
    tx = lpToken.transfer(
        strategy_proxy, lpToken.balanceOf(owner_l2),  {'from': accounts[9]})
    print("lp tx:", tx.events)
    txn = strategy_proxy._getTotalPTokens({'from': vault_proxy.address})
    print("contract ptokens: ", txn)
    interest = strategy_proxy.checkInterestEarned(
        weth.address, {'from': vault_proxy.address})
    print("interest: ", interest)
    assert interest > 0
    assert strategy_proxy.allocatedAmt(weth.address) == 0

    strategy_proxy.collectInterest(
        vault_proxy.address,
        weth.address,
        {'from': vault_proxy.address}
    )
    assert strategy_proxy.allocatedAmt(weth.address) == 0
    assert weth_erc20.balanceOf(vault_proxy.address) > 0




def test_total_pTokens_withdraw(sperax, weth, usdt, wbtc, owner_l2, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1]
    amount = int(1000000000)
    txn = weth.deposit(
        {'from': accounts[9].address, 'amount': amount}
    )
    curvePool = brownie.interface.ICurve3Pool(
        '0x960ea3e3C7FB317332d990873d354E18d7645590')
    amounts = [0, 0, amount]
    brownie.interface.IERC20(weth.address).approve(
        curvePool.address, amount, {'from': accounts[9]})
    curvePool.add_liquidity(amounts, 0, {'from': accounts[9]})
    lpToken = brownie.interface.IERC20(
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2')
    weth_erc20 = brownie.interface.IERC20(weth.address)
    tx = lpToken.transfer(
        strategy_proxy, lpToken.balanceOf(accounts[9]),  {'from': accounts[9]})
    print("lp tx:", tx.events)
    txn = strategy_proxy._getTotalPTokens({'from': vault_proxy.address})
    print("contract ptokens: ", txn)
    strategy_proxy.checkBalance(weth, {'from': vault_proxy.address})
    # withdraw 1/10 of the previous deposit
    txn = strategy_proxy.withdraw(
        accounts[9],
        weth.address,
        (amount/10),
        {'from': vault_proxy.address}
    )




def test_withdraw(sperax, usdt, owner_l2, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(1000000000)
    # withdraw before deposit-----------------------------------------------------------------------
    with brownie.reverts("Insufficient 2CRV balance"):
         txn = strategy_proxy.withdraw(
         accounts[9],
         usdt.address,
         amount,
         {'from': vault_proxy.address}
    )

    # usdt deposit-------------------------------------------------------

    # testing the validity of recipient.
    zero_address = "0x0000000000000000000000000000000000000000"
    with brownie.reverts("Invalid recipient"):
        txn = strategy_proxy.withdraw(
            zero_address,
            usdt.address,
            (amount),
            {'from': vault_proxy.address}
        )
    # usdt deposit--------------------------------------------------------------------------
    txn = usdt.transfer(strategy_proxy.address,
                              amount, {'from': owner_l2})

    assert txn.return_value == True
    txn = strategy_proxy.deposit(
        usdt.address,
        amount,
        {'from': vault_proxy.address}
    )
    assert txn.events['Deposit']['_asset'] == usdt.address
    assert txn.events['Deposit']['_amount'] == amount

    # withdraw 1/10 of the previous deposit
    txn = strategy_proxy.withdraw(
        accounts[9],
        usdt.address,
        (amount/10),
        {'from': vault_proxy.address}
    )

    with brownie.reverts("Caller is not the Vault"):
          strategy_proxy.withdraw(
         accounts[9],
         usdt.address,
         (amount/10),
         {'from': owner_l2.address}
    )
    with brownie.reverts("Insufficient 2CRV balance"):
         strategy_proxy.withdraw(
         accounts[9],
         usdt.address,
         (amount + 1),
         {'from': vault_proxy.address}
    )

def test_check_balance(sperax, weth, usdt):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1]
    zero_address = "0x0000000000000000000000000000000000000000"
    balance = strategy_proxy.checkBalance(usdt.address, {'from': vault_proxy.address})
    with brownie.reverts("Unsupported collateral"):
        balance = strategy_proxy.checkBalance(
            usdt, {'from': vault_proxy.address})

    assert balance == 0
    with brownie.reverts("Unsupported collateral"):
        strategy_proxy.checkBalance(
            zero_address, {'from': vault_proxy.address})


def test__safe_approve_all_tokens(sperax, owner_l2):
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
    strategy_proxy = strategy_proxies[1]
    strategy_proxy.safeApproveAllTokens(
        {'from': owner_l2.address}
    )


def test_collect_reward_token(sperax):
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
    strategy_proxy = strategy_proxies[1]
    txn = strategy_proxy.collectRewardToken(
        {'from': vault_proxy.address})


def test_set_reward_Token_Address(sperax, usdt, owner_l2):
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
    strategy_proxy = strategy_proxies[1];
    txn = strategy_proxy.setRewardTokenAddress(
        usdt.address,
        {'from': owner_l2.address})


def test_set_reward_liquidation_threshold(sperax, owner_l2):
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
    strategy_proxy = strategy_proxies[1];
    threshold = int(10)
    txn = strategy_proxy.setRewardLiquidationThreshold(
        threshold,
        {'from': owner_l2.address})
    low_threshold = int(0)
    txn = strategy_proxy.setRewardLiquidationThreshold(
        threshold,
        {'from': owner_l2.address})


def test_set_interest_liquidation_threshold(sperax, owner_l2):
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
    strategy_proxy = strategy_proxies[1]
    Threshold = int(10)
    txn = strategy_proxy.setInterestLiquidationThreshold(
        Threshold,
        {'from': owner_l2.address})

    lowThreshold = int(0)
    txn = strategy_proxy.setInterestLiquidationThreshold(
        lowThreshold,
        {'from': owner_l2.address})


def test_set_PToken_address(sperax, usdt, owner_l2):
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
    strategy_proxy = strategy_proxies[1];
    reward_address = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    txn = strategy_proxy.setPTokenAddress(
        usdt.address,
        reward_address,
        {'from': owner_l2.address})

    reward_address2 = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    with brownie.reverts("pToken already set"):
         strategy_proxy.setPTokenAddress(
         usdt.address,
         reward_address2,
         {'from': owner_l2.address})


def test_set_Reward_Token_zero_address_asset(sperax, owner_l2):
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
    strategy_proxy = strategy_proxies[1];
    zero_address = "0x0000000000000000000000000000000000000000"

    with brownie.reverts("Invalid addresses"):
        strategy_proxy.setPTokenAddress(
            zero_address,
            zero_address,
            {'from': owner_l2.address}
        )

def test_set_PToken_address(sperax, usdt, owner_l2):
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
    strategy_proxy = strategy_proxies[1];
    ptoken_address2 = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    with brownie.reverts("pToken already set"):
         strategy_proxy.setPTokenAddress(
         usdt.address,
         ptoken_address2,
         {'from': owner_l2.address})

    ptoken_address = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    with brownie.reverts("pToken already set"):
         strategy_proxy.setPTokenAddress(
         usdt.address,
         ptoken_address,
         {'from': owner_l2.address})


def test_remove_PToken(sperax, owner_l2):
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
    strategy_proxy = strategy_proxies[1];
    low_index = int(0)

    txn = strategy_proxy.removePToken(
        low_index,
        {'from': owner_l2.address}
    )
    print("removed PToken:", txn.events['PTokenRemoved']['_pToken'])
    print("removed asset:", txn.events['PTokenRemoved']['_asset'])

    high_index = int(9999999999)
    with brownie.reverts("Invalid index"):
        strategy_proxy.removePToken(
            high_index,
            {'from': owner_l2.address}
        )


def test_remove_PToken2(sperax, owner_l2):
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
    strategy_proxy = strategy_proxies[1];
    low_index = int(1)

    txn = strategy_proxy.removePToken(
        low_index,
        {'from': owner_l2.address}
    )


def test_remove_PToken_assets(sperax, owner_l2, accounts):
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
    strategy_proxy = strategy_proxies[1];
    low_index = int(1)

    txn = strategy_proxy.removePToken(
        low_index,
        {'from': owner_l2.address}
    )
    print("removed PToken:", txn.events['PTokenRemoved']['_pToken'])
    print("removed asset:", txn.events['PTokenRemoved']['_asset'])


def test_deposit(sperax, usdt, accounts, owner_l2):
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
    strategy_proxy = strategy_proxies[1];

    amount = int(9999)

    txn = usdt.transfer(strategy_proxy.address, amount, {'from': owner_l2})

    assert txn.return_value == True
    txn = strategy_proxy.deposit(
        usdt.address,
        amount,
        {'from': vault_proxy.address}
    )
    assert txn.events['Deposit']['_asset'] == usdt.address
    assert txn.events['Deposit']['_amount'] == amount
    balance = strategy_proxy.checkBalance(usdt, {'from': vault_proxy.address})
    assert balance > 0


def test_deposit_invalid_amount(sperax, usdt):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(0)

    with brownie.reverts("Must deposit something"):
        txn = strategy_proxy.deposit(
            usdt.address,
            amount,
            {'from': vault_proxy.address}
        )


def test_deposit_invalid_assets(sperax, invalid_collateral):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(9999)

    with brownie.reverts("Unsupported collateral"):
        strategy_proxy.deposit(
            invalid_collateral,
            amount,
            {'from': vault_proxy.address}
        )


def test_withdraw_invalid_assets(sperax, invalid_collateral, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(9999)

    with brownie.reverts("Unsupported collateral"):
        txn = strategy_proxy.withdraw(
            accounts[8],
            invalid_collateral,
            (amount/10),
            {'from': vault_proxy.address})


def test_withdraw_invalid_amount(sperax, usdt, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(0)

    with brownie.reverts("Invalid amount"):
        txn = strategy_proxy.withdraw(
            accounts[8],
            usdt.address,
            (amount),
            {'from': vault_proxy.address}
        )


def test_collect_interest_invalid(sperax, usdt, invalid_collateral, accounts, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(1000000000)
    # testing invalid cases
    zero_address = "0x0000000000000000000000000000000000000000"

    with brownie.reverts("Unsupported collateral"):
        txn = strategy_proxy.collectInterest(
            accounts[8],
            invalid_collateral,
            {'from': vault_proxy.address}
        )

    with brownie.reverts("Invalid recipient"):
        txn = strategy_proxy.collectInterest(
            zero_address,
            usdt.address,
            {'from': vault_proxy.address}
        )

    with brownie.reverts("Unsupported collateral"):
        strategy_proxy.checkInterestEarned(
            invalid_collateral, {'from': vault_proxy.address})

    with brownie.reverts():
        strategy_proxy.collectInterest(
            accounts[8],
            usdt.address,
            {'from': vault_proxy.address}
        )

    txn = usdt.transfer(strategy_proxy.address, amount, {'from': owner_l2})
    assert txn.return_value == True
    txn = strategy_proxy.deposit(
        usdt.address,
        amount,
        {'from': vault_proxy.address}
    )
    assert txn.events['Deposit']['_asset'] == usdt.address
    assert txn.events['Deposit']['_amount'] == amount
    print("Amount Deposited: ", amount)

def test_collect_interest_zero_interest(sperax, usdt, accounts):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    interest = strategy_proxy.checkInterestEarned(
        usdt.address, {'from': vault_proxy.address})
    assert interest == 0
    with brownie.reverts("No interest earned"):
        strategy_proxy.collectInterest(
            vault_proxy.address,
            usdt.address,
            {'from': vault_proxy.address}
        )

def test_collect_interest(sperax, usdt, accounts, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    # manually get some LP tokens (2CRV) and transfer them to strategy_proxy;
    # strategy_proxy will mistake these LP tokens (after being covert back to
    # collertal) as earned interest
    amount = int(1000000000)
    curvePool = brownie.interface.ICurve2Pool('0x7f90122BF0700F9E7e1F688fe926940E8839F353')
    amounts = [0, amount]
    usdt.approve(curvePool.address, amount, {'from': owner_l2})
    curvePool.add_liquidity(amounts, 0, {'from': owner_l2})
    lpToken = brownie.interface.IERC20('0x7f90122bf0700f9e7e1f688fe926940e8839f353')
    lpToken.transfer(
        strategy_proxy, lpToken.balanceOf(owner_l2),  {'from': owner_l2})
    interest = strategy_proxy.checkInterestEarned(
        usdt.address, {'from': vault_proxy.address})
    assert interest > 0
    assert strategy_proxy.allocatedAmt(usdt.address) == 0
    strategy_proxy.collectInterest(
        vault_proxy.address,
        usdt.address,
        {'from': vault_proxy.address}
    )
    assert strategy_proxy.allocatedAmt(usdt.address) == 0
    assert usdt.balanceOf(vault_proxy.address) > 0


def test_withdraw_to_vault_invalid_amount(sperax, usdt, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(0)

    with brownie.reverts("Invalid amount"):
        txn = strategy_proxy.withdrawToVault(
            usdt.address,
            (amount),
            {'from': owner_l2.address}
        )


def test_withdraw_to_vault_invalid_assets(sperax, invalid_collateral, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(10005)

    with brownie.reverts("Unsupported collateral"):
        strategy_proxy.withdrawToVault(
            invalid_collateral,
            (amount),
            {'from': owner_l2.address})

def test_withdraw_to_vault(sperax, usdt, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax
    strategy_proxy = strategy_proxies[1];
    amount = int(1000000)

    txn = usdt.transfer(strategy_proxy.address,
                              amount, {'from': owner_l2})
    assert txn.return_value == True
    txn = strategy_proxy.deposit(
        usdt.address,
        amount,
        {'from': vault_proxy.address}
    )
    print("to vault deposited:", txn.return_value)
    assert txn.events['Deposit']['_asset'] == usdt.address
    print("check amout deposited vault: ", txn.events['Deposit']['_amount'])

    txn = strategy_proxy.withdrawToVault(
        usdt.address,
        (amount/2),
        {'from': owner_l2.address}
    )
    with brownie.reverts("Insufficient 2CRV balance"):
         strategy_proxy.withdrawToVault(
         usdt.address,
         (amount + 10000),
         {'from': owner_l2.address}
    )
