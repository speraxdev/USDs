from brownie import (
    network
)

def getYorN(msg):
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
    answer = getYorN(msg)
    if answer == "y":
        return
    elif answer == "n":
        print("Exiting...")
        exit()
       

def choice(msg):
    """
    Prompts the user to choose y or n. If y, return true. If n, return false
    """
    answer = getYorN(msg)
    if answer.lower() == "y":
        return True
    else:
        return False

def onlyTestnet(func):
    """
    Checks if the network is testnet. If not does nothing
    """
    if network.show_active() == 'arbitrum-rinkeby':
        func()

def getContractToUpgrade(contract, scopeDict):
    version = getVersion(f"Enter version to upgrade {contract} to:")
    confirm(f"Confirm you want to upgrade {contract} to version {version}")
    return (getContractVersionedName(contract, version), getContract(contract, version, scopeDict))

def getVersion(msg):
    """
    Prompts the user to enter a version number.
    """
    while True:
        version = input(msg)
        try:
            version = int(version)
            return version
        except ValueError:
            print("Please enter a number.")

def getContractVersionedName(contract, version):
    return contract + "V" + str(version)

def getContract(contract, version, scopeDict):
    """
    Takes string and gets contract. Requires all brownie items to be imported ("import * from brownie")
    """
    contract_name = getContractVersionedName(contract, version)
    return scopeDict[contract_name]


    