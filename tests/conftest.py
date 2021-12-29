#!/usr/bin/python3
import pytest
import eth_utils
import math
import os
import json
import brownie
from dotenv import load_dotenv

# load environment variables defined in .env
load_dotenv()

def ordered_tokens(token1, amount1, token2, amount2):
    if(token1.address.lower() < token2.address.lower()):
        return token1, amount1, token2, amount2
    return token2, amount2, token1, amount1

@pytest.fixture(scope="module", autouse=True)
def admin(accounts):
    return accounts[0]

@pytest.fixture(scope="module", autouse=True)
def owner_l1(accounts):
    if brownie.network.show_active() == 'rinkeby':
        return accounts.add(os.getenv('LOCAL_ACCOUNT_PRIVATE_KEY')) # minter
    return accounts[1]

@pytest.fixture(scope="module", autouse=True)
def gatewayL1():
    # rinkeby
    if brownie.network.show_active() == 'rinkeby':
        gateway = '0x917dc9a69f65dc3082d518192cd3725e1fa96ca2'
    else: # Ethereum mainnet
        gateway = '0xcEe284F754E854890e311e3280b767F80797180d'
    return gateway

@pytest.fixture(scope="module", autouse=True)
def spa_l1(SperaxToken, SperaxTokenL1, gatewayL1, owner_l1):
    # rinkeby:
    if brownie.network.show_active() == 'rinkeby':
        spa_l1_address = '0x7776B097f723eBbc8cd1a17f1fe253D11235cCE1'
        router = '0x70c143928ecffaf9f5b406f7f4fc28dc43d68380'
        cwd = os.getcwd()
        filepath = cwd + '/supporting_contracts/SperaxTokenABI.json'
        with open(filepath) as f:
            abi = json.load(f)
        # retrieve existing SPA contract
        spa = brownie.Contract.from_abi(
            'SperaxToken',
            spa_l1_address,
            abi
        )
    else:
        # Ethereum mainnet
        router = '0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef'
        # deploy SPA contract
        spa = SperaxToken.deploy(
            'Sperax L1',
            'SPAL1',
            1000000000, # initial supply
            {'from': owner_l1}
        )

    wspa = SperaxTokenL1.deploy(
        'Wrapped Sperax L1',
        'wSPAL1',
        spa.address,
        gatewayL1,
        router,
        {'from': owner_l1}
    )
    spa.setMintable(
        wspa.address,
        True,
        {'from': owner_l1}
    )
    return (wspa, spa)

