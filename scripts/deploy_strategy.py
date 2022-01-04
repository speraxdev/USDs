import signal
import click
from brownie import (
    TransparentUpgradeableProxy,
    ProxyAdmin,
    VaultCore,
    TwoPoolStrategy,
    BuybackSingle,
    BuybackTwoHops,
    BuybackThreeHops,
    accounts,
    Contract,
    network
)
import eth_utils
from .constants import (
    strategy_vars_base,
    strategy_addresses,
    USDs,
    Strategies_file
)
from .utils import (
    confirm,
    signal_handler,
)
import json


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
    )
    print(f"contract owner account: {owner.address}\n")

    vault_proxy_address = USDs['mainnet']['vault_core_proxy']
    usds_proxy_address = USDs['mainnet']['USDs_l2_proxy']
    oracle_proxy_address = USDs['mainnet']['oracle_proxy']
    print(f"\nVault Proxy address: {vault_proxy_address}\n")
    print(f"\nUSDs Proxy address: {usds_proxy_address}\n")
    print(f"\nOracle Proxy address: {oracle_proxy_address}\n")

    usdt_address = strategy_addresses.usdt
    weth_address = strategy_addresses.weth
    usdc_address = strategy_addresses.usdc
    crv_address = strategy_addresses.crv
    print(f"\nUSDT address: {usdt_address}\n")
    print(f"\nWETH address: {weth_address}\n")
    print(f"\nUSDC address: {usdc_address}\n")
    print(f"\nCRV Proxy address: {crv_address}\n")
    confirm("Are the above addresses correct?")

    print(f"\nPlatform address: {strategy_vars_base.platform_address}\n")
    print(f"\nReward Token address: {strategy_vars_base.reward_token_address}\n")
    print(f"\nAssets: {strategy_vars_base.assets}\n")
    print(f"\nLP Tokens: {strategy_vars_base.lp_tokens}\n")
    print(f"\nCRV Gauge Index address: {strategy_vars_base.crv_gauge_address}\n")
    confirm("Are the above details correct?")

    # deploy strategy contracts for usdc and usdt
    strategy_proxy_addr_usdc = deploy_strategy(0, admin, owner, vault_proxy_address, oracle_proxy_address)
    strategy_proxy_addr_usdt = deploy_strategy(1, admin, owner, vault_proxy_address, oracle_proxy_address)
    # deploy buyback contract supporting swapping usdc
    buybackSingle = BuybackSingle.deploy(
        usds_proxy_address,
        vault_proxy_address,
        {'from': owner, 'gas_limit': 1000000000},
    )
    buybackSingle.updateInputTokenInfo(
        usdc_address, True, 500,
        {'from': owner, 'gas_limit': 1000000000},
    )
    # deploy buyback contract supporting swapping usdt
    buybackTwoHops = BuybackTwoHops.deploy(
        usds_proxy_address,
        vault_proxy_address,
        {'from': owner, 'gas_limit': 1000000000},
    )
    buybackTwoHops.updateInputTokenInfo(
        usdt_address, True, usdc_address, 500, 500,
        {'from': owner, 'gas_limit': 1000000000},
    )
    # deploy buyback contract supporting swapping crv back to usds
    buybackThreeHops = BuybackThreeHops.deploy(
        usds_proxy_address,
        vault_proxy_address,
        {'from': owner, 'gas_limit': 1000000000},
    )
    buybackThreeHops.updateInputTokenInfo(
        crv_address,
        True,
        weth_address,
        usdc_address,
        3000,
        500,
        500,
        {'from': owner, 'gas_limit': 1000000000},
    )
    vault_proxy = Contract.from_abi(
        "VaultCore",
        vault_proxy_address,
        VaultCore.abi
    )

    # simulate transacting with vault core from deployer address on fork
    if network.show_active() == 'arbitrum-main-fork':
        owner = accounts.at('0xc28c6970D8A345988e8335b1C229dEA3c802e0a6', force=True)

    # on VaultCore, add strategy contracts
    vault_proxy.addStrategy(
        strategy_proxy_addr_usdc,
        {'from': owner, 'gas_limit': 1000000000},
    )
    vault_proxy.addStrategy(
        strategy_proxy_addr_usdt,
        {'from': owner, 'gas_limit': 1000000000},
    )
    # on VaultCore, configure buyBackAddr of each strategy
    vault_proxy.updateStrategyRwdBuybackAddr(
        strategy_proxy_addr_usdc,
        buybackThreeHops.address,
        {'from': owner, 'gas_limit': 1000000000},
    )
    vault_proxy.updateStrategyRwdBuybackAddr(
        strategy_proxy_addr_usdt,
        buybackThreeHops.address,
        {'from': owner, 'gas_limit': 1000000000},
    )
    # on VaultCore, configure collateral's strategy address and buyback addresses
    # assuming usdt, wbtc and weth has been added to VaultCore
    vault_proxy.updateCollateralInfo(
        usdc_address,
        strategy_proxy_addr_usdc,
        True,                           # allocation permission
        1,                              # allocation percentage in %
        buybackSingle.address,
        False,                          # rebase permission
        {'from': owner, 'gas_limit': 1000000000},
    )
    vault_proxy.updateCollateralInfo(
        usdt_address,
        strategy_proxy_addr_usdt,
        True,                           # allocation permission
        1,                              # allocation percentage in %
        buybackTwoHops.address,
        False,                          # rebase permission
        {'from': owner, 'gas_limit': 1000000000},
    )

    # write to JSON
    with open(Strategies_file, "r") as file:
        data = json.load(file)
    data["two_pool_strategy_usdc"] = strategy_proxy_addr_usdc
    data["two_pool_strategy_usdt"] = strategy_proxy_addr_usdt
    data["buyback_single_usdc"] = buybackSingle.address
    data["buyback_two_hops_usdt"] = buybackTwoHops.address
    data["buyback_three_hops_crv"] = buybackThreeHops.address
    with open(Strategies_file, "w") as file:
        json.dump(data, file)


    print(f"\nTwoPoolStrategy for USDC deployed at address: {strategy_proxy_addr_usdc}")
    print(f"TwoPoolStrategy for USDT deployed at address: {strategy_proxy_addr_usdt}")
    print(f"\nBuybackSingle (usdc) deployed at address: {buybackSingle.address}")
    print(f"BuybackTwoHops (usdt) deployed at address: {buybackTwoHops.address}")
    print(f"BuybackThreeHops (crv) deployed at address: {buybackThreeHops.address}")

