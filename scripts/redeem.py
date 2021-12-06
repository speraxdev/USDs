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

    collateral_address = input("Enter collateral address: ")
    if len(collateral_address) == 0:
        print("\nCancelling operation")
        return

    amount = input("amount of USDs to mint: ")
    if len(amount) == 0 or int(amount) == 0:
        print("\nCancelling operation")
        return

    slippage_collateral = input("collateral slippage (%): ")
    if len(slippage_collateral) == 0:
        slippage_collateral = 0
    slippage_collateral = amount - amount * slippage_collateral * 100
    slippage_spa = input("SPA slippage (%): ")
    if len(slippage_spa) == 0:
        slippage_spa = 0
    slippage_spa = amount - amount * slippage_spa * 100

    print(f"\n{network.show_active()}:\n")
    vault_proxy = Contract.from_abi(
        "VaultCore",
        vault_proxy_address,
        VaultCore.abi
    )

    redeem = ''
    while len(redeem) == 0:
        redeem = input("redeem tokens (y/n)?: ")
        if redeem == 'n':
            continue
        if redeem == 'y':
            collateral_address = input("Enter collateral address: ")
            if len(collateral_address) == 0:
                print("\nCancelling operation")
                return

            amount = input("amount of USDs to mint: ")
            if len(amount) == 0 or int(amount) == 0:
                print("\nCancelling operation")
                return

            slippage_collateral = input("collateral slippage (%): ")
            if len(slippage_collateral) == 0:
                slippage_collateral = 0
            slippage_collateral = amount - amount * slippage_collateral * 100

            slippage_spa = input("SPA slippage (%): ")
            if len(slippage_spa) == 0:
                slippage_spa = 0
            slippage_spa = amount - amount * slippage_spa * 100

            deadline = int(input("deadline (minutes): ")) * 60
            deadline += chain.time() # add current time (epoch)

            print(f"\n{network.show_active()}:\n")
            vault_proxy = Contract.from_abi(
                "VaultCore",
                vault_proxy_address,
                VaultCore.abi
            )

            vault_proxy.redeem(
                collateral_address,
                int(amount),
                slippage_collateral,
                slippage_spa,
                deadline
            )