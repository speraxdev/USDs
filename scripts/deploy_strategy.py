import sys
import signal
import click
from brownie import (
    ProxyAdmin,
    TransparentUpgradeableProxy,
    ThreePoolStrategy,
    BuybackSingle,
    BuybackTwoHops,
    USDsL2,
    VaultCore,
    accounts,
    interface,
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


def signal_handler(signal, frame):
    sys.exit(0)

def deploy_one_strategy(index, admin, owner, vault_proxy_address):
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
        vault_proxy_address, # vault address
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978', # reward token address
        assets, # assets
        lp_tokens, # LP tokens
        '0x97E2768e8E73511cA874545DC5Ff8067eB19B787', # crv gauge address
        index,
        {'from': owner},
    )
    return strategy_proxy.address

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)
    print("\n**** WARNING: this script would only work on arbitrum mainnet or arbitrum mainnet fork ****")
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
    print(f"contract owner account: {owner.address}\n")

    vault_proxy_address = input("Enter VaultCore proxy address: ").strip()
    if len(vault_proxy_address) == 0:
        print("missing VaultCore proxy address")
        return
    usds_proxy_address = input("Enter USDs L2 proxy address: ").strip()
    if len(usds_proxy_address) == 0:
        print("missing USDs L2 proxy address")
        return
    vault_proxy = Contract.from_abi(
        "VaultCore",
        vault_proxy_address,
        VaultCore.abi
    )
    usds_proxy = Contract.from_abi(
        "USDsL2",
        usds_proxy_address,
        USDsL2.abi
    )

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
