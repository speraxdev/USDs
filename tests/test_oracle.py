import pytest
import json
import time
import brownie


def user(accounts):
    return accounts[9]

def test_update_USDs_Address(sperax,owner_l2):
    (   
         oracle_proxy,
         usds_proxy
    ) = sperax
    oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
        )