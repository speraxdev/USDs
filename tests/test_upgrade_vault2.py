#!/usr/bin/python3
import pytest
import brownie

#
# DON'T USE accounts[0-4]. 0-4 ARE RESERVED BY conftest.py
#

def test_upgrade_vault(sperax, VaultCoreV2, VaultCore, ProxyAdmin, accounts):
    (
        spa,
        usds_proxy,
        core_proxy,
        new_vault_proxy,
        oracle_proxy,
        strategy_proxies,
        buybacks,
        bancor
    ) = sperax

    print("upgrade Vault contract:\n")
    admin = '0x42d2f9f84EeB86574aA4E9FCccfD74066d809600'
    proxy_admin_address = '0x3E49925A79CbFb68BAa5bc9DFb4f7D955D1ddF25'
    owner_real = '0xc28c6970D8A345988e8335b1C229dEA3c802e0a6'
    vault_proxy_address = '0xF783DD830A4650D2A8594423F123250652340E3f'
    spa_address = '0x5575552988A3A80504bBaeB1311674fCFd40aD4B'
    vault_tool = '0x0390C6c7c320e41fCe0e6F0b982D20A88660F473'
    fee_vault = '0x4F987B24bD2194a574bB3F57b4e66B7f7eD36196'
    old_vault = brownie.Contract.from_abi(
        'VaultCore',
        vault_proxy_address,
        VaultCore.abi
    )
    proxy_admin = brownie.Contract.from_abi(
        'ProxyAdmin',
        proxy_admin_address,
        ProxyAdmin.abi
    )
    old_usds_address = old_vault.USDsAddr()
    old_oracle_address = old_vault.oracleAddr()

    new_vault = VaultCoreV2.deploy(
        {'from': owner_real}
    )
    new_vault_proxy = brownie.Contract.from_abi(
        "VaultCoreV2",
        vault_proxy_address,
        VaultCoreV2.abi
    )

    txn = proxy_admin.upgrade(
        vault_proxy_address,
        new_vault.address,
        {'from': admin}
    )
    new_vault.initialize(
        spa_address,
        vault_tool,
        fee_vault,
        {'from': owner_real}
    )
    new_vault_proxy.alignUpArray(
        {'from': owner_real}
    )
    assert new_vault_proxy.USDsAddr() == old_usds_address
    assert new_vault_proxy.oracleAddr() == old_oracle_address
    assert new_vault_proxy.allCollateralAddr(4) == '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
    assert new_vault_proxy.chi_beta() == 90000
