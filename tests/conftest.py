#!/usr/bin/python3
import pytest

@pytest.fixture(scope="module", autouse=True)
def owner_l1(accounts):
    return accounts[0]

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
    return accounts[1]

@pytest.fixture(scope="module", autouse=True)
def sperax(BancorFormula, USDsL2, SperaxTokenL2, Oracle, VaultCore, VaultCoreLibrary, usds1, owner_l2):
    # Arbitrum rinkeby:
    price_feed_eth_arbitrum_testnet = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    weth_arbitrum_testnet = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'
    l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'

    bancor = BancorFormula.deploy(
        {'from': owner_l2}
    )
    bancor.init()
    oracle = Oracle.deploy(
        {'from': owner_l2}
    )
    VaultCoreLibrary.deploy(
        {'from': owner_l2}
    )
    vault = VaultCore.deploy(
        {'from': owner_l2}
    )
    usds2 = USDsL2.deploy(
        'USDs Layer 2',
        'USDs2',
        vault.address, 
        l2_gateway,
        usds1.address,
        {'from': owner_l2}
    )
    spa = SperaxTokenL2.deploy(
        'Sperax',
        'SPA',
        l2_gateway,
        usds2.address,
        {'from': owner_l2},
    )

    oracle.initialize(
        price_feed_eth_arbitrum_testnet,
        spa.address,
        weth_arbitrum_testnet,
        {'from': owner_l2}
    )
    vault.initialize(
        spa.address,
        bancor.address,
        {'from': owner_l2}
    )
    vault.updateUSDsAddress(
        usds2.address,
        {'from': owner_l2}
    )
    vault.updateOracleAddress(
        oracle.address,
        {'from': owner_l2}
    )
    return (spa, usds2, vault)


@pytest.fixture(autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass
