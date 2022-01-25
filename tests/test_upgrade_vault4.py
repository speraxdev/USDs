#!/usr/bin/python3
import pytest
import brownie

#
# DON'T USE accounts[0-4]. 0-4 ARE RESERVED BY conftest.py
#

def test_upgrade_vault(sperax, VaultCoreV2, VaultCore, ProxyAdmin, accounts):
    print("upgrade Vault contract:\n")
    admin = '0x42d2f9f84EeB86574aA4E9FCccfD74066d809600'
    proxy_admin_address = '0x3E49925A79CbFb68BAa5bc9DFb4f7D955D1ddF25'
    owner = '0xc28c6970D8A345988e8335b1C229dEA3c802e0a6'
    vault_proxy_address = '0xF783DD830A4650D2A8594423F123250652340E3f'
    spa_address = '0x5575552988A3A80504bBaeB1311674fCFd40aD4B'
    vault_tool = '0x0390C6c7c320e41fCe0e6F0b982D20A88660F473'
    fee_vault = '0x4F987B24bD2194a574bB3F57b4e66B7f7eD36196'
    usdt_strategy = '0xdc118F2F00812326Fe0De5c9c74c1c0c609d1eB4'
    proxy_admin = brownie.Contract.from_abi(
        'ProxyAdmin',
        proxy_admin_address,
        ProxyAdmin.abi
    )
    vault = brownie.Contract.from_abi(
        'VaultCore',
        vault_proxy_address,
        VaultCore.abi
    )
    old_usds_address = vault.USDsAddr()
    old_oracle_address = vault.oracleAddr()

    new_vault_logic = VaultCore.deploy(
        {'from': owner}
    )

    txn = proxy_admin.upgrade(
        vault_proxy_address,
        new_vault_logic.address,
        {'from': admin}
    )
    new_vault_logic.initialize(
        spa_address,
        vault_tool,
        fee_vault,
        {'from': owner}
    )

    txn1 = vault.rebase({'from': owner})
    assert brownie.interface.ICurveGauge(vault.crvGaugeAddress()).claimed_reward(usdt_strategy, vault.crvToken()) > 0

    txn2 = vault.mintBySpecifyingUSDsAmt('0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', 1000000000, 10**20, 10**20, 49824360)

    assert 1 < 0
