import signal
import click
import importlib
import brownie
from .constants import (
    mainnetAddresses,
    testnetAddresses,
)
from .utils import (
    confirm,
    choice,
    onlyDevelopment,
    getAddressFromNetwork,
    getContractToUpgrade,
    signal_handler
)

accounts = brownie.accounts
network = brownie.network
Contract = brownie.Contract
VaultCore = brownie.VaultCore
def signal_handler(signal, frame):
    sys.exit(0)

# this script turn on/off swap fee of USDs minting and redeeming
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
    vault_proxy_address = getAddressFromNetwork(
        testnetAddresses.upgrade.vault_core_proxy,
        mainnetAddresses.upgrade.vault_core_proxy
    )
    print(f"account: {owner.address}\n")
    confirm(f"Confirm that the Vault Core's proxy address is {vault_proxy_address}")
    swap_in_fee = choice(f"Do you wish to turn on/off swap in fee on {vault_proxy_address}? y = on, n = off")
    swap_out_fee = choice(f"Do you wish to turn on/off swap out fee on {vault_proxy_address}? y = on, n = off")
    vaultCore = Contract.from_abi(
        "VaultCore",
        vault_proxy_address,
        VaultCore.abi
    )
    vaultCore.updateSwapInOutFeePermission(swap_in_fee, swap_out_fee, {'from': owner})
