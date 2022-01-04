import pytest
import json
import time
import brownie

@pytest.fixture(scope="module", autouse=True)
def invalid_collateral(weth):
    return weth.address;

def user(accounts):
    return accounts[9]

def mintUSDs(
    amount,
    usds_proxy,
    spa,
    vault_proxy,
    owner,
    usdt
    ):
    deadline = 1637632800 + brownie.chain.time()
    slippage_collateral = 1000000000000000000000000000000
    slippage_spa = 1000000000000000000000000000000
    spa.approve(vault_proxy.address, slippage_spa, {'from': owner})
    usdt.approve(vault_proxy.address, slippage_collateral, {'from': owner})
    txn = vault_proxy.mintBySpecifyingUSDsAmt(
        usdt.address,
        amount,
        slippage_collateral,
        slippage_spa,
        deadline,
        {'from': owner}
    )

def simulateInterest(
    usdt,
    strategy_proxy,
    owner_l2
    ):
    # manually put lp tokens into strategy contract to simulate interest earned
    amount = int(10000000)
    curvePool = brownie.interface.ICurve2Pool('0x7f90122BF0700F9E7e1F688fe926940E8839F353')
    amounts = [0, amount]
    usdt.approve(curvePool.address, amount, {'from': owner_l2})
    curvePool.add_liquidity(amounts, 0, {'from': owner_l2})
    lpToken = brownie.interface.IERC20('0x7f90122bf0700f9e7e1f688fe926940e8839f353')
    strategy_balance_before = strategy_proxy.checkBalance(usdt)
    lpToken.transfer(
        strategy_proxy, lpToken.balanceOf(owner_l2),  {'from': owner_l2})


def test_withdraw_from_strategy(sperax, usdt, owner_l2, accounts):
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
    # prepare a EOA address and a contract address as USDs holder
    # (assuming in sperax(), owner_l2 has 10000 * 10^18 USDs)
    eoa_holder = accounts[8];
    # transfer usdt and spa to eoa_holder and contract_holder
    usdt_source_address = '0x7f90122bf0700f9e7e1f688fe926940e8839f353'
    usdt_erc20 = brownie.interface.IERC20("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9")
    usdt_erc20.transfer(eoa_holder, 1000000*10**6, {'from': usdt_source_address})
    spa.transfer(eoa_holder, 4*10**18, {'from': owner_l2})
    # mint some USDs for eoa_holder and contract_holder
    mintUSDs(10000 * 10**18, usds_proxy, spa, vault_proxy, eoa_holder, usdt)
    # allocate collateral from vault
    vault_proxy.updateCollateralInfo(usdt, strategy_proxy, True, 100, buybacks[1], True, {'from': owner_l2})
    vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
    vault_proxy.allocate({'from': owner_l2})
    # withdraw
    spa.approve(vault_proxy.address, 1000000000000000000000000000000, {'from': owner_l2})
    amount = 100 * 10**18;
    assert amount < usds_proxy.balanceOf(owner_l2)
    usdt_balance_before = usdt.balanceOf(owner_l2)
    txn = vault_proxy.redeem(
        usdt.address,
        amount,
        0,
        0,
        1637632800 + brownie.chain.time(),
        {'from': owner_l2}
    )
    assert usdt.balanceOf(owner_l2) > usdt_balance_before

