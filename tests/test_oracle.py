import pytest
import json
import time
import brownie


def user(accounts):
    return accounts[9]


def test_update_in_out_ratio(sperax, mock_token2, owner_l2):
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

    bugging_time= int(4294967295)-brownie.chain.time()+100000
    
    brownie.chain.snapshot()
    chainlink_usdc_price_feed = '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3'
    oracle_proxy.updateCollateralInfo(
        mock_token2.address,  # ERC20 address
        True,  # supported
        chainlink_usdc_price_feed,  # chainlink price feed address
        10**8,  # chainlink price feed precision
        {'from': owner_l2}
    )

    period = int(120)
    short_period = int(20)
    long_period = int(300)
    print(bugging_time%2**32)
    tx = oracle_proxy.changePeriod(
        period,
        short_period,
        long_period,
        {'from': owner_l2.address}
    )
    with brownie.reverts("updateInOutRatio: the time elapsed is too short."):
        tx = oracle_proxy.updateInOutRatio(
            {'from': owner_l2.address}
        )
    
    
    brownie.chain.sleep(122)
    tx = oracle_proxy.updateInOutRatio(
        {'from': owner_l2.address}
    )
    brownie.chain.sleep(130)
    with brownie.reverts("SafeMath: division by zero"):
        tx = oracle_proxy.updateInOutRatio(
            {'from': owner_l2.address}
        )
    brownie.chain.sleep(bugging_time)
    with brownie.reverts("updateInOutRatio: error last update happened in the future"):
       tx = oracle_proxy.updateInOutRatio(
            {'from': owner_l2.address}
        )
            
def test_consult(sperax, mock_token2, owner_l2):
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
    pool_address = '0x149671e74dDa61BEE5C9007353edbbA95b4d448B'
    zero_address ="0x0000000000000000000000000000000000000000"


    tx = oracle_proxy._getUniMAPrice(
            pool_address,
            spa.address,
            zero_address,
            10**2,
            10**18,
            1000,
            {'from': owner_l2.address}
        )


    with brownie.reverts("BP"):
        tx = oracle_proxy._getUniMAPrice(
            pool_address,
            spa.address,
            mock_token2.address,
            10**18,
            10**18,
            0,
            {'from': owner_l2.address}
        )
    tx = oracle_proxy._getUniMAPrice(
            pool_address,
            spa.address,
            mock_token2.address,
            10**2,
            10**18,
            1,
            {'from': owner_l2.address}
        )



def test_get_SPA_price(sperax, owner_l2):
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

    spa_address="0xB4A3B0Faf0Ab53df58001804DdA5Bfc6a3D59008" #arb-mainnet
    usds_address="0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    zero_address ="0x0000000000000000000000000000000000000000"
    
    tx = oracle_proxy.getSPAprice(
        {'from': owner_l2.address}
    )
    
    tx=oracle_proxy.updateUniPoolsSetting(
        zero_address,
        usds_address,
        300,
        300,
        {'from': owner_l2.address}
    ) 
    with brownie.reverts("SPA oracle pool does not exist."):
        tx = oracle_proxy.getSPAprice(
        {'from': owner_l2.address}
    )
def test_update_USDs_Address(sperax, owner_l2):
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
    spa_address="0xB4A3B0Faf0Ab53df58001804DdA5Bfc6a3D59008" #arb-mainnet
    usds_address="0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    zero_address ="0x0000000000000000000000000000000000000000"

    tx = oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )
    print(tx.events)
    tx=oracle_proxy.updateUniPoolsSetting(
        spa_address,
        usds_address,
        300,
        300,
        {'from': owner_l2.address}
    ) 
    tx = oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )



def test_get_USDC_price(sperax, owner_l2):
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


    tx = oracle_proxy.getUSDCprice(
        {'from': owner_l2.address}
    )


def test_get_USDs_price(sperax,weth,accounts, owner_l2):
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
    # chainlink_usdc_price_feed = '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3'
    # oracle_proxy.updateCollateralInfo(
    #     weth.address,  # ERC20 address
    #     True,  # supported
    #     chainlink_usdc_price_feed,  # chainlink price feed address
    #     10**8,  # chainlink price feed precision
    #     {'from': owner_l2}
    # )
    # deadline = 1637632800 + brownie.chain.time() 
    # amount  = 1000000
    # slippage_collateral = 1000000000000000000000000000000
    # slippage_spa = 1000000000000000000000000000000
    # spa.approve(accounts[5].address, amount, {'from': owner_l2})
    # spa.transfer(accounts[5].address, amount, {'from': owner_l2})

    # spa.approve(vault_proxy.address, slippage_spa, {'from': accounts[5] })

    # weth_erc20 = brownie.interface.IERC20(weth.address)
    # weth_erc20.approve(vault_proxy.address, slippage_spa, {'from': accounts[5]})

    
    # txn = vault_proxy.mintBySpecifyingUSDsAmt(
    #     weth.address,
    #     int(amount),
    #     slippage_collateral,
    #     slippage_spa,
    #     deadline,
    #     {'from': accounts[5]}
    # )

    tx = oracle_proxy.getUSDsPrice(
        {'from': owner_l2.address}
    )


def test_get_USDS_price_average(sperax, owner_l2):
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

    tx = oracle_proxy.getUSDsPrice_average(
        {'from': owner_l2.address}
    )


def test_get_Collateral_Price(sperax, mock_token2, owner_l2):
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
    zero_address = "0x0000000000000000000000000000000000000000"
    with brownie.reverts("getCollateralPrice: Collateral not supported."):
        tx = oracle_proxy.getCollateralPrice(
            zero_address,
            {'from': owner_l2.address}
        )
    tx = oracle_proxy.getCollateralPrice(
        mock_token2.address,
        {'from': owner_l2.address}
    )


def test_get_Collateral_Price_Precision(sperax, mock_token2, owner_l2):
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
    zero_address = "0x0000000000000000000000000000000000000000"
    with brownie.reverts("getCollateralPrice_prec: Collateral not supported."):
        tx = oracle_proxy.getCollateralPrice_prec(
            zero_address,
            {'from': owner_l2.address}
        )
    tx = oracle_proxy.getCollateralPrice_prec(
        mock_token2.address,
        {'from': owner_l2.address}
    )


def test_update_vault_address(sperax, mock_token2, owner_l2):
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

    tx = oracle_proxy.updateVaultAddress(
        mock_token2.address,
        {'from': owner_l2.address}
    )



def test_quote_at_tick(sperax, mock_token2, owner_l2):
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

   
    pool_address = '0x149671e74dDa61BEE5C9007353edbbA95b4d448B'
    with brownie.reverts("BP"):
        tx = oracle_proxy._getUniMAPrice(
            pool_address,
            spa.address,
            mock_token2.address,
            10**18,
            10**18,
            0,
            {'from': owner_l2.address}
        )
