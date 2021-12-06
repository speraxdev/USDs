#!/usr/bin/python3
import pytest
import eth_utils
import math
import os
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
        '0xcEe284F754E854890e311e3280b767F80797180d', # L1 bridge
        '0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef', # L1 router
        {'from': owner_l1}
    )
    return usds1

@pytest.fixture(scope="module", autouse=True)
def mock_token1(MockToken, owner_l2):
    return MockToken.deploy(
        {'from': owner_l2}
    )

@pytest.fixture(scope="module", autouse=True)
def mock_token2(MockToken, owner_l2):
    return MockToken.deploy(
        {'from': owner_l2}
    )

@pytest.fixture(scope="module", autouse=True)
def mock_token3(MockToken, owner_l2):
    return MockToken.deploy(
        {'from': owner_l2}
    )

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
def chainlink_flags():
    # Arbitrum-rinkeby testnet:
    #return '0x491B1dDA0A8fa069bbC1125133A975BF4e85a91b'
    # Arbitrum-one mainnet:
    return '0x3C14e07Edd0dC67442FA96f1Ec6999c57E810a83'

@pytest.fixture(scope="module", autouse=True)
def weth():
    # Arbitrum-one mainnet:
    weth_address = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
    # Arbitrum-rinkeby testnet:
    #weth_address = '0xB47e6A5f8b33b3F17603C83a0535A9dcD7E32681'
    return brownie.interface.IWETH9(weth_address)

@pytest.fixture(scope="module", autouse=True)
def usdt():
    # Arbitrum-one mainnet:
    usdt_address = '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'
    return brownie.interface.IERC20(usdt_address)

@pytest.fixture(scope="module", autouse=True)
def wbtc():
    # Arbitrum-one mainnet:
    wbtc_address = '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f'
    return brownie.interface.IERC20(wbtc_address)

@pytest.fixture(scope="module", autouse=True)
def proxy_admin(
    ProxyAdmin,
    admin
):
    # admin contract
    return ProxyAdmin.deploy(
        {'from': admin}
    )

@pytest.fixture(scope="module", autouse=True)
def sperax(
    proxy_admin,
    TransparentUpgradeableProxy,
    BancorFormula,
    VaultCoreTools,
    USDsL2,
    SperaxTokenL2,
    Oracle,
    VaultCore,
    usds1,
    ThreePoolStrategy,
    BuybackSingle,
    BuybackMultihop,
    chainlink_flags,
    usdt,
    wbtc,
    weth,
    mock_token1,
    mock_token2,
    mock_token3,
    Contract,
    admin,
    vault_fee,
    owner_l2,
    interface,
):
    # Arbitrum-one (mainnet):
    chainlink_eth_price_feed = '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612'
    l2_gateway = '0x096760F208390250649E3e8763348E783AEF5562'
    chainlink_flags = '0x3C14e07Edd0dC67442FA96f1Ec6999c57E810a83'

    # Arbitrum rinkeby:
    #chainlink_eth_price_feed = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    #l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'

    bancor = deploy_bancor(
        BancorFormula,
        owner_l2
    )

    (vault_proxy, vault_core_tools) = deploy_vault(
        VaultCoreTools,
        VaultCore,
        TransparentUpgradeableProxy,
        bancor,
        Contract,
        proxy_admin,
        admin,
        owner_l2
    )

    oracle_proxy = deploy_oracle(
        Oracle,
        TransparentUpgradeableProxy,
        Contract,
        proxy_admin,
        admin,
        owner_l2
    )

    usds_proxy = deploy_usds(
        USDsL2,
        TransparentUpgradeableProxy,
        Contract,
        vault_proxy,
        l2_gateway,
        usds1,
        proxy_admin,
        admin,
        owner_l2
    )

    #wrapper_spa1_address = os.environ.get('WRAPPER_SPA1_ADDRESS')
    wrapper_spa1_address = '0xB4A3B0Faf0Ab53df58001804DdA5Bfc6a3D59008'
    spa = SperaxTokenL2.deploy(
        'Sperax L2',
        'SPAL2',
        l2_gateway,
        wrapper_spa1_address, # wrapper SPA L1
        {'from': owner_l2},
    )

    strategy_proxy = deploy_strategy(
        TransparentUpgradeableProxy,
        ThreePoolStrategy,
        vault_proxy,
        usdt,
        wbtc,
        weth,
        Contract,
        proxy_admin,
        admin,
        owner_l2
    )

    buyback = deploy_buyback(
        BuybackSingle,
        vault_proxy,
        spa,
        usds_proxy,
        1, # pool_fee
        owner_l2
    )

    oracle_proxy.initialize(
        chainlink_eth_price_feed,
        spa.address,
        weth.address,
        chainlink_flags,
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
        oracle_proxy.address,
        {'from': owner_l2}
    )

    # configure stablecoin collaterals in vault and oracle
    configure_collaterals(
        vault_proxy,
        oracle_proxy,
        buyback,
        usdt,
        wbtc,
        owner_l2
    )

    create_uniswap_v3_pool(
        mock_token1, # token1
        mock_token1.balanceOf(owner_l2), # amount1
        mock_token2, # token2
        mock_token2.balanceOf(owner_l2), # amount2
        owner_l2
    )

    return (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    )


