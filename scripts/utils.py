from brownie import *
import sys
import signal
from .constants import (
    wSPAL1_file,
    SPAL2_file,
    USDs_file
)
import json
# network = brownie.network

def signal_handler(signal, frame):
    sys.exit(0)

def _getYorN(msg):
    while True:
        answer = input(msg + " [y/n] ")
        lowercase_answer = answer.lower()
        if lowercase_answer == "y" or lowercase_answer == "n":
            return lowercase_answer
        else:
            print("Please enter y or n.")

def confirm(msg):
    """
    Prompts the user to confirm an action.
    If they hit yes, nothing happens, meaning the script continues.
    If they hit no, the script exits.
    """
    answer = _getYorN(msg)
    if answer == "y":
        return
    elif answer == "n":
        print("Exiting...")
        exit()
       

def choice(msg):
    """
    Prompts the user to choose y or n. If y, return true. If n, return false
    """
    answer = _getYorN(msg)
    if answer.lower() == "y":
        return True
    else:
        return False

def onlyDevelopment(func):
    """
    Checks if the network is in the list of testnet or mainnet forks. 
    If so, it calls the function
    If not does nothing
    """
    dev_networks = [
        'arbitrum-rinkeby', 
        'arbitrum-main-fork', 
        'development', 
        'geth-dev', 
        'rinkeby'
    ]
    if network.show_active() in dev_networks: 
        func() # can also just return t/f

def getAddressFromNetwork(testnetAddr, mainnetAddr):
    """
    Checks if network is in the list of testnets
    If so, returns testnet address
    If not, returns mainnet address
    """
    testnets = [
        'arbitrum-rinkeby', 
        'rinkeby'
    ]
    if network.show_active() in testnets:
        return testnetAddr
    return mainnetAddr


def getContractToUpgrade(contract):
    version = getNumber(f"Enter version to upgrade {contract} to:")
    confirm(f"Confirm you want to upgrade {contract} to version {version}")
    return (_getContractVersionedName(contract, version), _getContract(contract, version))

def getNumber(msg):
    """
    Prompts the user to enter a number. Checks that it is a number.
    """
    while True:
        version = input(msg)
        try:
            version = int(version)
            return version
        except ValueError:
            print("Please enter a number.")

def _getContractVersionedName(contract, version):
    return contract + "V" + str(version)

def _getContract(contract, version):
    """
    Takes string and gets contract. Requires all brownie items to be imported ("import * from brownie")
    """
    contract_name = _getContractVersionedName(contract, version)
    return globals()[contract_name]

def editAddressFile(path, address, property=""):
    """
    Edits the address file.
    """
    with open(path, "r") as file:
        data = json.load(file)
    testnets = [
        'arbitrum-rinkeby', 
        'rinkeby'
    ]
    if network.show_active() in testnets:
        net = "testnet"
    else:
        net = "mainnet"
    if (len(property) > 0):
        data[net][property] = address
    else:
        data[net] = address
    with open(path, "w") as file:
        json.dump(data, file)


    