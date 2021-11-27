#!/usr/bin/python3
import pytest
import eth_utils
import brownie 
import math

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
def mock_usdc(MockUSDC, owner_l2):
    return MockUSDC.deploy(
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
def weth():
    # Arbitrum-one mainnet:
    weth_address = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
    # Arbitrum-rinkeby testnet:
    #weth_address = '0xB47e6A5f8b33b3F17603C83a0535A9dcD7E32681'
    return brownie.interface.IERC20(weth_address)

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
<<<<<<< HEAD
    CompoundStrategy,
    BuybackSingle,
    BuybackMultihop,
=======
    BuybackSingle,
    BuybackMultihop,
    weth,
>>>>>>> usdt_test
    Contract,
    admin,
    vault_fee,
    owner_l2,
    interface,
):
    # Arbitrum-one (mainnet):
    chainlink_eth_price_feed = '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612'
    l2_gateway = '0x096760F208390250649E3e8763348E783AEF5562'

    # Arbitrum rinkeby:
    #chainlink_eth_price_feed = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    #l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'

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

    buyback = BuybackSingle.deploy(
        usds_proxy.address, # token1
        vault_proxy.address,
        {'from': owner_l2}
    )
    pool_fee = 1
    buyback.updateInputTokenInfo(
        spa.address, # token2
        True, # supported
        pool_fee,
        {'from': owner_l2}
    )

    # mint USDs to owner_l2 for the uniswap pool
    amount = int(10000 * 10 ** 18)
    mint_usds(amount, spa, vault_proxy, owner_l2)

    create_uniswap_v3_pool(
        usds_proxy, # token1: USDS
        amount, # amount1
        mock_usdc, # token2
        mock_usdc.balanceOf(owner_l2), # amount2
        owner_l2
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
<<<<<<< HEAD

    # deploy strategy and buyback contracts
    strategy = CompoundStrategy.deploy(
        {'from': owner_l2}
    )
    proxy = TransparentUpgradeableProxy.deploy(
        strategy.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin}
    )
    strategy_proxy = Contract.from_abi(
        "CompoundStrategy",
        proxy.address,
        CompoundStrategy.abi
    )
    strategy_proxy.initialize(
        # platform address
        vault_proxy.address, # vault address
        # reward token address
        # assets
        # p tokens
        {'from': owner_l2}
    )

    return (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy)
=======
    
    # configure stablecoin collaterals in vault and oracle
    #configure_collaterals(vault_proxy, oracle_proxy, buyback, owner_l2)

    return (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback)


def configure_collaterals(
    vault_proxy,
    oracle_proxy,
    buyback,
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

def mint_usds(amount, spa, vault_proxy, owner_l2):
    # put owner_l2 into the mintableGroup of SPA
    txn = spa.setMintable(
        owner_l2,
        True,
        {'from': owner_l2}
    )
    assert txn.events['Mintable']['account'] == owner_l2

    txn = spa.mintForUSDs(
        owner_l2,
        amount,
        {'from': owner_l2}
    )
    print(f"mint SPA: {txn.events}")

    # set mintRedeemAllowed = True so mint function succeeds
    txn = vault_proxy.updateMintBurnPermission(
        True,
        {'from': owner_l2}
    )
    assert txn.events['MintRedeemPermssionChanged']['permission'] == True

    deadline = 1637632800 + brownie.chain.time() # deadline: 2 hours
    # mint USDs by specifying amount of SPA to burn
    txn = vault_proxy.mintWithSPA(
        spa.address,
        amount,
        0, # USDs slippage
        1, # collateral slippage
        deadline,
        {'from': owner_l2}
    )
    assert txn.events['USDsMinted']['wallet'] == owner_l2
    assert txn.events['USDsMinted']['USDsAmt'] == amount

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
    print(f"pool: {pool.address}")
    
    # provide initial liquidity
    fee = 300
    deadline = 1637632800 + brownie.chain.time() # deadline: 2 hours
    params = [
        token1,
        token2,
        fee,
        get_lower_tick(), # tickLower
        get_upper_tick(), # tickUpper
        amount1,
        amount2,
        0, # minimum amount of token1 expected
        0, # minimum amount of token2 expected
        owner_l2,
        deadline
    ]
    txn = position_mgr.mint(
        params,
        {'from': owner_l2}
    )
    print(txn.return_value)

def get_lower_tick():
    return math.ceil(-887272 / 60) * 60
>>>>>>> usdt_test

def get_upper_tick():
    return math.floor(887272 / 60) * 60

def encode_price(n1, n2):
    return math.trunc(math.sqrt(int(n1)/int(n2)) * 2**96)