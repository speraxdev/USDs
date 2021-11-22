#!/usr/bin/python3
import os
import pytest
import eth_utils

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
def fee_vault(accounts):
    return accounts[3]

@pytest.fixture(scope="module", autouse=True)
def weth_token(Contract, network, USDsL2):
    # kovan network
    weth = ''
    abi = [{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_symbol","type":"string"},{"internalType":"uint8","name":"_decimals","type":"uint8"},{"internalType":"uint256","name":"_initialSupply","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"}],"name":"AllowTransfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"}],"name":"BlockTransfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"MintPaused","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"MintUnpaused","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Mintable","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Unmintable","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"recipients","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"name":"batchTransfer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burnFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mintForUSDs","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"mintPause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"mintPaused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"mintUnpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"mintableAccounts","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"mintableGroup","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"releaseAmount","type":"uint256"}],"name":"release","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"revokeAllMintable","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"bool","name":"allow","type":"bool"}],"name":"setMintable","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"timelockOf","outputs":[{"internalType":"uint256","name":"releaseTime","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"releaseTime","type":"uint256"}],"name":"transferWithLock","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"}]
#    if network.show_active() == 'kovan':
#        weth = '0xd0A1E359811322d97991E03f863a0C30C2cF029C'
#    if network.show_active() == 'rinkeby':
#        weth = '0xd0A1E359811322d97991E03f863a0C30C2cF029C'
#    else: # default to ganache local development
        # reusing USDsL2 as a ERC20 input token for testing purposes
    weth = USDsL2.deploy(
        {'from': owner_l2}
    )
    abi = USDsL2.abi
    
    return Contract.from_abi("ERC20", weth, abi)

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
    weth_token,
    Contract,
    admin,
    owner_l2,
    fee_vault
):
    # Arbitrum rinkeby:
    price_feed_eth_arbitrum_testnet = '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
    weth_arbitrum_testnet = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'
    l2_gateway = '0x9b014455AcC2Fe90c52803849d0002aeEC184a06'

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

    #buyback = Contract.from_abi("BuybackSingle",  BuybackSingle[-1].address, BuybackSingle.abi)
    buyback = BuybackSingle.deploy(
        '0xE592427A0AEce92De3Edee1F18E0157C05861564', # swap router address
        usds_proxy.address,
        weth_token, # input token
        vault_proxy.address,
        fee_vault
    )

    oracle_proxy.initialize(
        price_feed_eth_arbitrum_testnet,
        spa.address,
        weth_arbitrum_testnet,
        {'from': owner_l2}
    )
    oracle_proxy.updateUSDsAddress(
        usds_proxy.address,
        {'from': owner_l2}
    )

    vault_proxy.initialize(
        spa.address,
        vault_core_tools.address,
        fee_vault,
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

@pytest.fixture(scope="module", autouse=True)
def user_account(accounts):
    WALLET_PRIVATE_KEY = os.environ.get('WALLET_PRIVATE_KEY')
    # default to ganache local development
    if len(WALLET_PRIVATE_KEY) == 0:
        return accounts[4]
    return accounts.add(WALLET_PRIVATE_KEY)

@pytest.fixture(autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass
