from brownie import (
    USDsL2,
    MockToken
)
import signal
import random
import brownie
import os 
import sys

#   $ brownie run ./scripts/hypothesis_test.py --network arbitrum-main-fork -t -I  
#   data = [usds, usdc, 500, -276420, -276220, 9999979817270147043, 9048980, 5243166300392573143, 4268818, owner, chain.time() + 100000]
#  txn = nftm.mint(data, {'from': owner, 'gas_limit':1000000000000})
#  usds.changeSupply(2*usds.totalSupply())

# usdt = '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9'
usds = None
def signal_handler(signal, frame):
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    owner = brownie.accounts.add(os.getenv("0x07e3180be78c83d77dfa4dfee2debe9e301a84f67549e9b2a2b0043125015218")) # minter: '0x07e3180be78c83d77dfa4dfee2debe9e301a84f67549e9b2a2b0043125015218'

    global usds    
    if not usds:
        usdc =  MockToken.deploy(
            "USDc Token",
            "USDc",
            6,
            {'from': owner}
        )
        while(True):
            usds = USDsL2.deploy({
                'from': owner
            })
            if(usds.address.lower() < usdc.address.lower()):
                break
        
        print('usdsL2: ', usds)
        usds.initialize('USDs', 'S', '0xB4F9A869fcfDc8D301E5a8f2fcDB655addEE3bCb', '0xB4F9A869fcfDc8D301E5a8f2fcDB655addEE3bCb', '0xB4F9A869fcfDc8D301E5a8f2fcDB655addEE3bCb', {'from':owner})
        usds.mint(owner, 10000000000000000000000, {'from':owner})
        nftm = brownie.interface.INonfungiblePositionManager('0xC36442b4a4522E871399CD717aBDD847Ab11FE88')
        txn = nftm.createAndInitializePoolIfNecessary(usds, usdc, 500, 79224306130848112672356, {'from': owner})
        
        usds.approve(nftm.address, 1000000000000000000000000, {'from':owner})
        usdc.approve(nftm.address, 1000000000000000000000000, {'from': owner})    
        
    #   $ brownie run ./scripts/hypothesis_test.py --network arbitrum-main-fork -t -I  
    #   data = [usds, usdc, 500, -276420, -276220, 9999979817270147043, 9048980, 5243166300392573143, 4268818, owner, chain.time() + 100000]
    
    while(True):
        random_amount_0_desired= random.randint(10**18,10**25)
        random_amount_1_desired= random.randint(10**6,10**13)

        amount_0_min=random.randint(10**18,random_amount_0_desired)
        amount_1_min=random.randint(10**6,random_amount_1_desired)
        data = [usds, usdc, 500, -276420, -276220, random_amount_0_desired, random_amount_1_desired,amount_0_min, amount_1_min, owner, brownie.chain.time() + 100000]
        
        print(f"\nAmount 0 Desired: {random_amount_0_desired}\t\tAmount 1 Desired: {random_amount_1_desired}") 
        print(f"Min Amount 0: {amount_0_min}\t\tMin Amount 1: {amount_1_min}") 
        
        txn = nftm.mint(data, {'from': owner, 'gas_limit':12000000})
        print(txn.revert_msg)
        if random.randint(0,1)==1:
       
            rebase_factor=random.randint(2,99)
        
            initial_totalSupply=usds.totalSupply()
            change_usds_tSupply=usds.changeSupply(usds.totalsupply()*rebase_factor)
            non_rebasing_supply=usds.nonRebasingSupply()
            rebasing_credits_per_token=usds.rebasingCreditsPerToken()

            print(f"initial supply: {initial_totalSupply}\t\trebased: {change_usds_tSupply}") 
            print(f"Non rebasing Supply: {non_rebasing_supply}\t\trebasing credits per token: {rebasing_credits_per_token}") 

        
    # while(True):
    #     choice = int(input('\nOption:- \n0 -> To end test \n1 ->Add liquidity \n2-> To interact in console \n-> '))
    #     if(choice == 0):
    #         sys.exit()

    #     elif(choice == 1):
    #         lower_tick = int(float(input('Enter lower_tick: ')))
    #         upper_tick = int(float(input('Enter upper_tick: ')))
            
    #         usds_amount = int(float(input('Enter usds_amount: ')))
    #         usdc_amount = int(float(input('Enter usdc_amount: ')))
    #         usds_min_amount = int(float(input('Enter usds_min_amount: ')))
    #         usdc_min_amount = int(float(input('Enter usdc_min_amount: ')))
            
    #         usds.approve(nftm.address, usds_amount, {'from':owner})
    #         usdc.approve(nftm.address, usdc_amount, {'from': owner})
            
    #         data = [usds, usdc, 500, lower_tick, upper_tick, usds_amount, usdc_amount, usds_min_amount, usdc_min_amount, owner, brownie.chain.time() + 10000]
    #         txn = nftm.mint(data, {'from': owner, 'gas_limit':100000000000})
            
    #         print('Position: ', txn.return_val)
    #     else: 
    #         break


    

    
