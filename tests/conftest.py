#!/usr/bin/python3

import pytest

@pytest.fixture(scope="module", autouse=True)
def vault(VaultCore, accounts):
    owner = accounts[1]
    vault = VaultCore.deploy(
        {'from': owner}
    )
    vault.initialize(
        {'from': owner}
    )
    return vault

@pytest.fixture(scope="module", autouse=True)
def usds(USDs, vault, accounts):
    owner = accounts[0]
    usds = USDs.deploy(
        {'from': owner}
    )
    usds.initialize(
        'stablecoin',
        'COIN',
        vault, 
        {'from': owner}
    )
    return usds


@pytest.fixture(autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass
