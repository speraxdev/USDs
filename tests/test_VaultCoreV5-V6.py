# To-do: add test cases for interest_upperBound after TwpPoolStrategyV3
#        implemented

import pytest
import brownie

CRV_threshold = 1*10**18
interest_upperBound = 1000*10**6

# test on: VaultCoreV5 to V6
def upgrade(VaultCoreV6, ProxyAdmin):
    admin = '0x42d2f9f84EeB86574aA4E9FCccfD74066d809600'
    owner = '0xc28c6970D8A345988e8335b1C229dEA3c802e0a6'
    proxy_admin = brownie.Contract.from_abi(
        'ProxyAdmin',
        '0x3E49925A79CbFb68BAa5bc9DFb4f7D955D1ddF25',
        ProxyAdmin.abi
    )
    new_vault_logic = VaultCoreV6.deploy({'from': owner})
    proxy_admin.upgrade(
        '0xF783DD830A4650D2A8594423F123250652340E3f', #VaultCore
        new_vault_logic.address,
        {'from': admin}
    )
    new_vault_logic.initialize(
        '0x5575552988A3A80504bBaeB1311674fCFd40aD4B', #SperaxTokenL2
        '0x0390C6c7c320e41fCe0e6F0b982D20A88660F473', #VaultCoreTools
        '0x4F987B24bD2194a574bB3F57b4e66B7f7eD36196', #fee vault
        {'from': owner}
    )


# assumption: Some CRV available to claim on USDC_strategy
def test_rewardUpgrade(TwoPoolStrategyV2, VaultCoreV5, VaultCoreV6, ProxyAdmin):
    if brownie.network.show_active() != 'arbitrum-main-fork':
        raise ValueError('Not on arbitrum-main-fork')

    admin = '0x42d2f9f84EeB86574aA4E9FCccfD74066d809600'
    owner = '0xc28c6970D8A345988e8335b1C229dEA3c802e0a6'
    vaultCore = '0xF783DD830A4650D2A8594423F123250652340E3f'
    usdc =  brownie.interface\
        .IERC20('0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8')
    usdt =  brownie.interface\
        .IERC20('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')
    crv = brownie.interface.IERC20('0x11cdb42b0eb46d95f990bedd4695a6e3fa034978')
    pool = brownie.interface\
        .ICurve2PoolV2('0x7f90122bf0700f9e7e1f688fe926940e8839f353')
    gauge =  brownie.interface\
        .ICurveGauge('0xbF7E49483881C76487b0989CD7d9A8239B20CA41')
    vaultCore = brownie.Contract.from_abi(
        'VaultCore',
        '0xF783DD830A4650D2A8594423F123250652340E3f',
        VaultCoreV5.abi
    )
    USDC_strategy = brownie.Contract.from_abi(
        'USDC_strategy',
        '0xbF82a3212e13b2d407D10f5107b5C8404dE7F403',
        TwoPoolStrategyV2.abi # Change to V3 later
    )
    USDT_strategy = brownie.Contract.from_abi(
        'USDT_strategy',
        '0xdc118F2F00812326Fe0De5c9c74c1c0c609d1eB4',
        TwoPoolStrategyV2.abi # Change to V3 later
    )

    USDC_claimable_CRV = gauge.claimable_reward(USDC_strategy, crv)
    if USDC_claimable_CRV < CRV_threshold:
        raise ValueError('Not enough CRV claimable (on USDC strategy)')

    brownie.chain.snapshot()
    txn =  vaultCore.rebase({'from': owner})
    # CRV that would have been claimed by USDC_contract (before upgrade)
    crvReceived = txn.events['RewardTokenCollected'][0]['amount']
    crvReserved = crv.balanceOf('0x6d5240f086637fb408c7F727010A10cf57D51B62')
    assert crvReserved == 0
    brownie.chain.revert()
    upgrade(VaultCoreV6, ProxyAdmin)
    USDC_strategy.setRewardLiquidationThreshold(
        CRV_threshold,
        {'from': owner}
    )
    USDC_strategy.setInterestLiquidationThreshold(
        interest_upperBound,
        {'from': owner}
    )
    USDT_strategy.setInterestLiquidationThreshold(
        interest_upperBound,
        {'from': owner}
    )
    vaultCore.rebase({'from': owner})
    # Keep the address below updated yp the rwdReserve being used
    crvReserved = crv.balanceOf('0x6d5240f086637fb408c7F727010A10cf57D51B62')
    assert crvReserved == crvReceived - CRV_threshold
