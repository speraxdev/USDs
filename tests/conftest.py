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
def vault(VaultCore, VaultCoreLibrary, accounts):
    owner_vault = accounts[2]
    core = VaultCoreLibrary.deploy(
        {'from': owner_vault}
    )
    vault = VaultCore.deploy(
        {'from': owner_vault}
    )
    vault.initialize(
        {'from': owner_vault}
    )
    return vault

@pytest.fixture(scope="module", autouse=True)
def usds2(USDsL2, vault, owner_l2):
    usds2 = USDsL2.deploy(
        {'from': owner_l2}
    )
    usds2.initialize(
        'USDs Layer 2',
        'USDs2',
        vault, 
        {'from': owner_l2}
    )
    return usds2


@pytest.fixture(autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass
