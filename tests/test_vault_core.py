#!/usr/bin/python3
import pytest
import brownie

def test_mind_usds(sperax, usdt, owner_l2, accounts):
    (
        spa,
        usds_proxy,
        core_proxy,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop
    ) = sperax

    deadline = 1637632800 + brownie.chain.time() 
      
    amount  = 10000
    slippage_collateral = 0
    slippage_collateral = amount - amount * slippage_collateral * 100
    slippage_spa = 0
    slippage_spa = amount - amount * slippage_spa * 100

    bal = usdt.balanceOf(owner_l2.address)
    print(owner_l2)
    print("----------------------------------", bal)
    # mint USDs by specifying amount of USDs to mint
    vault_proxy.mintWithUSDs(
        usdt.address,
        int(amount),
        slippage_collateral,
        slippage_spa,
        deadline,
        {'from': accounts[10]}
    )
