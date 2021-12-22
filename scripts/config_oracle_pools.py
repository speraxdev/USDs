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
    spa_pool_address = input("Enter SPA-USDC Pool address: ").strip()
    if len(spa_pool_address) == 0:
        print("\nMissing SPA Pool address\n")
        return
    usds_pool_ready = input("Is the USDs-USDC pool ready? (y/n)").strip()
    if usds_pool_ready != 'y' and usds_pool_ready != 'n':
        print("\nInvalid Input (y/n)\n")
        return
    if usds_pool_ready == 'y':
        usds_pool_address = input("Enter USDs Pool address: ").strip()
        if len(usds_pool_address) == 0:
            print("\nMissing USDs Pool address\n")
            return
    if usds_pool_ready == 'n':
    spa_pool = brownie.interface.IUniswapV3Pool(spa_pool_address)
    spa_pool.increaseObservationCardinalityNext(20, {'from': owner})
    if usds_pool_ready == 'y':
        usds_pool = brownie.interface.IUniswapV3Pool(usds_pool_address)
        spa_pool.increaseObservationCardinalityNext(20, {'from': owner})
