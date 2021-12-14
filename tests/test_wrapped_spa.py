import pytest
from brownie import  Wei, Contract, reverts
import time

def buyback_single_no_pool(sperax, weth, BuybackSingle, owner_l2):
    (   spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax
