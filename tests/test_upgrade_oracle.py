#!/usr/bin/python3
import pytest
import brownie

#
# DON'T USE accounts[0-3]. 0-3 ARE RESERVED BY conftest.py
#

def test_upgrade_oracle(sperax, OracleV2, Contract, admin, owner_l2):
    (proxy_admin, spa, usds2, vault_core_tools, vault_proxy, oracle_proxy) = sperax
    print("upgrade Oracle contract:\n")
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

    # Arbitrum rinkeby:
    price_feed_eth_arbitrum_testnet = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    weth_arbitrum_testnet = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'

    new_oracle.initialize(
        price_feed_eth_arbitrum_testnet,
        spa.address,
        weth_arbitrum_testnet,
        {'from': owner_l2}
    )

    new_oracle_proxy = Contract.from_abi(
        "OracleV2",
        oracle_proxy.address,
        OracleV2.abi
    )

    print(f"Oracle v2 proxy address: {new_oracle_proxy.address}")
    new_oracle_proxy.version() == "Oracle v.2"

    new_oracle_proxy.updateUSDsAddress(
        usds2.address,
        {'from': owner_l2}
    )
    new_oracle_proxy.updateVaultAddress(
        vault_proxy.address,
        {'from': owner_l2}
    )

    # admin cannot call base contract functions
    with brownie.reverts():
        new_oracle_proxy.updateUSDsAddress(
            usds2.address,
            {'from': admin}
        )
        new_oracle_proxy.updateVaultAddress(
            vault_proxy.address,
            {'from': admin}
        )