import signal
import click
from brownie import (
    TransparentUpgradeableProxy,
    ProxyAdmin,
    BancorFormula,
    VaultCoreTools,
    Oracle,
    SperaxTokenL2,
    USDsL2,
    VaultCore,
    ThreePoolStrategy,
    BuybackTwoHops,
    BuybackThreeHops,
    accounts,
    network,
    Contract,
    convert
)
import eth_utils
from .constants import (
    mainnetAddresses,
    testnetAddresses,
    USDs_token_details
)
from .utils import (
    confirm,
    getAddressFromNetwork,
    signal_handler
)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    print("\n**** WARNING: this script would only work on arbitrum mainnet or arbitrum mainnet fork ****")

    #if not os.environ.get('WEB3_INFURA_PROJECT_ID'):
    #    print("\nEnvironment variable WEB3_INFURA_PROJECT_ID is not set\n")
    #    return

    # print("\n**** WARNING: fee vault will be the same as contract owner ****")

    # proxy admin account
    admin = accounts.load(
        click.prompt(
            "admin account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"admin account: {admin.address}\n")

    # contract owner account
    owner = accounts.load(
        click.prompt(
            "owner account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"contract owner account: {owner.address}\n")

    print(f"\nDeploying on {network.show_active()}:\n")
    spa_l1_address = getAddressFromNetwork(
        testnetAddresses.deploy.L1_wSPA,
        mainnetAddresses.deploy.L1_wSPA
    )
    usds_l1_address = getAddressFromNetwork(
        testnetAddresses.deploy.L1_USDs,
        mainnetAddresses.deploy.L1_USDs
    )
    fee_vault = getAddressFromNetwork(
        testnetAddresses.deploy.fee_vault,
        mainnetAddresses.deploy.fee_vault
    )

    spa_l2_address = getAddressFromNetwork(
        testnetAddresses.deploy.L2_SPA,
        mainnetAddresses.deploy.L2_SPA
    )

    print(f"\nL1 wSPA address: {spa_l1_address}\n")
    print(f"\nL1 USDs address: {usds_l1_address}\n")
    print(f"\nFee Vault address: {fee_vault}\n")
    print(f"\nL2 SPA address: {spa_l2_address}\n")
    confirm("Are the above addresses correct?")

    initial_balance = owner.balance()

    name = USDs_token_details.name
    symbol = USDs_token_details.symbol
    print(f"\nToken Name: {name}\n")
    print(f"\nToken Symbol: {symbol}\n")
    confirm("Are the above details correct?")
    print('\n')

    # third party addresses
    l2_gateway = getAddressFromNetwork(
        testnetAddresses.third_party.l2_gateway,
        mainnetAddresses.third_party.l2_gateway
    )
    chainlink_usdc_price_feed = getAddressFromNetwork(
        testnetAddresses.third_party.chainlink_usdc_price_feed,
        mainnetAddresses.third_party.chainlink_usdc_price_feed
    )
    usdc_arbitrum = getAddressFromNetwork(
        testnetAddresses.third_party.usdc_arbitrum,
        mainnetAddresses.third_party.usdc_arbitrum
    )
    chainlink_flags = getAddressFromNetwork(
        testnetAddresses.third_party.chainlink_flags,
        mainnetAddresses.third_party.chainlink_flags
    )

    # admin contract
    proxy_admin = ProxyAdmin.deploy(
        {'from': admin}
    )

    # deploy smart contracts
    bancor = BancorFormula.deploy(
        {'from': owner }
#        publish_source=True,
    )
    txn = bancor.init()

    core = VaultCoreTools.deploy(
        {'from': owner }
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        core.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin }
#        publish_source=True,
    )
    core_proxy = Contract.from_abi("VaultCoreTools", proxy.address, VaultCoreTools.abi)
    txn = core_proxy.initialize(bancor.address, {'from': owner})

    vault = VaultCore.deploy(
        {'from': owner }
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        vault.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin },
#        publish_source=True,
    )
    vault_proxy = Contract.from_abi("VaultCore", proxy.address, VaultCore.abi)

    oracle = Oracle.deploy(
        {'from': owner },
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        oracle.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin },
#        publish_source=True,
    )
    oracle_proxy = Contract.from_abi("Oracle", proxy.address, Oracle.abi)

    usds = USDsL2.deploy(
        {'from': owner },
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        usds.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin },
#        publish_source=True,
    )
    usds_proxy = Contract.from_abi("USDsL2", proxy.address, USDsL2.abi)

    usds_proxy.initialize(
        name,
        symbol,
        vault_proxy.address,
        l2_gateway,
        usds_l1_address,
        {'from': owner },
#        publish_source=True,
    )


    txn = oracle_proxy.initialize(
        chainlink_usdc_price_feed,
        spa_l2_address,
        usdc_arbitrum,
        chainlink_flags,
        {'from': owner }
    )

    oracle_proxy.updateVaultAddress(
        vault_proxy.address,
        {'from': owner }
    )

    txn = vault_proxy.initialize(
        spa_l2_address,
        core_proxy.address,
        fee_vault,
        {'from': owner }
    )

    # configure VaultCore contract with USDs contract address
    txn = vault_proxy.updateUSDsAddress(
        usds_proxy,
        {'from': owner }
    )
    # configure VaultCore contract with Oracle contract address
    txn = vault_proxy.updateOracleAddress(
        oracle_proxy.address,
        {'from': owner }
    )

    spa = Contract.from_abi("SperaxTokenL2", spa_l2_address, SperaxTokenL2.abi)

    if network.show_active() != 'arbitrum-main-fork':
        txn = spa.setMintable(
            vault_proxy.address,
            True,
            {'from': owner }
        )

    # configure stablecoin collaterals in vault and oracle
    configure_collaterals(vault_proxy, oracle_proxy, owner, convert)
    deploy_strategy(usds_proxy, vault_proxy, admin, owner)

    print(f"\n{network.show_active()}:\n")
    print(f"Bancor Formula address: {bancor.address}")

    print(f"Vault Core Tools:")
    print(f"\taddress: {core.address}")
    print(f"\tproxy address: {core_proxy.address}")

    print(f"Vault Core:")
    print(f"\taddress: {vault.address}")
    print(f"\tproxy address: {vault_proxy.address}")

    print(f"Oracle:")
    print(f"\taddress: {oracle.address}")
    print(f"\tproxy address: {oracle_proxy.address}")

    print(f"USDsL2:")
    print(f"\taddress: {usds.address}")
    print(f"\tproxy address: {usds_proxy.address}")

    final_balance = owner.balance()
    print(f'\naccount balance: {final_balance}')
    gas_cost = initial_balance - final_balance
    gas_cost = "{:,}".format(gas_cost) # format with comma delimiters
    print(f'gas cost:        {gas_cost} gwei\n')


