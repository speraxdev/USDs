import sys
import signal
import click
import brownie

def signal_handler(signal, frame):
    sys.exit(0)

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

    # deploy buyBack
    buyback = brownie.Buyback.deploy(
        '0xD74f5255D557944cf7Dd0E45FF521520002D5748', #USDs
        '0xF783DD830A4650D2A8594423F123250652340E3f', #VaultCore
        {'from': owner, 'gas_limit': 500000000}
    )
    # configure buyback for USDC, USDT and CRV
    buyback.updateInputTokenInfo(
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', #USDC
        True,
        1,
        '0x0000000000000000000000000000000000000000',
        '0x0000000000000000000000000000000000000000',
        500,
        0,
        0,
        {'from': owner, 'gas_limit': 100000000}
    )
    buyback.updateInputTokenInfo(
        '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', #USDT
        True,
        2,
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', #USDC
        '0x0000000000000000000000000000000000000000',
        500,
        500,
        0,
        {'from': owner, 'gas_limit': 100000000}
    )
    buyback.updateInputTokenInfo(
        '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978', #CRV
        True,
        3,
        '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1', #WETH
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', #USDC
        3000,
        500,
        500,
        {'from': owner, 'gas_limit': 100000000}
    )
    vault_core = brownie.Contract.from_abi(
        'VaultCore',
        '0xF783DD830A4650D2A8594423F123250652340E3f', #Vault
        brownie.VaultCore.abi
    )
    # update USDC
    vault_core.updateCollateralInfo(
        '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', #USDC
        '0xbF82a3212e13b2d407D10f5107b5C8404dE7F403', #USDC_strategy
        True,
        80,
        buyback.address,
        True,
        {'from': owner, 'gas_limit': 100000000}
    )
    # update USDT
    vault_core.updateCollateralInfo(
        '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', #USDT
        '0xdc118F2F00812326Fe0De5c9c74c1c0c609d1eB4', #USDT_strategy
        True,
        80,
        buyback.address,
        True,
        {'from': owner, 'gas_limit': 100000000}
    )
    vault_core.updateStrategyRwdBuybackAddr(
        '0xbF82a3212e13b2d407D10f5107b5C8404dE7F403', #USDC_strategy
        buyback.address,
        {'from': owner, 'gas_limit': 100000000}
    )
    vault_core.updateStrategyRwdBuybackAddr(
        '0xdc118F2F00812326Fe0De5c9c74c1c0c609d1eB4', #USDT_strategy
        buyback.address,
        {'from': owner, 'gas_limit': 100000000}
    )
