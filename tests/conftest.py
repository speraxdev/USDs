#!/usr/bin/python3
import os
import pytest
import eth_utils
import brownie 

@pytest.fixture(scope="module", autouse=True)
def admin(accounts):
    return accounts[0]

@pytest.fixture(scope="module", autouse=True)
def owner_l1(accounts):
    return accounts[1]

@pytest.fixture(scope="module", autouse=True)
def usds1(USDsL1, owner_l1):
    usds1 = USDsL1.deploy(
        {'from': owner_l1}
    )
    usds1.initialize(
        'USDs Layer 1',
        'USDs1',
        {'from': owner_l1}
    )
    return usds1


@pytest.fixture(scope="module", autouse=True)
def owner_l2(accounts):
    return accounts[2]

@pytest.fixture(scope="module", autouse=True)
def vault_fee(accounts):
    return accounts[3]

@pytest.fixture(scope="module", autouse=True)
def user_account(accounts):
    return accounts[4]

@pytest.fixture(scope="module", autouse=True)
def user_account_with_no_balance(accounts):
    return accounts[5]

@pytest.fixture(scope="module", autouse=True)
def weth(interface, chain):
    # Arbitrum-one mainnet:
    weth_address = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
    # Arbitrum-rinkeby testnet:
    #weth_address = '0xB47e6A5f8b33b3F17603C83a0535A9dcD7E32681'
    return interface.IERC20(weth_address)

@pytest.fixture(scope="module", autouse=True)
def sol(interface):
    sol_address = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
    return interface.IERC20(sol_address)

@pytest.fixture(scope="module", autouse=True)
def uniswap_v3_swap_router(interface):
    return interface.ISwapRouter('0xE592427A0AEce92De3Edee1F18E0157C05861564')

@pytest.fixture(scope="module", autouse=True)
def invalid_token(interface):
    sol_address = '0x82af49447d8a07e3bd95bd0d56f35241523fbab2'
    return interface.IERC20(sol_address)

@pytest.fixture(scope="module", autouse=True)
def buyback_single_sol_spa(BuybackSingle, owner_l2, uniswap_v3_swap_router, sol, spa, vault_proxy):
    return BuybackSingle.deploy(
        uniswap_v3_swap_router,
        sol.address, 
        spa.address, 
        vault_proxy.address, 
        3000, {"from":  owner_l2}
    )


@pytest.fixture(scope="module", autouse=True)
def buyback_single_spa_weth_pf05(BuybackSingle, owner_l2, uniswap_v3_swap_router, sol, weth, vault_proxy):
    return BuybackSingle.deploy(
        uniswap_v3_swap_router,
        sol.address, 
        weth.address, 
        vault_proxy.address, 
        50000, {"from": owner_l2}
    )

@pytest.fixture(scope="module", autouse=True)
def buyback_multihop_usdt_sol_weth(BuybackMultihop, owner_l2, uniswap_v3_swap_router, sol, weth, usds, vault_proxy): 
    return BuybackMultihop.deploy(
        uniswap_v3_swap_router,
        weth.address,
        usds.address, 
        sol.address, 
        vault_proxy.address, 
        3000, 
        3000,
        {"from": owner_l2}
    )

@pytest.fixture(scope="module", autouse=True)
def buyback_multihop_usdt_spa_weth_pf50(BuybackMultihop, owner_l2, uniswap_v3_swap_router, spa, weth, usds, vault_proxy): 
    return BuybackMultihop.deploy(
        uniswap_v3_swap_router,
        weth.address,
        usds.address, 
        spa.address, 
        vault_proxy.address, 
        50000, 
        50000,
        {"from": owner_l2}
    )


@pytest.fixture(scope="module", autouse=True)
def buyback_multihop_usdt_invalid_token_weth(BuybackMultihop, owner_l2, uniswap_v3_swap_router, invalid_token, weth, usds, vault_proxy): 
    return BuybackMultihop.deploy(
        uniswap_v3_swap_router,
        weth.address,
        usds.address, 
        invalid_token.address, 
        vault_proxy.address, 
        3000, 
        3000,
        {"from": owner_l2}
    )

