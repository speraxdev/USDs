import sys
import signal
from brownie import (
    ProxyAdmin,
    Oracle,
    OracleV2,
    VaultCore,
    VaultCoreV2,
    accounts,
    network,
    Contract,
)
import eth_utils

def signal_handler(signal, frame):
    sys.exit(0)

def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    else:
        return initializer.encode_input(*args)

def upgrade(
    account,
    proxy,
    newimplementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                newimplementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, newimplementation_address, {"from": account}
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                newimplementation_address, encoded_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo(newimplementation_address, {"from": account})
    return transaction
    
def main():
    # handle ctrl-C event
    signal.signal(signal.SIGINT, signal_handler)

    print("\nEnter admin account password:")
    try:
        admin = accounts.load(filename="admin.keystore")
    except ValueError:
        print("\nInvalid admin wallet or password\n")
        return
    except FileNotFoundError:
        print("\nFile not found: ~/.brownie/accounts/admin.json")
        return

    print("\nPress enter if you do not wish to upgrade a specific contract\n")
    vault_proxy_address = input("Enter VaultCore Proxy address: ")
    oracle_proxy_address = input("Enter Oracle Proxy address: ")

    initial_balance = admin.balance()

    # proxy admin contract
    proxy_admin = ProxyAdmin[-1]

    print(f"\n{network.show_active()}:\n")
    # retrieve contracts
    if vault_proxy_address:
        new_vault = VaultCoreV2.deploy(
            {'from': admin, 'gas_limit': 1000000000}
        )
        vault_proxy = Contract.from_abi(
            "VaultCore",
            vault_proxy_address,
            VaultCore.abi
        )
        upgrade(
            admin,
            vault_proxy,
            new_vault,
            proxy_admin_contract=proxy_admin
        )
        new_vault_proxy = Contract.from_abi(
            "VaultCoreV2",
            vault_proxy.address,
            VaultCoreV2.abi
        )
        print(f"Vault Core proxy address: {new_vault_proxy.address}")

    if oracle_proxy_address:
        oracle_proxy = Contract.from_abi("Oracle", oracle_proxy_address, Oracle.abi)