def deploy_bancor(
    BancorFormula,
    owner_l2
):
    bancor = BancorFormula.deploy(
        {'from': owner_l2}
    )
    bancor.init()
    return bancor


def deploy_vault(
    VaultCoreTools,
    VaultCore,
    TransparentUpgradeableProxy,
    bancor,
    Contract,
    proxy_admin,
    admin,
    owner_l2
):
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
    return (vault_proxy, vault_core_tools)


def deploy_oracle(
    Oracle,
    TransparentUpgradeableProxy,
    Contract,
    proxy_admin,
    admin,
    owner_l2
):
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
    return oracle_proxy


def deploy_usds(
    USDsL2,
    TransparentUpgradeableProxy,
    Contract,
    vault_proxy,
    l2_gateway,
    usds1,
    proxy_admin,
    admin,
    owner_l2
):
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
    return usds_proxy


def deploy_strategy(
    TransparentUpgradeableProxy,
    ThreePoolStrategy,
    vault_proxy,
    usdt,
    wbtc,
    weth,
    Contract,
    proxy_admin,
    admin,
    owner_l2,
):
    # Arbitrum-one (mainnet):
    platform_address = '0xF97c707024ef0DD3E77a0824555a46B622bfB500'
    reward_token_address = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    crv_gauge_address = '0x97E2768e8E73511cA874545DC5Ff8067eB19B787'

    assets = [
        usdt,
        wbtc,
        weth,
    ]

    p_tokens = [
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
    ]

    # THREE POOL strategy
    strategy = ThreePoolStrategy.deploy(
        {'from': owner_l2}
    )
    proxy = TransparentUpgradeableProxy.deploy(
        strategy.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin}
    )
    strategy_proxy = Contract.from_abi(
        "ThreePoolStrategy",
        proxy.address,
        ThreePoolStrategy.abi
    )
    strategy_proxy.initialize(
        platform_address,
        vault_proxy,
        reward_token_address,
        assets,
        p_tokens,
        crv_gauge_address,
        weth.address,
        {'from': owner_l2}
    )
    return strategy_proxy


