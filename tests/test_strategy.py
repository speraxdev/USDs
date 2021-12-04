import pytest
import json
import time
import brownie

def test_deposit(sperax, wbtc):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback
    ) = sperax

    amount = int(9999)
    txn = strategy_proxy.deposit(
        wbtc.address,
        amount,
        {'from': vault_proxy.address}
    )
    txn.events['Deposit']['_asset'] == wbtc
    txn.events['Deposit']['_amount'] == amount