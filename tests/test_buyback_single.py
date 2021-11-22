import pytest
import json
import os
from brownie import  Wei, accounts, BuybackSingle, Contract, reverts
import time

WALLET_PRIVATE_KEY = os.environ.get('WALLET_PRIVATE_KEY')
EMPTY_WALLET_PRIVATE_KEY = os.environ.get('EMPTY_WALLET_PRIVATE_KEY')
SPA = "0xbb5E27Ae27A6a7D092b181FbDdAc1A1004e9adff"
WETH = "0xd0A1E359811322d97991E03f863a0C30C2cF029C"
DAI = "0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa"
SWAP_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
SOL = "0x38cc7d6c8148737b733c4db23d6ecdb8951d9ff1"


abi = [{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_symbol","type":"string"},{"internalType":"uint8","name":"_decimals","type":"uint8"},{"internalType":"uint256","name":"_initialSupply","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"}],"name":"AllowTransfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"}],"name":"BlockTransfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"MintPaused","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"MintUnpaused","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Mintable","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Unmintable","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"recipients","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"name":"batchTransfer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burnFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mintForUSDs","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"mintPause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"mintPaused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"mintUnpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"mintableAccounts","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"mintableGroup","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"releaseAmount","type":"uint256"}],"name":"release","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"revokeAllMintable","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"bool","name":"allow","type":"bool"}],"name":"setMintable","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"timelockOf","outputs":[{"internalType":"uint256","name":"releaseTime","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"releaseTime","type":"uint256"}],"name":"transferWithLock","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"}]

@pytest.fixture(scope="module")
def user_account():
    return accounts.add(WALLET_PRIVATE_KEY)

@pytest.fixture(scope="module")
def user_account_with_no_balance():
    return accounts.add(EMPTY_WALLET_PRIVATE_KEY)

@pytest.fixture(scope="module")
def weth_token():
    return Contract.from_abi("ERC20", WETH, abi)

@pytest.fixture(scope="module")
def spa_token():
    return Contract.from_abi("ERC20", SPA, abi)


@pytest.fixture(scope="module")
def dai_token():
    return Contract.from_abi("ERC20", DAI, abi)


@pytest.fixture(scope="module")
def buyback_single_spa_weth(user_account): 
    return BuybackSingle.deploy(
        SWAP_ROUTER,
        WETH, 
        SPA, 
        user_account.address, 
        3000, {"from": user_account}
    )

@pytest.fixture(scope="module")
def buyback_single_sol_spa(user_account):
    return BuybackSingle.deploy(
        SWAP_ROUTER,
        SOL, 
        SPA, 
        user_account.address, 
        3000, {"from": user_account}
    )


@pytest.fixture(scope="module")
def buyback_single_spa_weth_pf05(user_account):
    return BuybackSingle.deploy(
        SWAP_ROUTER,
        WETH, 
        SPA, 
        user_account.address, 
        50000, {"from": user_account}
    )
     
def test_swap_successful(buyback_single_spa_weth, user_account, weth_token, spa_token):
    balance1 = weth_token.balanceOf(user_account.address)

    allowance = spa_token.allowance(user_account.address, buyback_single_spa_weth.address)
    if(allowance <= 0):
        spa_token.approve(buyback_single_spa_weth.address, 10000000, {"from": user_account})

    buyback_single_spa_weth.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})

    time.sleep(10)

    balance2 = weth_token.balanceOf(user_account.address)
    transferedBalance  = balance2 - balance1
    assert transferedBalance > 0



def test_swap_with_no_pool(buyback_single_sol_spa, user_account, weth_token, spa_token):
    failed = False
    allowance = spa_token.allowance(user_account.address, buyback_single_sol_spa.address)
    if(allowance <= 0):
        spa_token.approve(buyback_single_sol_spa.address, 10000000, {"from": user_account})

    try:
        buyback_single_sol_spa.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False



def test_swap_insufficient_balance(buyback_single_spa_weth, user_account_with_no_balance, weth_token, spa_token):
    failed = False
    allowance = spa_token.allowance(user_account_with_no_balance.address, buyback_single_spa_weth.address)
    try:
        if(allowance <= 0):
            spa_token.approve(buyback_single_spa_weth.address, 1000, {"from": user_account_with_no_balance})

        with reverts("Insufficient funds"):
            buyback_single_spa_weth.swap(100000, {"from": user_account_with_no_balance, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False
  

def test_swap_invalid_pool_fee(buyback_single_spa_weth_pf05, user_account, weth_token, spa_token):
    failed = False
    allowance = spa_token.allowance(user_account.address, buyback_single_spa_weth_pf05.address)
    if(allowance <= 0):
        spa_token.approve(buyback_single_spa_weth_pf05.address, 10000000, {"from": user_account})

    try:
        buyback_single_spa_weth_pf05.swap(100000, {"from": user_account, "allow_revert": True, "gas_limit": 1000000})
        failed = True
    except Exception:
       failed = False
    assert failed == False














    

