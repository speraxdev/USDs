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

# this script helps increase slots of reserved for moving average on a Uni V3
# pool
# Oracle use one pool (SPA-USDC) to get the price of SPA
# and the other (USDs-USDC) to get the price of USDs
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
    pool_address = input("Enter Pool address: ").strip()
    if len(pool_address) == 0:
        print("\nMissing Pool address\n")
        return
    pool = brownie.interface.IUniswapV3Pool(pool_address)
    pool.increaseObservationCardinalityNext(20, {'from': owner})
