import signal
import click
import importlib
import brownie

def main():
    signal.signal(signal.SIGINT, signal_handler)
    # proxy admin account
    admin = accounts.load(
        click.prompt(
            "admin account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"admin account: {admin.address}\n")

    # contract owner account
    owner = accounts.load(
        click.prompt(
            "owner account",
            type=click.Choice(accounts.load())
        )
    )
    print(f"contract owner account: {owner.address}\n")

    proxy_admin = brownie.Contract.from_abi(
        'ProxyAdmin',
        '0x3E49925A79CbFb68BAa5bc9DFb4f7D955D1ddF25',
        ProxyAdmin.abi
    )
    new_usdc_strategy_logic = TwoPoolStrategyV2.deploy({'from': owner})
    proxy_admin.upgrade(
        '0xbF82a3212e13b2d407D10f5107b5C8404dE7F403',
        new_usdc_strategy_logic.address,
        {'from': admin}
    )
    new_usdc_strategy_logic.initialize(
        '0x7f90122bf0700f9e7e1f688fe926940e8839f353',
        vault_core.address,
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978',
        ['0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8','0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'],
        ['0x7f90122bf0700f9e7e1f688fe926940e8839f353','0x7f90122bf0700f9e7e1f688fe926940e8839f353'],
        '0xbF7E49483881C76487b0989CD7d9A8239B20CA41',
        0,
        '0xf3f98086f7B61a32be4EdF8d8A4b964eC886BBcd',
        {'from': owner}
    )
    new_usdt_strategy_logic = TwoPoolStrategyV2.deploy({'from': owner})
    proxy_admin.upgrade(
        '0xdc118F2F00812326Fe0De5c9c74c1c0c609d1eB4',
        new_usdt_strategy_logic.address,
        {'from': admin}
    )
    new_usdt_strategy_logic.initialize(
        '0x7f90122bf0700f9e7e1f688fe926940e8839f353',
        vault_core.address,
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978',
        ['0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8','0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'],
        ['0x7f90122bf0700f9e7e1f688fe926940e8839f353','0x7f90122bf0700f9e7e1f688fe926940e8839f353'],
        '0xbF7E49483881C76487b0989CD7d9A8239B20CA41',
        1,
        '0xf3f98086f7B61a32be4EdF8d8A4b964eC886BBcd',
        {'from': owner}
    )
