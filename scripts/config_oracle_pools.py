import sys
import signal
import brownie
from brownie import (
    Oracle,
    network,
    Contract,
    accounts
)

def signal_handler(signal, frame):
    sys.exit(0)

# this script configures the Uniswap pool addresses in Oracle
# Oracle use one pool (SPA-ETH) to get the price of SPA
# and the other (USDs-USDC) to get the price of USDs
# note: configure the pool for SPA first
def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    print("\nEnter contract owner account password:")
    try:
        owner = accounts.load(filename="minter.keystore")
    except ValueError:
        print("\nInvalid owner wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/minter.json")
        return

    print(f"\nConfigure Uniswap pools on Oracle on {network.show_active()}:\n")
    oracle_address = input("Enter Oracle address: ").strip()
    if len(oracle_address) == 0:
        print("\nMissing Oracle address\n")
        return
    spa_l2_address = input("Enter SPA address: ").strip()
    if len(spa_l2_address) == 0:
        print("\nMissing SPA address\n")
        return
    spa_pool_address = input("Enter SPA-ETH Pool address: ").strip()
    if len(spa_pool_address) == 0:
        print("\nMissing SPA Pool address\n")
        return
    usds_pool_ready = input("Is the USDs-USDC pool ready? (y/n)").strip()
    if usds_pool_ready != 'y' and usds_pool_ready != 'n':
        print("\nInvalid Input (y/n)\n")
        return

    weth_address = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
    usdc_address = '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8'

    if network.show_active() == 'arbitrum-rinkeby':
        weth_address = '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681'
        usdc_address = '0x09b98f8b2395d076514037ff7d39a091a536206c'

    if usds_pool_ready == 'y':
        usds_pool_address = input("Enter SPA Pool address: ").strip()
        if len(usds_pool_address) == 0:
            print("\nMissing USDs Pool address\n")
            return
    if usds_pool_ready == 'n':
        usds_pool_address = '0x0000000000000000000000000000000000000000'

    oracle = Contract.from_abi(
        "Oracle",
        oracle_address,
        Oracle.abi
    )

    txn = oracle.updateOraclePoolsAddress(
        weth_address,
        usdc_address,
        usds_pool_address,
        spa_pool_address,
        {'from': owner, 'gas_limit': 10000000, 'allow_revert' : True}
    )

    # increaseObservationCardinalityNext to support moving averge price feed

    spa_pool = brownie.interface.IUniswapV3Pool(spa_pool_address)
    spa_pool.increaseObservationCardinalityNext(20, {'from': owner})
    if usds_pool_ready == 'y':
        usds_pool = brownie.interface.IUniswapV3Pool(usds_pool_address)
        spa_pool.increaseObservationCardinalityNext(20, {'from': owner})