def configure_collaterals(
    vault_proxy,
    oracle_proxy,
    owner,
    convert
):
    # configure stablecoin collaterals in vault and oracle
    collaterals = getAddressFromNetwork(
        testnetAddresses.collaterals,
        mainnetAddresses.collaterals
    )
    precision = 10**8
    zero_address = convert.to_address('0x0000000000000000000000000000000000000000')
    for collateral, chainlink in collaterals.items():
        # authorize a new collateral
        vault_proxy.addCollateral(
            collateral, # address of: , USDT, DAI or WBTC
            zero_address, # _defaultStrategyAddr: CURVE, AAVE, etc
            False, # _allocationAllowed
            0, # _allocatePercentage
            zero_address, # _buyBackAddr
            False, # _rebaseAllowed
            {'from': owner }
        )
        # wire up price feed for the added collateral
        oracle_proxy.updateCollateralInfo(
            collateral, # ERC20 address
            True, # supported
            chainlink, # chainlink price feed address
            precision, # chainlink price feed precision
            {'from': owner }
        )

def deploy_strategy(
    usds_proxy,
    vault_proxy,
    admin,
    owner
):
    usdt_address = '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'
    wbtc_address = '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f'
    weth_address = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
    usdc_address = '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8'
    crv_address = '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978'
    # deploy strategy contracts for usdt, wbtc and weth
    strategy_proxy_addr_usdt = deploy_one_strategy(0, admin, owner, vault_proxy)
    strategy_proxy_addr_wbtc = deploy_one_strategy(1, admin, owner, vault_proxy)
    strategy_proxy_addr_weth = deploy_one_strategy(2, admin, owner, vault_proxy)
    # deploy buyback contract supporting swapping usdt, wbtc and weth back to usds
    buybackTwoHops = BuybackTwoHops.deploy(
        usds_proxy.address,
        vault_proxy.address,
        {'from': owner},
    )
    buybackTwoHops.updateInputTokenInfo(
        usdt_address, True, usdc_address, 500, 500,
        {'from': owner},
    )
    buybackTwoHops.updateInputTokenInfo(
        wbtc_address, True, usdc_address, 3000, 500,
        {'from': owner},
    )
    buybackTwoHops.updateInputTokenInfo(
        weth_address, True, usdc_address, 10000, 500,
        {'from': owner},
    )
    # deploy buyback contract supporting swapping crv back to usds
    buybackThreeHops = BuybackThreeHops.deploy(
        usds_proxy.address,
        vault_proxy.address,
        {'from': owner},
    )
    buybackThreeHops.updateInputTokenInfo(
        crv_address,
        True,
        weth_address,
        usdc_address,
        3000,
        500,
        500,
        {'from': owner},
    )
    vault_proxy = Contract.from_abi(
        "VaultCore",
        vault_proxy.address,
        VaultCore.abi
    )
    # on VaultCore, add strategy contracts
    vault_proxy.addStrategy(
        strategy_proxy_addr_usdt,
        {'from': owner},
    )
    vault_proxy.addStrategy(
        strategy_proxy_addr_wbtc,
        {'from': owner},
    )
    vault_proxy.addStrategy(
        strategy_proxy_addr_weth,
        {'from': owner},
    )
    # on VaultCore, configure buyBackAddr of each strategy
    vault_proxy.updateStrategyRwdBuybackAddr(
        strategy_proxy_addr_usdt,
        buybackThreeHops.address,
        {'from': owner},
    )
    vault_proxy.updateStrategyRwdBuybackAddr(
        strategy_proxy_addr_usdt,
        buybackThreeHops.address,
        {'from': owner},
    )
    vault_proxy.updateStrategyRwdBuybackAddr(
        strategy_proxy_addr_usdt,
        buybackThreeHops.address,
        {'from': owner},
    )
    # on VaultCore, configure collateral's strategy address and buyback addresses
    # assuming usdt, wbtc and weth has been added to VaultCore
    vault_proxy.updateCollateralInfo(
        usdt_address,
        strategy_proxy_addr_usdt,
        True,
        80,
        buybackTwoHops.address,
        True,
        {'from': owner},
    )
    vault_proxy.updateCollateralInfo(
        wbtc_address,
        strategy_proxy_addr_wbtc,
        True,
        80,
        buybackTwoHops.address,
        True,
        {'from': owner},
    )
    vault_proxy.updateCollateralInfo(
        weth_address,
        strategy_proxy_addr_weth,
        True,
        80,
        buybackTwoHops.address,
        True,
        {'from': owner},
    )

    print(f"\nThreePoolStrategy for USDT deployed at address: {strategy_proxy_addr_usdt}")
    print(f"ThreePoolStrategy for WBTC deployed at address: {strategy_proxy_addr_wbtc}")
    print(f"ThreePoolStrategy for WETH deployed at address: {strategy_proxy_addr_weth}")
    print(f"\nBuybackTwoHops (usdt, wbtc, weth) deployed at address: {buybackTwoHops.address}")
    print(f"BuybackThreeHops (crv) deployed at address: {buybackThreeHops.address}")


