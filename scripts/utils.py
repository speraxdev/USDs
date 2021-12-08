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

    
    