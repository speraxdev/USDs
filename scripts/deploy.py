import sys
import signal
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

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    #if not os.environ.get('WEB3_INFURA_PROJECT_ID'):
    #    print("\nEnvironment variable WEB3_INFURA_PROJECT_ID is not set\n")
    #    return

    print("\n**** WARNING: fee vault will be the same as contract owner ****")

    print("\nEnter admin account password:")
    try:
        admin = accounts.load(filename="admin.keystore")
    except ValueError:
        print("\nInvalid admin wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/admin.json")
        return

    print("\nEnter contract owner account password:")
    try:
        owner = accounts.load(filename="minter.keystore")
    except ValueError:
        print("\nInvalid owner wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/minter.json")
        return

    fee_vault = owner

    initial_balance = owner.balance()

    name = input("\nEnter name (Sperax USD): ") or "Sperax USD"
    symbol = input("Enter symbol (USDs): ") or "USDs"
    print('\n')

    # arbitrum-one (mainnet):
    l2_gateway = '0x096760F208390250649E3e8763348E783AEF5562'
    # chainlink price feed for ETH on Arbitrum
    chainlink_eth_price_feed = '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612'
    weth_arbitrum = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
    l1_address = '' # USDs address on layer 1 [rinkeby]

    if network.show_active() == 'arbitrum-rinkeby':
        # Arbitrum rinkeby:
        l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'
        chainlink_eth_price_feed = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
        weth_arbitrum = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'
        l1_address = '0x377ff873b648b678608b216467ee94713116c4cd' # USDs address on layer 1 [rinkeby]

    # admin contract
    proxy_admin = ProxyAdmin.deploy(
        {'from': admin},
#        publish_source=True,
    )

    # deploy smart contracts
    bancor = BancorFormula.deploy(
        {'from': owner},
#        publish_source=True,
    )
    txn = bancor.init()

    core = VaultCoreTools.deploy(
        {'from': owner},
#        publish_source=True,
    )
    txn = core.initialize(bancor.address)

    vault = VaultCore.deploy(
        {'from': owner},
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
        {'from': owner},
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
        {'from': owner},
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
        l1_address,
        {'from': owner},
#        publish_source=True,
    )

    spa = SperaxTokenL2.deploy(
        'Sperax',
        'SPA',
        l2_gateway,
        usds_proxy.address,
        {'from': owner},
#        publish_source=True,
    )

    txn = oracle_proxy.initialize(
        chainlink_eth_price_feed,
        spa.address,
        weth_arbitrum,
        {'from': owner}
    )

    oracle_proxy.updateVaultAddress(
        vault_proxy.address,
        {'from': owner}
    )

    txn = vault_proxy.initialize(
        spa.address,
        core.address,
        fee_vault,
        {'from': owner}
    )

    # configure VaultCore contract with USDs contract address
    txn = vault_proxy.updateUSDsAddress(
        usds_proxy,
        {'from': owner}
    )
    # configure VaultCore contract with Oracle contract address
    txn = vault_proxy.updateOracleAddress(
        oracle_proxy.address,
        {'from': owner}
    )

    txn = spa.setMintable(
        vault_proxy.address,
        True,
        {'from': owner}
    )

    # configure stablecoin collaterals in vault and oracle
    configure_collaterals(vault_proxy, oracle_proxy, owner, convert)

    print(f"\n{network.show_active()}:\n")
    print(f"Bancor Formula address: {bancor.address}")
    print(f"Vault Core Tools address: {core.address}")

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
            {'from': owner}
        )
        # wire up price feed for the added collateral
        oracle_proxy.updateCollateralInfo(
            collateral, # ERC20 address
            True, # supported
            chainlink, # chainlink price feed address
            precision, # chainlink price feed precision
            {'from': owner}
        )
