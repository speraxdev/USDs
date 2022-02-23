import pytest
import brownie

# test on: TwoPoolStrategyV2 to TwoPoolStrategyV3
# assumption: now both strategies do not have interest
# then after the upgrade, rebase should not redeem any lp token
def test_upgrade(ProxyAdmin, TwoPoolStrategyV3, Oracle, VaultCore):
    if brownie.network.show_active() != 'arbitrum-main-fork':
        raise ValueError('Not on arbitrum-main-fork')
    # addresses
    admin = '0x42d2f9f84EeB86574aA4E9FCccfD74066d809600'
    owner = '0xc28c6970D8A345988e8335b1C229dEA3c802e0a6'
    usdc =  brownie.interface.IERC20('0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8')
    usdt =  brownie.interface.IERC20('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')
    pool = brownie.interface.ICurve2PoolV2('0x7f90122bf0700f9e7e1f688fe926940e8839f353')
    gauge =  brownie.interface.ICurveGauge('0xbF7E49483881C76487b0989CD7d9A8239B20CA41')
    vaultCore = brownie.Contract.from_abi(
        'VaultCore',
        '0xF783DD830A4650D2A8594423F123250652340E3f',
        VaultCore.abi
    )
    oracle = brownie.Contract.from_abi(
        'oracle',
        '0xf3f98086f7B61a32be4EdF8d8A4b964eC886BBcd',
        Oracle.abi
    )
    usdc_price = oracle.getCollateralPrice(usdc)
    usdt_price = oracle.getCollateralPrice(usdt)
    proxy_admin = brownie.Contract.from_abi(
        'ProxyAdmin',
        '0x3E49925A79CbFb68BAa5bc9DFb4f7D955D1ddF25',
        ProxyAdmin.abi
    )
    USDC_strategy = brownie.Contract.from_abi(
        'USDC_strategy',
        '0xbF82a3212e13b2d407D10f5107b5C8404dE7F403',
        TwoPoolStrategyV3.abi
    )
    USDT_strategy = brownie.Contract.from_abi(
        'USDT_strategy',
        '0xdc118F2F00812326Fe0De5c9c74c1c0c609d1eB4',
        TwoPoolStrategyV3.abi
    )
    usdc_lp_balance_before = gauge.balanceOf(USDC_strategy)
    usdt_lp_balance_before = gauge.balanceOf(USDT_strategy)
    usdc_allocatedAmt_before = USDC_strategy.allocatedAmt(usdc)
    usdt_allocatedAmt_before = USDT_strategy.allocatedAmt(usdt)

    # assumption: now both strategies do not have interest
    assumption_hold = True
    # for USDC strategy
    pool.calc_withdraw_one_coin(usdc_lp_balance_before, 0)
    if pool.calc_withdraw_one_coin(usdc_lp_balance_before, 0) > usdc_allocatedAmt_before:
        raise ValueError('Assumption does not hold')
    elif pool.calc_withdraw_one_coin(usdc_lp_balance_before, 1) \
        * oracle.getCollateralPrice(usdt) \
        / oracle.getCollateralPrice(usdc) \
        > usdc_allocatedAmt_before:
        raise ValueError('Assumption does not hold')
    if pool.calc_withdraw_one_coin(usdt_lp_balance_before, 1) > usdt_allocatedAmt_before:
        raise ValueError('Assumption does not hold')
    elif pool.calc_withdraw_one_coin(usdt_lp_balance_before, 0) \
        * oracle.getCollateralPrice(usdc) \
        / oracle.getCollateralPrice(usdt) \
        > usdt_allocatedAmt_before:
        raise ValueError('Assumption does not hold')

    # upgrade everything
    new_usdc_strategy_logic = TwoPoolStrategyV3.deploy({'from': owner})
    new_usdt_strategy_logic = TwoPoolStrategyV3.deploy({'from': owner})
    proxy_admin.upgrade(
        USDC_strategy.address,
        new_usdc_strategy_logic.address,
        {'from': admin}
    )
    new_usdc_strategy_logic.initialize(
        '0x7f90122bf0700f9e7e1f688fe926940e8839f353',
        '0xF783DD830A4650D2A8594423F123250652340E3f',
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978',
        ['0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8','0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'],
        ['0x7f90122bf0700f9e7e1f688fe926940e8839f353','0x7f90122bf0700f9e7e1f688fe926940e8839f353'],
        '0xbF7E49483881C76487b0989CD7d9A8239B20CA41',
        0,
        '0xf3f98086f7B61a32be4EdF8d8A4b964eC886BBcd',
        {'from': owner}
    )
    proxy_admin.upgrade(
        USDT_strategy.address,
        new_usdt_strategy_logic.address,
        {'from': admin}
    )
    new_usdt_strategy_logic.initialize(
        '0x7f90122bf0700f9e7e1f688fe926940e8839f353',
        '0xF783DD830A4650D2A8594423F123250652340E3f',
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978',
        ['0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8','0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'],
        ['0x7f90122bf0700f9e7e1f688fe926940e8839f353','0x7f90122bf0700f9e7e1f688fe926940e8839f353'],
        '0xbF7E49483881C76487b0989CD7d9A8239B20CA41',
        1,
        '0xf3f98086f7B61a32be4EdF8d8A4b964eC886BBcd',
        {'from': owner}
    )
    vaultCore.rebase({'from': owner})
    usdc_lp_balance_after = gauge.balanceOf(USDC_strategy)
    usdt_lp_balance_after = gauge.balanceOf(USDT_strategy)
    usdc_allocatedAmt_after = USDC_strategy.allocatedAmt(usdc)
    usdt_allocatedAmt_after= USDT_strategy.allocatedAmt(usdt)
    assert usdc_lp_balance_before == usdc_lp_balance_after
    assert usdt_lp_balance_before == usdt_lp_balance_after
    assert usdc_allocatedAmt_before == usdc_allocatedAmt_after
    assert usdt_allocatedAmt_before == usdt_allocatedAmt_after