#!/usr/bin/python3
import pytest
import brownie

#
# DON'T USE accounts[0-4]. 0-4 ARE RESERVED BY conftest.py
#

def test_upgrade_oracle(sperax, OracleV2, proxy_admin, Contract, admin, owner_l2):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
<<<<<<< HEAD
        strategy_proxy,
=======
        strategy_proxies,
>>>>>>> 6b4339c5d90926b4e0f121ed86f77501ab320539
        buybacks,
        bancor
    ) = sperax

    print("upgrade Oracle contract:\n")
    # test case requires duplicating the contract, Oracle.sol, renamed as OracleV2.sol
    new_oracle = OracleV2.deploy(
        {'from': owner_l2}
    )

    with brownie.reverts():
        proxy_admin.upgrade(
            oracle_proxy.address,
            new_oracle.address,
            {'from': owner_l2}
        )

    txn = proxy_admin.upgrade(
        oracle_proxy.address,
        new_oracle.address,
        {'from': admin}
    )

    # Arbitrum-one:
    chainlink_eth_price_feed = '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612'
    chainlink_flags = '0x3C14e07Edd0dC67442FA96f1Ec6999c57E810a83'
    weth_address = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'

    new_oracle.initialize(
        chainlink_eth_price_feed,
        spa.address,
        weth_address,
        chainlink_flags,
        {'from': owner_l2}
    )

    new_oracle_proxy = Contract.from_abi(
        "OracleV2",
        oracle_proxy.address,
        OracleV2.abi
    )

    print(f"Oracle v2 proxy address: {new_oracle_proxy.address}")
    # requires duplicating Oracle.sol contract. The duplicate contract should
    # be called OracleV2.sol. This version 2 contract must expose a new function
    # called version() that returns the string "Oracle v.2"
    assert new_oracle_proxy.version() == "Oracle v.2"

    new_oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )
    new_oracle_proxy.updateVaultAddress(
        vault_proxy.address,
        {'from': owner_l2}
    )

    # admin cannot call base contract functions
    with brownie.reverts():
        new_oracle_proxy.updateUSDsAddress(
            usds_proxy.address,
            {'from': admin}
        )
        new_oracle_proxy.updateVaultAddress(
            vault_proxy.address,
            {'from': admin}
        )

    # Arbitrum mainnet collaterals:
    collaterals = {
        # USDC
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8': '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3',
        # USDT
        '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9': '0x3f3f5dF88dC9F13eac63DF89EC16ef6e7E25DdE7',
        # DAI
        '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1': '0xc5C8E77B397E531B8EC06BFb0048328B30E9eCfB',
        # WBTC
        '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f': '0x6ce185860a4963106506C203335A2910413708e9',
    }
    precision = 10**8
    for collateral, chainlink in collaterals.items():
        new_oracle_proxy.updateCollateralInfo(
            collateral, # ERC20 address
            True, # supported
            chainlink, # chainlink price feed address
            precision, # chainlink price feed precision
            {'from': owner_l2}
        )
