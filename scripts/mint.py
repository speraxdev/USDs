import sys
import signal
import click
from brownie import (
    VaultCore,
    accounts,
    network,
    Contract,
    chain,
)

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    # contract owner account
    owner = accounts.load(
        click.prompt(
            "admin account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"contract owner account: {owner.address}\n")

    vault_proxy_address = input("Enter VaultCore proxy address: ").strip()
    if len(vault_proxy_address) == 0:
        print("\nMissing Vault proxy address\n")
        return

    print(f"\n{network.show_active()}:\n")
    vault_proxy = Contract.from_abi(
        "VaultCore",
        vault_proxy_address,
        VaultCore.abi
    )

    mint = ''
    while len(mint) == 0:
        mint = input("mint tokens (y/n)?: ")
        if mint == 'n':
            continue
        if mint == 'y':
            collateral_address = input("Enter collateral address: ")
            if len(collateral_address) == 0:
                print("\nCancelling operation")
                continue
            deadline = int(input("deadline (minutes): ")) * 60
            deadline += chain.time() # add current time (epoch)
            print("Mint with:")
            print("\t1. USDs")
            print("\t2. SPA")
            print("\t3. collateral")
            stake = ''
            while len(stake) == 0:
                stake = input("Enter option (1/2/3): ")
                if stake == '1':
                    amount = input("amount of USDs to mint: ")
                    if len(amount) == 0 or int(amount) == 0:
                        print("\nCancelling operation")
                        continue
                    slippage_collateral = input("collateral slippage (%): ")
                    if len(slippage_collateral) == 0:
                        slippage_collateral = 0
                    slippage_collateral = amount - amount * slippage_collateral * 100
                    slippage_spa = input("SPA slippage (%): ")
                    if len(slippage_spa) == 0:
                        slippage_spa = 0
                    slippage_spa = amount - amount * slippage_spa * 100
                    # mint USDs by specifying amount of USDs to mint
                    vault_proxy.mintWithUSDs(
                        collateral_address,
                        int(amount),
                        slippage_collateral,
                        slippage_spa,
                        deadline
                    )
                if stake == '2':
                    amount = input("amount of SPA to burn: ")
                    if len(amount) == 0 or int(amount) == 0:
                        print("\nCancelling operation")
                        continue
                    slippage_collateral = input("collateral slippage (%): ")
                    if len(slippage_collateral) == 0:
                        slippage_collateral = 0
                    slippage_collateral = amount - amount * slippage_collateral * 100
                    slippage_usds = input("USDs slippage (%): ")
                    if len(slippage_usds) == 0:
                        slippage_usds = 0
                    slippage_usds = amount - amount * slippage_usds * 100
                    # mint USDs by specifying amount of SPA to burn
                    vault_proxy.mintWithSPA(
                        collateral_address,
                        int(amount),
                        slippage_usds,
                        slippage_collateral,
                        deadline
                    )
                if stake == '3':
                    amount = input("amount of collateral to stake: ")
                    if len(amount) == 0 or int(amount) == 0:
                        print("\nCancelling operation")
                        continue
                    slippage_usds = input("USDs slippage (%): ")
                    if len(slippage_usds) == 0:
                        slippage_usds = 0
                    slippage_usds = amount - amount * slippage_usds * 100
                    slippage_spa = input("SPA slippage (%): ")
                    if len(slippage_spa) == 0:
                        slippage_spa = 0
                    slippage_spa = amount - amount * slippage_spa * 100
                    # mint USDs by specifying amount of collateral to stake
                    vault_proxy.mintWithColla(
                        collateral_address,
                        int(amount),
                        slippage_usds,
                        slippage_spa,
                        deadline
                    )