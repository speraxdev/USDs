#!/usr/bin/python3
import os
import pytest
import eth_utils
from brownie import network

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
def user_account(accounts):
    private_key = os.environ.get('WALLET_PRIVATE_KEY')
    # default to ganache local development
    if len(private_key) == 0:
        return accounts[4]
    return accounts.add(private_key)

@pytest.fixture(scope="module", autouse=True)
def weth(interface, chain):
    # Arbitrum-rinkeby testnet:
    weth_address = '0xB47e6A5f8b33b3F17603C83a0535A9dcD7E32681'

    if chain.id == 42161:
        # Arbitrum-one mainnet:
        weth_address = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'

    return interface.IERC20(weth_address)

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
    owner_l2,
    interface,
    chain,
):
    # Arbitrum rinkeby:
    price_feed_eth = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'
    swap_router = interface.ISwapRouter('0x9413AD42910c1eA60c737dB5f58d1C504498a3cD')

    if chain.id == 42161:
        # Arbitrum-one mainnet:
        price_feed_eth = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
        l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'
        swap_router = interface.ISwapRouter('0x9413AD42910c1eA60c737dB5f58d1C504498a3cD')

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

    pool_fee = 1

    buyback = BuybackSingle.deploy(
        swap_router, # swap router address
        usds_proxy.address,
        weth.address, # input token
        vault_proxy.address,
        pool_fee,
        {'from': owner_l2},
    )

    oracle_proxy.initialize(
        price_feed_eth,
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
        pool_fee,
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

    
    return (proxy_admin, spa, usds_proxy, vault_core_tools, vault_proxy, oracle_proxy, buyback)