def deploy_one_strategy(index, admin, owner, vault_proxy):
    if network.show_active() == 'mainnet' or 'arbitrum-main-fork':
        strategy = ThreePoolStrategy.deploy(
            {'from': owner},
        )
        proxy_admin = ProxyAdmin.deploy(
            {'from': admin},
        )
        proxy = TransparentUpgradeableProxy.deploy(
            strategy.address,
            proxy_admin.address,
            eth_utils.to_bytes(hexstr="0x"),
            {'from': admin},
    #        publish_source=True,
        )
        strategy_proxy = Contract.from_abi(
            "ThreePoolStrategy",
            proxy.address,
            ThreePoolStrategy.abi
        )

        assets = [
            '0x82af49447d8a07e3bd95bd0d56f35241523fbab1',
            '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
            '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
        ]
        lp_tokens = [
            '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
            '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
            '0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2',
        ]
        strategy_proxy.initialize(
            '0x960ea3e3C7FB317332d990873d354E18d7645590', # platform address
            vault_proxy.address, # vault address
            '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978', # reward token address
            assets, # assets
            lp_tokens, # LP tokens
            '0x97E2768e8E73511cA874545DC5Ff8067eB19B787', # crv gauge address
            index,
            {'from': owner},
        )
        return strategy_proxy.address