def deploy_strategy(index, admin, owner, vault_proxy, oracle_proxy):
    strategy = TwoPoolStrategy.deploy(
        {'from': owner, 'gas_limit': 1000000000},
    )
    proxy = TransparentUpgradeableProxy.deploy(
        strategy.address,
        '0x3E49925A79CbFb68BAa5bc9DFb4f7D955D1ddF25',
        eth_utils.to_bytes(hexstr="0x"),
        {'from': admin, 'gas_limit': 1000000000},
    #        publish_source=True,
    )
    strategy_proxy = Contract.from_abi(
        "TwoPoolStrategy",
        proxy.address,
        TwoPoolStrategy.abi
    )

    strategy_vars_base.vault_proxy_address = vault_proxy
    strategy_vars_base.index = index
    strategy_vars_base.oracle_proxy_address = oracle_proxy
    strategy_proxy.initialize(
        strategy_vars_base.platform_address,
        strategy_vars_base.vault_proxy_address,
        strategy_vars_base.reward_token_address,
        strategy_vars_base.assets,
        strategy_vars_base.lp_tokens,
        strategy_vars_base.crv_gauge_address,
        strategy_vars_base.index,
        strategy_vars_base.oracle_proxy_address,
        {'from': owner, 'gas_limit': 1000000000},
    )
    return strategy_proxy.address
