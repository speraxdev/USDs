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

    #if not os.environ.get('WEB3_INFURA_PROJECT_ID'):
    #    print("\nEnvironment variable WEB3_INFURA_PROJECT_ID is not set\n")
    #    return

    print("\n**** WARNING: fee vault will be the same as contract owner ****")

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
    print(f"\nL1 wSPA address: {spa_l1_address}\n")
    print(f"\nL1 USDs address: {usds_l1_address}\n")
    print(f"\nFee Vault address: {fee_vault}\n")
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
    chainlink_eth_price_feed = getAddressFromNetwork(
        testnetAddresses.third_party.chainlink_eth_price_feed,
        mainnetAddresses.third_party.chainlink_eth_price_feed
    )
    weth_arbitrum = getAddressFromNetwork(
        testnetAddresses.third_party.weth_arbitrum,
        mainnetAddresses.third_party.weth_arbitrum
    )
    chainlink_flags = getAddressFromNetwork(
        testnetAddresses.third_party.chainlink_flags,
        mainnetAddresses.third_party.chainlink_flags
    )

    # admin contract
    proxy_admin = ProxyAdmin.deploy(
        {'from': admin, 'gas_limit': 1000000000}
#        publish_source=True,
    )

    # deploy smart contracts
    bancor = BancorFormula.deploy(
        {'from': owner, 'gas_limit': 1000000000}
#        publish_source=True,
    )
    txn = bancor.init()

    core = VaultCoreTools.deploy(
        {'from': owner, 'gas_limit': 1000000000}
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        core.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin, 'gas_limit': 1000000000}
#        publish_source=True,
    )
    core_proxy = Contract.from_abi("VaultCoreTools", proxy.address, VaultCoreTools.abi)
    txn = core_proxy.initialize(bancor.address, {'from': owner})

    vault = VaultCore.deploy(
        {'from': owner, 'gas_limit': 1000000000}
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        vault.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin, 'gas_limit': 1000000000},
#        publish_source=True,
    )
    vault_proxy = Contract.from_abi("VaultCore", proxy.address, VaultCore.abi)

    oracle = Oracle.deploy(
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        oracle.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin, 'gas_limit': 1000000000},
#        publish_source=True,
    )
    oracle_proxy = Contract.from_abi("Oracle", proxy.address, Oracle.abi)

    usds = USDsL2.deploy(
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        usds.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin, 'gas_limit': 1000000000},
#        publish_source=True,
    )
    usds_proxy = Contract.from_abi("USDsL2", proxy.address, USDsL2.abi)

    usds_proxy.initialize(
        name,
        symbol,
        vault_proxy.address,
        l2_gateway,
        usds_l1_address,
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=True,
    )

    spa = SperaxTokenL2.deploy(
        'Sperax',
        'SPA',
        l2_gateway,
        spa_l1_address,
        {'from': owner, 'gas_limit': 1000000000},
#        publish_source=True,
    )

    txn = oracle_proxy.initialize(
        chainlink_eth_price_feed,
        spa.address,
        weth_arbitrum,
        chainlink_flags,
        {'from': owner, 'gas_limit': 1000000000}
    )

    oracle_proxy.updateVaultAddress(
        vault_proxy.address,
        {'from': owner, 'gas_limit': 1000000000}
    )

    txn = vault_proxy.initialize(
        spa.address,
        core_proxy.address,
        fee_vault,
        {'from': owner, 'gas_limit': 1000000000}
    )

    # configure VaultCore contract with USDs contract address
    txn = vault_proxy.updateUSDsAddress(
        usds_proxy,
        {'from': owner, 'gas_limit': 1000000000}
    )
    # configure VaultCore contract with Oracle contract address
    txn = vault_proxy.updateOracleAddress(
        oracle_proxy.address,
        {'from': owner, 'gas_limit': 1000000000}
    )

    txn = spa.setMintable(
        vault_proxy.address,
        True,
        {'from': owner, 'gas_limit': 1000000000}
    )

    # configure stablecoin collaterals in vault and oracle
    configure_collaterals(vault_proxy, oracle_proxy, owner, convert)

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

    print(f"SPA layer 2 address: {spa.address}")

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
            collateral, # address of: USDC, USDT, DAI or WBTC
            zero_address, # _defaultStrategyAddr: CURVE, AAVE, etc
            False, # _allocationAllowed
            0, # _allocatePercentage
            zero_address, # _buyBackAddr
            False, # _rebaseAllowed
            {'from': owner, 'gas_limit': 1000000000}
        )
        # wire up price feed for the added collateral
        oracle_proxy.updateCollateralInfo(
            collateral, # ERC20 address
            True, # supported
            chainlink, # chainlink price feed address
            precision, # chainlink price feed precision
            {'from': owner, 'gas_limit': 1000000000}
        )
