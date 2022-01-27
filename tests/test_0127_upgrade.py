import pytest
import json
import time
import brownie

# test on: 1. TwoPoolStrategy yield collection change: now the strategy collect yield via token with higher return
#          2. Buyback: buyback unified
#          3. USDsL2: rebase's impact on outflow removed
def test_upgrade(sperax, ProxyAdmin, VaultCoreV5, USDsL2V3, Buyback, TwoPoolStrategyV2, OracleV4, VaultCoreToolsV4):
    # addresses
    admin = '0x42d2f9f84EeB86574aA4E9FCccfD74066d809600'
    owner = '0xc28c6970D8A345988e8335b1C229dEA3c802e0a6'
    proxy_admin = brownie.Contract.from_abi(
        'ProxyAdmin',
        '0x3E49925A79CbFb68BAa5bc9DFb4f7D955D1ddF25',
        ProxyAdmin.abi
    )
    vault_core = brownie.Contract.from_abi(
        'VaultCoreV5',
        '0xF783DD830A4650D2A8594423F123250652340E3f',
        VaultCoreV5.abi
    )
    usds = brownie.Contract.from_abi(
        'USDsL2V3',
        '0xD74f5255D557944cf7Dd0E45FF521520002D5748',
        USDsL2V3.abi
    )
    USDC_strategy = brownie.Contract.from_abi(
        'USDC_strategy',
        '0xbF82a3212e13b2d407D10f5107b5C8404dE7F403',
        TwoPoolStrategyV2.abi
    )
    oracle = brownie.Contract.from_abi(
        'OracleV4',
        '0xf3f98086f7B61a32be4EdF8d8A4b964eC886BBcd',
        OracleV4.abi
    )
    interest_before = USDC_strategy.checkInterestEarned('0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8')


    # upgrade everything
    new_usds_logic = USDsL2V3.deploy({'from': owner})
    proxy_admin.upgrade(
        usds.address,
        new_usds_logic.address,
        {'from': admin}
    )
    new_vault_logic = VaultCoreV5.deploy({'from': owner})
    proxy_admin.upgrade(
        vault_core.address,
        new_vault_logic.address,
        {'from': admin}
    )
    new_vault_logic.initialize(
        '0x5575552988A3A80504bBaeB1311674fCFd40aD4B', #SperaxTokenL2
        '0x0390C6c7c320e41fCe0e6F0b982D20A88660F473', #VaultCoreToolsV4
        '0x4F987B24bD2194a574bB3F57b4e66B7f7eD36196', #fee vault
        {'from': owner}
    )
    new_usdc_strategy_logic = TwoPoolStrategyV2.deploy({'from': owner})
    proxy_admin.upgrade(
        USDC_strategy.address,
        new_usdc_strategy_logic.address,
        {'from': admin}
    )
    new_usdc_strategy_logic.initialize(
        '0x7f90122bf0700f9e7e1f688fe926940e8839f353',
        vault_core.address,
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978',
        ['0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8','0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'],
        ['0x7f90122bf0700f9e7e1f688fe926940e8839f353','0x7f90122bf0700f9e7e1f688fe926940e8839f353'],
        '0xbF7E49483881C76487b0989CD7d9A8239B20CA41',
        0,
        '0xf3f98086f7B61a32be4EdF8d8A4b964eC886BBcd',
        {'from': owner}
    )
    new_oracle_logic = OracleV4.deploy({'from': owner})
    proxy_admin.upgrade(
        '0xf3f98086f7B61a32be4EdF8d8A4b964eC886BBcd',
        new_oracle_logic.address,
        {'from': admin}
    )
    new_oracle_logic.initialize(
        '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3',
        '0x5575552988A3A80504bBaeB1311674fCFd40aD4B',
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        '0x3C14e07Edd0dC67442FA96f1Ec6999c57E810a83',
        {'from': owner}
    )
    new_tool_logic = VaultCoreToolsV4.deploy({'from': owner})
    proxy_admin.upgrade(
        '0x0390C6c7c320e41fCe0e6F0b982D20A88660F473',
        new_tool_logic.address,
        {'from': admin}
    )
    new_tool_logic.initialize(
        '0x4c58845BeF21E772eeE8B370e378df64fA660CD3',
        {'from': owner}
    )

    interest_after = USDC_strategy.checkInterestEarned('0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8')
    # deploy buyBack
    buyback = Buyback.deploy(
        usds.address,
        vault_core.address,
        {'from': owner}
    )
    # configure buyback for USDC and CRV
    buyback.updateInputTokenInfo(
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        True,
        1,
        '0x0000000000000000000000000000000000000000',
        '0x0000000000000000000000000000000000000000',
        500,
        0,
        0,
        {'from': owner}
    )
    buyback.updateInputTokenInfo(
        '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        True,
        2,
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        '0x0000000000000000000000000000000000000000',
        500,
        500,
        0,
        {'from': owner}
    )
    buyback.updateInputTokenInfo(
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978', #CRV
        True,
        3,
        '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1', #WETh
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', #USDC
        3000,
        500,
        500,
        {'from': owner}
    )
    vault_core.updateCollateralInfo(
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        USDC_strategy.address,
        True,
        80,
        buyback.address,
        True,
        {'from': owner}
    )
    vault_core.updateStrategyRwdBuybackAddr(
        USDC_strategy.address,
        buyback.address,
        {'from': owner}
    )
    outflow_before = usds.totalBurnt()
    txn = vault_core.rebase({'from': owner})
    outflow_after = usds.totalBurnt()
    assert outflow_after == outflow_before
    assert interest_after > interest_before
    assert oracle.getSPAprice() > 0