@pytest.fixture(scope="module", autouse=True)
def usds1(USDsL1, gatewayL1, owner_l1):
    usds1 = USDsL1.deploy(
        {'from': owner_l1}
    )
    usds1.initialize(
        'USDs Layer 1',
        'USDs1',
        gatewayL1, # L1 bridge/gateway
        '0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef', # L1 router
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
    # Ethereum mainnet fork
    if brownie.network.show_active() in ['mainnet-fork', 'rinkeby']:
        weth_address = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    return brownie.interface.IWETH9(weth_address)

@pytest.fixture(scope="module", autouse=True)
def usdt(MockToken, owner_l2):
    if brownie.network.show_active() in ['mainnet-fork', 'arbitrum-rinkeby']:
        usdt_address = '0xdac17f958d2ee523a2206206994597c13d831ec7'
        return brownie.interface.IERC20(usdt_address)
    token = MockToken.deploy(
        "USDT Token",
        "USDT",
        int(6),
        {'from': owner_l2}
    )
    print("USDT: ", token.address)
    return brownie.interface.IERC20(token.address)


@pytest.fixture(scope="module", autouse=True)
def wbtc(MockToken, owner_l2):
    if brownie.network.show_active() in ['arbitrum-rinkeby']:
        wbtc_address = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599'
        return brownie.interface.IERC20(wbtc_address)

    token = MockToken.deploy(
        "WBTC Token",
        "WBTC",
        int(8),
        {'from': owner_l2}
    )
    print("WBTC: ", token.address)
    return brownie.interface.IERC20(token.address)

    return
@pytest.fixture(scope="module", autouse=True)
def usdc(MockToken, owner_l2):
    if brownie.network.show_active() == 'arbitrum-rinkeby':
        return brownie.interface.IERC20('0x09b98f8b2395d076514037ff7d39a091a536206c')
    token = MockToken.deploy(
        "USDc Token",
        "USDc",
        int(6),
        {'from': owner_l2}
    )
    print("USDC: ", token.address)
    return brownie.interface.IERC20(token.address)

@pytest.fixture(scope="module", autouse=True)
def dai():
    # Arbitrum-one mainnet:
    dai_address = '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1'

    return brownie.interface.IERC20(dai_address)


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
    TwoPoolStrategy,
    BuybackTwoHops,
    BuybackThreeHops,
    chainlink_flags,
    usdt,
    wbtc,
    weth,
    usdc,
    dai,
    Contract,
    admin,
    vault_fee,
    owner_l2,
    accounts,
):
    if brownie.network.show_active() in ['mainnet-fork', 'rinkeby']:
        print("NOTE: skip deploying contracts for Arbitrum (L2)")
        return

    # Arbitrum-one (mainnet):
    chainlink_usdc_price_feed = '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3'
    l2_gateway = '0x096760F208390250649E3e8763348E783AEF5562'

    # Arbitrum rinkeby:
    #chainlink_usdc_price_feed = '0xe020609A0C31f4F96dCBB8DF9882218952dD95c4'
    #l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'

    bancor = deploy_bancor(
        BancorFormula,
        owner_l2
    )

    (vault_proxy, core_proxy) = deploy_vault(
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
        usdc,
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

    oracle_proxy.initialize(
        chainlink_usdc_price_feed,
        spa.address,
        usdc.address,
        chainlink_flags,
        {'from': owner_l2}
    )

    vault_proxy.initialize(
        spa.address,
        core_proxy.address,
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

    oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )

    # configure stablecoin collaterals in vault and oracle
    configure_collaterals(
        vault_proxy,
        oracle_proxy,
        usdc,
        usdt,
        wbtc,
        weth,
        dai,
        owner_l2
    )

    if brownie.network.show_active() in ['arbitrum-main-fork', 'arbitrum-one']:
        (strategies, buybacks) = deploy_strategies(
            TransparentUpgradeableProxy,
            TwoPoolStrategy,
            BuybackTwoHops,
            BuybackThreeHops,
            vault_proxy,
            oracle_proxy,
            usds_proxy,
            usdc,
            usdt,
            wbtc,
            weth,
            Contract,
            proxy_admin,
            admin,
            owner_l2
        )

    amount = 10 * 10**18
    # here it's temporarily change Oralce for SPA from SPA-USDC to SPA-ETH
    # would suggest to use a mock token to mock USDC instead
    mintSPA(spa, amount, owner_l2, vault_proxy)
    deposit_weth(weth, owner_l2, accounts, amount)
    spa_usdc_pool =  create_uniswap_v3_pool(spa, usdc, int(100 * 10**18), int(100 * 10**6), 3000, owner_l2)

    return (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategies,
        buybacks,
        bancor
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
    core = VaultCoreTools.deploy(
        {'from': owner_l2}
    )
    proxy = TransparentUpgradeableProxy.deploy(
        core.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin},
    )
    core_proxy = Contract.from_abi("VaultCoreTools", proxy.address, VaultCoreTools.abi)
    core_proxy.initialize(
        bancor.address,
        {'from': owner_l2}
    )

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
    return (vault_proxy, core_proxy)


def deploy_oracle(
    Oracle,
    TransparentUpgradeableProxy,
    usdc,
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

def deploy_strategies(
    TransparentUpgradeableProxy,
    TwoPoolStrategy,
    BuybackTwoHops,
    BuybackThreeHops,
    vault_proxy,
    oracle_proxy,
    usds_proxy,
    usdc,
    usdt,
    wbtc,
    weth,
    Contract,
    proxy_admin,
    admin,
    owner_l2,
):
    # Arbitrum-one (mainnet):
    platform_address = '0x960ea3e3C7FB317332d990873d354E18d7645590'
    reward_token_address = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    crv_gauge_address = '0x97E2768e8E73511cA874545DC5Ff8067eB19B787'

    assets = [
        usdt,
        wbtc,
        weth,
    ]
    lp_tokens = [
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
        '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
    ]

    usdt_strategy = deploy_strategy(
        TransparentUpgradeableProxy,
        TwoPoolStrategy,
        vault_proxy,
        oracle_proxy,
        Contract,
        proxy_admin,
        admin,
        owner_l2,
    )
    usdt_strategy.initialize(
        platform_address,
        vault_proxy,
        reward_token_address,
        assets,
        lp_tokens,
        crv_gauge_address,
        0,
        oracle_proxy,
        {'from': owner_l2}
    )
    wbtc_strategy = deploy_strategy(
        TransparentUpgradeableProxy,
        TwoPoolStrategy,
        vault_proxy,
        oracle_proxy,
        Contract,
        proxy_admin,
        admin,
        owner_l2,
    )
    wbtc_strategy.initialize(
        platform_address,
        vault_proxy,
        reward_token_address,
        assets,
        lp_tokens,
        crv_gauge_address,
        1,
        oracle_proxy,
        {'from': owner_l2}
    )
    weth_strategy = deploy_strategy(
        TransparentUpgradeableProxy,
        TwoPoolStrategy,
        vault_proxy,
        oracle_proxy,
        Contract,
        proxy_admin,
        admin,
        owner_l2,
    )
    weth_strategy.initialize(
        platform_address,
        vault_proxy,
        reward_token_address,
        assets,
        lp_tokens,
        crv_gauge_address,
        2,
        oracle_proxy,
        {'from': owner_l2}
    )

    two_hops_buyback = deploy_buyback_two_hops(
        BuybackTwoHops,
        vault_proxy,
        usds_proxy,
        usdt,
        usdc,
        wbtc,
        weth,
        owner_l2
    )
    three_hops_buyback = deploy_buyback_three_hops(
        BuybackThreeHops,
        vault_proxy,
        usds_proxy,
        usdc,
        weth,
        owner_l2
    )

    configure_vault(
        usdt,
        wbtc,
        weth,
        vault_proxy,
        usdt_strategy,
        wbtc_strategy,
        weth_strategy,
        two_hops_buyback,
        three_hops_buyback,
        owner_l2
    )

    return ((
        usdt_strategy,
        wbtc_strategy,
        weth_strategy,
    ), (
        two_hops_buyback,
        three_hops_buyback
    ))

def deploy_strategy(
    TransparentUpgradeableProxy,
    TwoPoolStrategy,
    vault_proxy,
    oracle_proxy,
    Contract,
    proxy_admin,
    admin,
    owner_l2,
):
    strategy = TwoPoolStrategy.deploy(
        {'from': owner_l2}
    )
    proxy = TransparentUpgradeableProxy.deploy(
        strategy.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin}
    )
    strategy_proxy = Contract.from_abi(
        "TwoPoolStrategy",
        proxy.address,
        TwoPoolStrategy.abi
    )

    return strategy_proxy

def deploy_buyback_two_hops(
    BuybackTwoHops,
    vault_proxy,
    usds_proxy,
    usdt,
    usdc,
    wbtc,
    weth,
    owner_l2
):
    buyback = BuybackTwoHops.deploy(
        usds_proxy.address,
        vault_proxy.address,
        {'from': owner_l2}
    )
    buyback.updateInputTokenInfo(
        usdt,
        True, # supported
        usdc,
        500,
        500,
        {'from': owner_l2}
    )
    buyback.updateInputTokenInfo(
        wbtc,
        True, # supported
        usdc,
        3000,
        500,
        {'from': owner_l2}
    )
    buyback.updateInputTokenInfo(
        weth,
        True, # supported
        usdc,
        10000,
        500,
        {'from': owner_l2}
    )
    return buyback

def deploy_buyback_three_hops(
    BuybackThreeHops,
    vault_proxy,
    usds_proxy,
    usdc,
    weth,
    owner_l2
):
    buyback = BuybackThreeHops.deploy(
        usds_proxy.address,
        vault_proxy.address,
        {'from': owner_l2}
    )
    crv_address = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    buyback.updateInputTokenInfo(
        crv_address,
        True, # supported
        weth,
        usdc,
        3000,
        500,
        500,
        {'from': owner_l2}
    )
    return buyback

def configure_vault(
    usdt,
    wbtc,
    weth,
    vault_proxy,
    usdt_strategy,
    wbtc_strategy,
    weth_strategy,
    two_hops_buyback,
    three_hops_buyback,
    owner_l2
):
    vault_proxy.addStrategy(
        usdt_strategy,
        {'from': owner_l2}
    )
    vault_proxy.addStrategy(
        wbtc_strategy,
        {'from': owner_l2}
    )
    vault_proxy.addStrategy(
        weth_strategy,
        {'from': owner_l2}
    )
    vault_proxy.updateStrategyRwdBuybackAddr(
        usdt_strategy,
        three_hops_buyback.address,
        {'from': owner_l2}
    )
    vault_proxy.updateStrategyRwdBuybackAddr(
        wbtc_strategy,
        three_hops_buyback.address,
        {'from': owner_l2}
    )
    vault_proxy.updateStrategyRwdBuybackAddr(
        weth_strategy,
        three_hops_buyback.address,
        {'from': owner_l2}
    )
    vault_proxy.updateCollateralInfo(
        usdt,
        usdt_strategy,
        True,
        80,
        two_hops_buyback.address,
        True,
        {'from': owner_l2}
    )
    vault_proxy.updateCollateralInfo(
        wbtc,
        wbtc_strategy,
        True,
        80,
        two_hops_buyback.address,
        True,
        {'from': owner_l2}
    )
    vault_proxy.updateCollateralInfo(
        weth,
        weth_strategy,
        True,
        80,
        two_hops_buyback.address,
        True,
        {'from': owner_l2}
    )


def configure_collaterals(
    vault_proxy,
    oracle_proxy,
    usdc,
    usdt,
    wbtc,
    weth,
    dai,
    owner_l2
):
    if brownie.network.show_active() in ['mainnet-fork', 'rinkeby']:
        print("NOTE: skip deploying contracts for Arbitrum (L2)")
        return

    # Arbitrum mainnet collaterals: token address, chainlink
    collaterals = {
        usdc: '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3',
        usdt: '0x3f3f5dF88dC9F13eac63DF89EC16ef6e7E25DdE7',
        # DAI
        dai: '0xc5C8E77B397E531B8EC06BFb0048328B30E9eCfB',
        wbtc: '0x6ce185860a4963106506C203335A2910413708e9',
        weth: '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612',
    }

    precision = 10**8
    zero_address = brownie.convert.to_address('0x0000000000000000000000000000000000000000')
    for collateral, chainlink in collaterals.items():
        print("collateral", collateral)
        # authorize a new collateral
        vault_proxy.addCollateral(
            collateral, # address of: USDC, USDT, DAI or WBTC
            zero_address, # _defaultStrategyAddr: CURVE, AAVE, etc
            False, # _allocationAllowed
            0, # _allocatePercentage
            zero_address, # _buyBackAddr
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


def create_uniswap_v3_pool(
    token1,
    token2,
    amount1,
    amount2,
    fee,
    owner
):
    position_mgr_address = '0xC36442b4a4522E871399CD717aBDD847Ab11FE88'
    position_mgr = brownie.interface.INonfungiblePositionManager(position_mgr_address)

    t1, a1, t2, a2 = ordered_tokens(token1, amount1, token2, amount2)
    print("t1: ", t1)
    print("a1: ", a1)
    print("t2: ", t2)
    print("a2: ", a2)
    # approve uniswap's non fungible position manager to transfer our tokens
    t1.approve(position_mgr.address, a1, {'from': owner})
    t2.approve(position_mgr.address, a2, {'from': owner})

    # create a transaction pool
    pool = position_mgr.createAndInitializePoolIfNecessary(
        t1,
        t2,
        fee,
        encode_price(a1, a2),
        {'from': owner}
    )

    deadline = 1637632800 + brownie.chain.time() # deadline: 2 hours
    params = [
        t1,
        t2,
        fee,
        lower_tick(), # tickLower
        upper_tick(), # tickUpper
        a1,
        a2,
        0, # minimum amount of spa expected
        0, # minimum amount of token2 expected
        owner,
        deadline
    ]
    txn = position_mgr.mint(
        params,
        {'from': owner}
    )


    return pool.return_value


def mintSPA(
    spa,
    amount,
    owner_l2,
    vault_proxy
):
    if brownie.network.show_active() in ['mainnet-fork', 'rinkeby']:
        print("NOTE: skip deploying contracts for Arbitrum (L2)")
        return

    # make owner allowed to mint SPA tokens
    txn = spa.setMintable(
        owner_l2.address,
        True,
        {'from': owner_l2}
    )

    assert txn.events['Mintable']['account'] == owner_l2.address

    txn = spa.mintForUSDs(
        owner_l2,
        amount,
        {'from': owner_l2}
    )
    assert txn.events['Transfer']['to'] == owner_l2
    assert txn.events['Transfer']['value'] == amount

def update_oracle_setting(oracle_proxy, usdc, owner_l2, spa, usds_proxy):
    if brownie.network.show_active() in ['mainnet-fork', 'rinkeby']:
        print("NOTE: skip deploying contracts for Arbitrum (L2)")
        return

    oracle_proxy.updateUniPoolsSetting(
        usdc.address,
        usdc.address,
        3000,
        3000,
    {'from': owner_l2} )


def deposit_weth(weth, owner_l2, accounts, amount):
    txn = weth.deposit({'from': owner_l2, 'amount': amount})
    weth_erc20 = brownie.interface.IERC20(weth.address)
    # transfer weth to strategy_proxy contract
    txn = weth_erc20.transfer(accounts[5],
                            amount, {'from': owner_l2})

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
