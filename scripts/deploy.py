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
    USDs_token_details,
    USDs_file
)
from .utils import (
    confirm,
    getAddressFromNetwork,
    signal_handler,
    editAddressFile
)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    print("\nDeploying essential components of USDs")
    print("On testnet excluding TwoPoolStrategy and Buyback")

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
    # Bancor
    bancor = BancorFormula.deploy(
        {'from': owner }
    )
    txn = bancor.init()

    # VaultCoreTools
    core = VaultCoreTools.deploy(
        {'from': owner }
    )
    proxy = TransparentUpgradeableProxy.deploy(
        core.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin }
    )
    vault_tools_proxy = Contract.from_abi("VaultCoreTools", proxy.address, VaultCoreTools.abi)
    txn = vault_tools_proxy.initialize(bancor.address, {'from': owner })

    # VaultCore
    vault = VaultCore.deploy(
        {'from': owner }
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        vault.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin },
    )
    vault_proxy = Contract.from_abi("VaultCore", proxy.address, VaultCore.abi)
    txn = vault_proxy.initialize(
        spa_l2_address,
        vault_tools_proxy.address,
        fee_vault,
        {'from': owner }
    )

    # Oracle
    oracle = Oracle.deploy(
        {'from': owner },
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        oracle.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin },
    )
    oracle_proxy = Contract.from_abi("Oracle", proxy.address, Oracle.abi)
    txn = oracle_proxy.initialize(
        chainlink_usdc_price_feed,
        spa_l2_address,
        usdc_arbitrum,
        chainlink_flags,
        {'from': owner }
    )

    # USDs
    usds = USDsL2.deploy(
        {'from': owner },
#        publish_source=True,
    )
    proxy = TransparentUpgradeableProxy.deploy(
        usds.address,
        proxy_admin.address,
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin },
    )
    usds_proxy = Contract.from_abi("USDsL2", proxy.address, USDsL2.abi)
    usds_proxy.initialize(
        name,
        symbol,
        vault_proxy.address,
        l2_gateway,
        usds_l1_address,
        {'from': owner },
    )

    # configure VaultCore contract with USDs, Oracle contract address
    txn = vault_proxy.updateUSDsAddress(
        usds_proxy,
        {'from': owner }
    )
    # configure VaultCore contract with Oracle contract address
    txn = vault_proxy.updateOracleAddress(
        oracle_proxy.address,
        {'from': owner }
    )
    txn = oracle_proxy.updateVaultAddress(
        vault_proxy.address,
        {'from': owner }
    )
    txn = oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
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

    print(f"\n{network.show_active()}:\n")
    editAddressFile(USDs_file, bancor.address, "bancor_formula")
    editAddressFile(USDs_file, vault_tools_proxy.address, "vault_core_tools_proxy")
    editAddressFile(USDs_file, vault_proxy.address, "vault_core_proxy")
    editAddressFile(USDs_file, oracle_proxy.address, "oracle_proxy")
    editAddressFile(USDs_file, usds_proxy.address, "USDs_l2_proxy")
    print(f"Bancor Formula address: {bancor.address}")

    print(f"Vault Core Tools:")
    print(f"\taddress: {core.address}")
    print(f"\tproxy address: {vault_tools_proxy.address}")

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
            10**8, # chainlink price feed precision
            {'from': owner }
        )

