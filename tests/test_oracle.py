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
    chainlink_usdc_price_feed = '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3'
    oracle_proxy.updateCollateralInfo(
        mock_token2.address,  # ERC20 address
        True,  # supported
        chainlink_usdc_price_feed,  # chainlink price feed address
        10**8,  # chainlink price feed precision
        {'from': owner_l2}
    )
    period = int(70)
    short_period = int(20)
    long_period = int(110)

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
    time.sleep(71)
    tx = oracle_proxy.updateInOutRatio(
        {'from': owner_l2.address}
    )
    time.sleep(90)
    with brownie.reverts("SafeMath: division by zero"):
        tx = oracle_proxy.updateInOutRatio(
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
    tx = oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )
    print(tx.events)


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

    tx = oracle_proxy.getSPAprice(
        {'from': owner_l2.address}
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


def test_get_USDs_price(sperax, owner_l2):
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