def test_allocate(sperax, usdt, owner_l2, accounts):
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
    # prepare a EOA address and a contract address as USDs holder
    # (assuming in sperax(), owner_l2 has 10000 * 10^18 USDs)
    eoa_holder = accounts[8];
    contract_holder = oracle_proxy.address;
    # transfer usdt and spa to eoa_holder and contract_holder
    usdt_source_address = '0x7f90122bf0700f9e7e1f688fe926940e8839f353'
    usdt_erc20 = brownie.interface.IERC20("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9")
    usdt_erc20.transfer(eoa_holder, 1000000*10**6, {'from': usdt_source_address})
    usdt_erc20.transfer(contract_holder, 1000000*10**6, {'from': usdt_source_address})
    spa.transfer(eoa_holder, 4*10**18, {'from': owner_l2})
    spa.transfer(contract_holder, 4*10**18, {'from': owner_l2})
    # mint some USDs for eoa_holder and contract_holder
    mintUSDs(10000 * 10**18, usds_proxy, spa, vault_proxy, eoa_holder, usdt)
    mintUSDs(10000 * 10**18, usds_proxy, spa, vault_proxy, contract_holder, usdt)
    vault_asset_balance = usdt_erc20.balanceOf(vault_proxy)
    assert vault_asset_balance > 0;
    # allocate collateral from vault
    vault_asset_balance_before = usdt_erc20.balanceOf(vault_proxy)
    vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
    vault_proxy.allocate({'from': owner_l2})
    assert usdt_erc20.balanceOf(vault_proxy) < vault_asset_balance_before
    assert usdt_erc20.balanceOf(strategy_proxy) == 0
    assert strategy_proxy.checkBalance(usdt) > 0



def test_rebase(sperax, usdt, usdc, owner_l2, accounts, BuybackTwoHops, USDsL2):
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
    # switching to using real deployed usds
    # (because the usds-usdc pool created during coftest is problematic)
    usds_real = brownie.interface.IERC20('0xD74f5255D557944cf7Dd0E45FF521520002D5748')
    brownie.Contract.from_abi('USDs', usds_real.address, USDsL2.abi).changeVault(vault_proxy.address, {'from': '0xc28c6970D8A345988e8335b1C229dEA3c802e0a6'})
    vault_proxy.updateUSDsAddress(usds_real.address, {'from': owner_l2})
    buyback = BuybackTwoHops.deploy(
        usds_real.address,
        vault_proxy.address,
        {'from': owner_l2}
    )
    buyback.updateInputTokenInfo(
        usdt,
        True, # supported
        usdc,
        500,
        500,
        {'from': owner_l2}
    )
    # sending usds to an eoa and a contract
    eoa_holder = accounts[8];
    contract_holder = oracle_proxy.address;
    usds_resource = '0x08e0b47588e1ac22bc0f8b4afaa017aaf273f85e'
    usds_real.transfer(eoa_holder, 100 * 10**18, {'from': usds_resource})
    usds_real.transfer(contract_holder, 100 * 10**18, {'from': usds_resource})

    # allocate
    vault_proxy.updateCollateralInfo(usdt, strategy_proxy, True, 80, buyback, True, {'from': owner_l2})
    vault_proxy.updateAllocationPermission(True, {'from': owner_l2})
    vault_proxy.allocate({'from': owner_l2})
    vault_proxy.updateRebasePermission(True, {'from': owner_l2})
    # manually put lp tokens into strategy contract to simulate interest earned
    simulateInterest(usdt, strategy_proxy, owner_l2)
    interest = strategy_proxy.checkInterestEarned(
        usdt.address, {'from': vault_proxy.address})
    assert interest > 0
    # rebase
    vault_proxy.grantRole(vault_proxy.REBASER_ROLE(), owner_l2, {'from': owner_l2}).wait(1)
    strategy_balance_before = strategy_proxy.checkBalance(usdt)
    contract_holder_balance_before = usds_proxy.balanceOf(contract_holder)
    eoa_holder_balance_before = usds_real.balanceOf(eoa_holder)
    usds_total_supply_before = usds_real.totalSupply()
    tx = vault_proxy.rebase({'from': owner_l2}).wait(1)
    slippage = 3
    assert usds_proxy.balanceOf(contract_holder) > contract_holder_balance_before - slippage
    assert usds_proxy.balanceOf(contract_holder) < contract_holder_balance_before + slippage
    assert usds_real.balanceOf(eoa_holder) > eoa_holder_balance_before + slippage
    assert strategy_proxy.checkBalance(usdt) < strategy_balance_before
    assert usds_real.totalSupply() > usds_total_supply_before