def deploy_buyback(
    BuybackSingle,
    vault_proxy,
    spa,
    usds_proxy,
    pool_fee,
    owner_l2
):
    buyback = BuybackSingle.deploy(
        mock_token1.address, # token1
        vault_proxy.address,
        {'from': owner_l2}
    )
    pool_fee = 3000
    buyback.updateInputTokenInfo(
        mock_token2.address, # token2
        True, # supported
        pool_fee,
        {'from': owner_l2}
    )

    buyback_multihop  =  BuybackMultihop.deploy(
        mock_token1.address, # token1
        vault_proxy.address,
        {'from': owner_l2}
    )
    pool_fee1 = 3000
    pool_fee2 = 3000
    #(address _inputTokenAddr, bool _supported, address _intermediateToken, uint24 _poolFee1, uint24 _poolFee2)
    buyback_multihop.updateInputTokenInfo(
        mock_token2.address,
        True, #supported
        mock_token3.address, #_intermediateToken
        pool_fee1,
        pool_fee2
    )
        
    oracle_proxy.initialize(
        chainlink_eth_price_feed,
        spa.address,
        weth.address,
        chainlink_flags,
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
    configure_collaterals(
        vault_proxy,
        oracle_proxy,
        buyback,
        owner_l2
    )

    tranfer_mock_token_to_vault(
        owner_l2,
        vault_proxy,
        mock_token2
    )

    amount = 100000
    create_uniswap_v3_pool(
        mock_token1, # token1
        amount, # amount1
        mock_token2, # token2
        amount, # amount2
        owner_l2
    )

    create_uniswap_v3_pool(
        mock_token1, # token1
        amount, # amount1
        mock_token3, # token3
        amount, # amount2
        owner_l2
    )

    create_uniswap_v3_pool(
        mock_token2, # token2
        amount, # amount1
        mock_token3, # token3
        amount, # amount2
        owner_l2
    )

    # THREE POOL STRATEGY
    # Arbitrum-one (mainnet):
    platform_address = '0xF97c707024ef0DD3E77a0824555a46B622bfB500'
    reward_token_address = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    crv_gauge_address = '0x97E2768e8E73511cA874545DC5Ff8067eB19B787'
    crv_minter_address = '0xd061D61a4d941c39E5453435B6345Dc261C2fcE0'

    assets = [
        # USDT
        '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        # WBTC 
        '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
        # WETH
        '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
    ]

    p_tokens = [
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
        ]

    strategy = ThreePoolStrategy.deploy(
        {'from': owner_l2}
    )

    strategy.initialize(
        platform_address,
        vault_proxy.address,
        reward_token_address,
        assets,
        p_tokens,
        crv_gauge_address,
        crv_minter_address,
        {'from': owner_l2}
    )

    return (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback, buyback_multihop)

def configure_collaterals(
    vault_proxy,
    oracle_proxy,
    buyback,
    usdt,
    wbtc,
    owner_l2
):
    # Arbitrum mainnet collaterals: token address, chainlink
    collaterals = {
        # USDC
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8': '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3',
        # USDT
        usdt: '0x3f3f5dF88dC9F13eac63DF89EC16ef6e7E25DdE7',
        # DAI
        '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1': '0xc5C8E77B397E531B8EC06BFb0048328B30E9eCfB',
        # WBTC
        wbtc: '0x6ce185860a4963106506C203335A2910413708e9',
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
            buyback, # _buyBackAddr
            False, # _rebaseAllowed
            {'from': owner_l2}
        )
        # wire up price feed for the added collateral
        oracle_proxy.updateCollateralInfo(
            collateral, # ERC20 address
            True, # supported
            chainlink, # chainlink price feed address
            precision, # chainlink price feed precision
            {'from': owner_l2}
        )

# create pool for pair tokens (input parameters) on Arbitrum-one
# To obtain the interface to INonfungiblePositionManager required
# copying the following files from @uniswap-v3-periphery@1.3.0:
#
# - contracts/interface/IERC721Permit.sol
# - contracts/interface/INonfungiblePositionManager.sol
# - contracts/interface/IPeripheryImmutableState.sol
# - contracts/interface/IPeripheryPayments.sol
# - contracts/interface/IPoolInitializer.sol
# - contracts/libraries/PoolAddress.sol
def create_uniswap_v3_pool(
    token1,
    amount1,
    token2,
    amount2,
    owner_l2
):
    position_mgr_address = '0xC36442b4a4522E871399CD717aBDD847Ab11FE88'
    position_mgr = brownie.interface.INonfungiblePositionManager(position_mgr_address)

    # approve uniswap's non fungible position manager to transfer our tokens
    token1.approve(position_mgr.address, amount1, {'from': owner_l2})
    token2.approve(position_mgr.address, amount2, {'from': owner_l2})

    # create a transaction pool
    fee = 3000
    txn = position_mgr.createAndInitializePoolIfNecessary(
        token1,
        token2,
        fee,
        encode_price(amount1, amount2),
        {'from': owner_l2}
    )
    # newly created pool address
    pool = txn.return_value
    print(f"uniswap v3 pool address (token1-token2 pair): {pool}")

    # provide initial liquidity
    deadline = 1637632800 + brownie.chain.time() # deadline: 2 hours
    params = [
        token1,
        token2,
        fee,
        lower_tick(), # tickLower
        upper_tick(), # tickUpper
        amount1,
        amount2,
        0, # minimum amount of token1 expected
        0, # minimum amount of token2 expected
        owner_l2,
        deadline
    ]
    txn = position_mgr.mint(
        params,
        {'from': owner_l2, 'allow_revert' : True}
    )
    print(txn.return_value)

def tranfer_mock_token_to_vault(owner_l2, vault_proxy, token1):
    amount = 1000000000000000000000000000
    token1.approve(vault_proxy.address, amount, {'from': owner_l2})
    token1.transfer(vault_proxy.address, amount, {'from': owner_l2})
    print("vault_proxy balance", token1.balanceOf(vault_proxy.address))
    
def lower_tick():
    return math.ceil(-887272 / 60) * 60

def upper_tick():
    return math.floor(887272 / 60) * 60

def encode_price(n1, n2):
    return math.trunc(math.sqrt(int(n1)/int(n2)) * 2**96)


@pytest.fixture(autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass
