import sys
import signal
import click
import brownie

def signal_handler(signal, frame):
    sys.exit(0)

# this script helps increase slots of reserved for moving average on a Uni V3
# pool
# Oracle use one pool (SPA-USDC) to get the price of SPA
# and the other (USDs-USDC) to get the price of USDs
def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)
    # log in account
    owner = brownie.accounts.load(
        click.prompt(
            "account",
            type=click.Choice(brownie.accounts.load())
        )
    )
    print(f"account: {owner.address}\n")

    print(f"\nConfigure Uniswap pools on Oracle on {brownie.network.show_active()}:\n")
    pool_address = input("Enter Pool address: ").strip()
    if len(pool_address) == 0:
        print("\nMissing Pool address\n")
        return
    pool = brownie.interface.IUniswapV3Pool(pool_address)
    pool.increaseObservationCardinalityNext(20, {'from': owner})
