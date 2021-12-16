import pytest
from brownie import (
    reverts,
    convert
)

def test_mint(spa_l1, owner_l1):
    wspa, spa = spa_l1
    amount = int(1000)
    # approve the mint transaction first
    txn = spa.approve(
        wspa,
        amount,
        {'from': owner_l1}
    )
    assert txn.events['Approval']['owner'] == owner_l1
    assert txn.events['Approval']['spender'] == wspa
    assert txn.events['Approval']['value'] == amount

    txn = wspa.mint(
        amount,
        {'from': owner_l1}
    )
    assert txn.events['Transfer']['from'] == owner_l1 
    zero_address = convert.to_address('0x0000000000000000000000000000000000000000')
    assert txn.events['Transfer']['to'] == zero_address
    assert txn.events['Transfer']['value'] == amount

    txn = wspa.balanceOf(owner_l1)
    assert txn == amount

def test_transfer(spa_l1, owner_l1, accounts):
    wspa, spa = spa_l1
    recipient = accounts[6]
    amount = 1000
    # approve the mint transaction first
    txn = spa.approve(
        wspa,
        amount,
        {'from': owner_l1}
    )
    txn = wspa.mint(
        amount,
        {'from': owner_l1}
    )
    txn = wspa.transfer(
        recipient,
        amount - 1,
        {'from': owner_l1}
    )
    assert txn.events['Transfer']['from'] == owner_l1
    assert txn.events['Transfer']['to'] == recipient
    assert txn.events['Transfer']['value'] == amount - 1

    txn = wspa.balanceOf(recipient)
    assert txn == amount - 1
    txn = wspa.balanceOf(owner_l1)
    assert txn == 1

    txn = wspa.transfer(
        recipient,
        0,
        {'from': owner_l1}
    )
    assert txn.events['Transfer']['from'] == owner_l1
    assert txn.events['Transfer']['to'] == recipient
    assert txn.events['Transfer']['value'] == 0
    
    # call should fail because sender has insufficient wrapped spa left
    with reverts():
        txn = wspa.transfer(
            recipient,
            amount,
            {'from': owner_l1}
        )

def test_burn(spa_l1, owner_l1):
    wspa, spa = spa_l1
    amount = 1000
    # approve the mint transaction first
    txn = spa.approve(
        wspa,
        amount,
        {'from': owner_l1}
    )
    txn = wspa.mint(
        amount,
        {'from': owner_l1}
    )
    zero_address = convert.to_address('0x0000000000000000000000000000000000000000')
    for value in range(2):
        txn = wspa.burn(
            value,
            {'from': owner_l1}
        )
        assert txn.events['Transfer']['from'] == zero_address
        assert txn.events['Transfer']['to'] == owner_l1
        assert txn.events['Transfer']['value'] == value

    # call should fail because of insufficent funds
    with reverts():
        txn = wspa.burn(
            amount,
            {'from': owner_l1}
        )

def test_bridge_mint(spa_l1, owner_l1, gatewayL1, accounts):
    wspa, spa = spa_l1
    amount = 928383
    txn = wspa.bridgeMint(
        accounts[6],
        amount,
        {'from': gatewayL1}
    )

    # call should fail because of invalid caller
    with reverts():
        txn = wspa.bridgeMint(
            accounts[6],
            amount,
            {'from': owner_l1}
        )

def test_arbitrum_enabled(spa_l1):
    wspa, spa = spa_l1
    txn = wspa.isArbitrumEnabled()
    assert txn == '0xa4b1'

def test_change_arbitrum_token(spa_l1, owner_l1, accounts):
    wspa, spa = spa_l1
    new_bridge = accounts[6]
    new_router = accounts[7]
    txn = wspa.changeArbToken(
        new_bridge,
        new_router,
        {'from': owner_l1}
    )
    assert txn.events['ArbitrumGatewayRouterChanged']['newBridge'] == new_bridge
    assert txn.events['ArbitrumGatewayRouterChanged']['newRouter'] == new_router

    zero_address = convert.to_address('0x0000000000000000000000000000000000000000')
    not_owner = accounts[8]
    with reverts():
        txn = wspa.changeArbToken(
            zero_address,
            zero_address,
            {'from': not_owner}
        )

def test_change_spa(spa_l1, owner_l1, accounts):
    wspa, spa = spa_l1
    new_spa = accounts[6]
    txn = wspa.changeSpaAddress(
        new_spa,
        {'from': owner_l1}
    )
    assert txn.events['SPAaddressUpdated']['oldSPA'] == spa.address
    assert txn.events['SPAaddressUpdated']['newSPA'] == new_spa

    not_owner = accounts[8]
    with reverts():
        txn = wspa.changeSpaAddress(
            new_spa,
            {'from': not_owner}
        )

def test_register_token(spa_l1, owner_l1, accounts):
    wspa, spa = spa_l1
    l2_token_address = accounts[6]

    submission_cost_for_bridge = 1000000000000
    submission_cost_for_router = 1000000000000
    max_gas = 1000000
    gas_price_bid = 9827373
    value = submission_cost_for_bridge + submission_cost_for_router + 2 * (max_gas * gas_price_bid) + 100

    gateway_value = 1
    router_value = 2
    credit_back_address = accounts[7]

    txn = wspa.registerTokenOnL2(
        l2_token_address,
        submission_cost_for_bridge,
        submission_cost_for_router,
        max_gas,
        gas_price_bid,
        gateway_value,
        router_value,
        credit_back_address,
        {'from': owner_l1, 'amount': value}
    )

    not_owner = accounts[8]
    with reverts():
        txn = wspa.registerTokenOnL2(
            l2_token_address,
            submission_cost_for_bridge,
            submission_cost_for_router,
            max_gas,
            gas_price_bid,
            gateway_value,
            router_value,
            credit_back_address,
            {'from': not_owner, 'amount': value}
        )