@pytest.fixture(scope="module", autouse=True)
def sperax(
    ProxyAdmin,
    TransparentUpgradeableProxy,
    BancorFormula,
    VaultCoreTools,
    USDsL2,
    SperaxTokenL2,
    Oracle,
    VaultCore,
    usds1,
    BuybackSingle,
    BuybackMultihop,
    weth,
    Contract,
    admin,
    vault_fee,
    owner_l2,
    interface,
):
    # Arbitrum-one (mainnet):
    chainlink_eth_price_feed = '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612'
    l2_gateway = '0x096760F208390250649E3e8763348E783AEF5562'
    uniswap_v3_swap_router = interface.ISwapRouter('0xE592427A0AEce92De3Edee1F18E0157C05861564')

    # Arbitrum rinkeby:
    #chainlink_eth_price_feed = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    #l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'
    #uniswap_v3_swap_router = interface.ISwapRouter('0x9413AD42910c1eA60c737dB5f58d1C504498a3cD')

    # admin contract
    proxy_admin = ProxyAdmin.deploy(
        {'from': admin}
    )

    bancor = BancorFormula.deploy(
        {'from': owner_l2}
    )
    bancor.init()

    vault_core_tools = VaultCoreTools.deploy(
        {'from': owner_l2}
    )
    vault_core_tools.initialize(bancor.address)

    vault = VaultCore.deploy(
        {'from': owner_l2}
    )
    proxy = TransparentUpgradeableProxy.deploy(
        vault.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin}
    )
    vault_proxy = Contract.from_abi("VaultCore", proxy.address, VaultCore.abi)

    oracle = Oracle.deploy(
        {'from': owner_l2}
    )
    proxy = TransparentUpgradeableProxy.deploy(
        oracle.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin}
    )
    oracle_proxy = Contract.from_abi("Oracle", proxy.address, Oracle.abi)

    usds = USDsL2.deploy(
        {'from': owner_l2}
    )
    proxy = TransparentUpgradeableProxy.deploy(
        usds.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin}
    )
    usds_proxy = Contract.from_abi("USDsL2", proxy.address, USDsL2.abi)
    usds_proxy.initialize(
        'USDs Layer 2',
        'USDs2',
        vault_proxy.address, 
        l2_gateway,
        usds1.address,
        {'from': owner_l2}
    )

    spa = SperaxTokenL2.deploy(
        'Sperax',
        'SPA',
        l2_gateway,
        usds_proxy.address,
        {'from': owner_l2},
    )

    # not sure if this is valid
    pool_fee = 3000

    buyback = BuybackSingle.deploy(
        uniswap_v3_swap_router, # uniswap v.3 router address
        usds_proxy.address,
        weth.address, # input token
        vault_proxy.address,
        pool_fee,
        {'from': owner_l2}
    )


    buyback_multihop = BuybackMultihop.deploy(
        uniswap_v3_swap_router,
        weth.address,
        usds_proxy.address, 
        spa.address, 
        vault_proxy.address, 
        pool_fee, 
        pool_fee,
        {"from": owner_l2}
    )

    oracle_proxy.initialize(
        chainlink_eth_price_feed,
        spa.address,
        weth.address,
        {'from': owner_l2}
    )
    oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )

    vault_proxy.initialize(
        spa.address,
        vault_core_tools.address,
        vault_fee,
        {'from': owner_l2}
    )
    vault_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )
    vault_proxy.updateOracleAddress(
        oracle.address,
        {'from': owner_l2}
    )
    
    # configure stablecoin collaterals in vault and oracle
    #configure_collaterals(vault_proxy, oracle_proxy, owner_l2, convert)

    return (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop)


def configure_collaterals(
    vault_proxy,
    oracle_proxy,
    owner_l2
):
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
    zero_address = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    for collateral, chainlink in collaterals.items():
        # authorize a new collateral
        vault_proxy.addCollateral(
            collateral, # address of: USDC, USDT, DAI or WBTC
            zero_address, # _defaultStrategyAddr: CURVE, AAVE, etc
            False, # _allocationAllowed
            0, # _allocatePercentage
            zero_address, # _buyBackAddr
            False, # _rebaseAllowed
            {'from': owner_l2, 'gas_limit': 1000000000}
        )
        # wire up price feed for the added collateral
        oracle_proxy.updateCollateralInfo(
            collateral, # ERC20 address
            True, # supported
            chainlink, # chainlink price feed address
            precision, # chainlink price feed precision
            {'from': owner_l2, 'gas_limit': 1000000000}
        )

# create pool for pair tokens (input parameters) on Arbitrum-one
def configure_uniswap_v3_pool(
    token1,
    token2
):
    pass