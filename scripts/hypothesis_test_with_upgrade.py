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
factory = brownie.interface.IUniswapV3Factory('0x1F98431c8aD98523631AE4a59f267346ea31F984') 
usds = brownie.Contract.from_abi('USDs', '0xD74f5255D557944cf7Dd0E45FF521520002D5748', USDsL2.abi)
usdc = brownie.Contract.from_abi('USDC', '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', MockToken.abi)
nftm =  brownie.interface.INonfungiblePositionManager('0xC36442b4a4522E871399CD717aBDD847Ab11FE88')
owner = brownie.accounts.at('0xc28c6970D8A345988e8335b1C229dEA3c802e0a6')
def signal_handler(signal, frame):
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    pool =  factory.getPool(usds,usdc, 500)
    

    # global usds, usdc, nftm, owner
    # if not usds:
        # owner = brownie.accounts.add(os.getenv("0x07e3180be78c83d77dfa4dfee2debe9e301a84f67549e9b2a2b0043125015218")) # minter: '0x07e3180be78c83d77dfa4dfee2debe9e301a84f67549e9b2a2b0043125015218'
        
        # usdc =  MockToken.deploy(
        #     "USDc Token",
        #     "USDc",
        #     6,
        #     {'from': owner}
        # )
        # while(True):
        #     usds = USDsL2.deploy({
        #         'from': owner
        #     })
        #     if(usds.address.lower() < usdc.address.lower()):
        #         break
        
        # print('usdsL2: ', usds)
        # nftm = brownie.interface.INonfungiblePositionManager('0xC36442b4a4522E871399CD717aBDD847Ab11FE88')
        # usds.initialize('USDs', 'S', '0xB4F9A869fcfDc8D301E5a8f2fcDB655addEE3bCb', '0xB4F9A869fcfDc8D301E5a8f2fcDB655addEE3bCb', '0xB4F9A869fcfDc8D301E5a8f2fcDB655addEE3bCb', {'from':owner})
        # usds.mint(owner, 10**26, {'from':owner})
        # txn = nftm.createAndInitializePoolIfNecessary(usds, usdc, 500, 79224306130848112672356, {'from': owner})
        
        # usds.approve(nftm.address, 10**28, {'from':owner})
        # usdc.approve(nftm.address, 10**28, {'from': owner})    
        
    #   $ brownie run ./scripts/hypothesis_test.py --network arbitrum-main-fork -t -I  
    #   data = [usds, usdc, 500, -276420, -276220, 9999979817270147043, 9048980, 5243166300392573143, 4268818, owner, chain.time() + 100000]
    while(True):
        try: 
            choice = int(input('\nOption:- \n0 -> To end test \n1 -> Test  \n2 -> Test with rebase \n3 -> To interact in console \n-> '))
            if(choice == 0):
                sys.exit()
            
            elif(choice == 2):
                rebase_factor = random.uniform(1, 1.1)
                print('Rebase factor: ', rebase_factor)
                initial_totalSupply = usds.totalSupply()
                change_usds_tSupply = usds.changeSupply(usds.totalSupply()*rebase_factor , {'from': owner})
                non_rebasing_supply=usds.nonRebasingSupply()
                rebasing_credits_per_token=usds.rebasingCreditsPerToken()
                print(f"initial supply: {initial_totalSupply}\t\trebased: {change_usds_tSupply}") 
                print(f"Non rebasing Supply: {non_rebasing_supply}\t\trebasing credits per token: {rebasing_credits_per_token}") 
                                
                usds_desired = 9999979817270147043
                usdc_desired = 9048980
                usds_min = 524316630039
                usdc_min = 4268

                data = [usds, usdc, 500, -276420, -276220, usds_desired, usdc_desired, usds_min, usdc_min, owner, brownie.chain.time() + 100000]
                
                print(f"\namount 0: {usds_desired}\t\tmin: {usds_min}") 
                print(f"amount 1: {usdc_desired}\t\tmin: {usdc_min}") 
                balance0 = usds.balanceOf(pool)
                try:    
                    txn = nftm.mint(data, {'from': owner, 'gas_limit':12000000})
                except Exception as e:
                    print(e)
                    print('Error: ', txn.revert_msg)
                balance0_updated = usds.balanceOf(pool)
                balance_added = balance0_updated - balance0
                amount0 = txn.events['Transfer'][0]['value']
                print('Position: ', txn.return_value)
                print('initial pool balance: ', balance0)
                print('final pool balance: ', balance0_updated)
                print('balance_added: ', balance_added )
                print('amount0: ', amount0)
                print('Discrepancy: ', balance_added - amount0)
                
                # if(flag):
                #     change_usds_tSupply = usds.changeSupply(usds.totalSupply()/rebase_factor)
                
                
            elif(choice == 1):
                    # usds_desired = random.randint(10**18, 10**25)
                    # usdc_desired = random.randint(10**6, 10**13)
                    # usds_min = random.randint(10**18, int(usds_desired/100))
                    # usdc_min =random.randint(10**6, int(usdc_desired/100))

                    usds_desired = 9999979817270147043
                    usdc_desired = 9048980
                    usds_min = 524316630039
                    usdc_min = 4268

                    data = [usds, usdc, 500, -276420, -276220, usds_desired, usdc_desired, usds_min, usdc_min, owner, brownie.chain.time() + 100000]
                    
                    print(f"\namount 0: {usds_desired}\t\tmin: {usds_min}") 
                    print(f"amount 1: {usdc_desired}\t\tmin: {usdc_min}") 
                    balance0 = usds.balanceOf(pool)

                    try:    
                        txn = nftm.mint(data, {'from': owner, 'gas_limit':12000000})
                    except Exception as e:
                        print(e)
                        print('Error: ', txn.revert_msg)
                    balance0_updated = usds.balanceOf(pool)
                    balance_added = balance0_updated - balance0
                    amount0 = txn.events['Transfer'][0]['value']
                    print('Position: ', txn.return_value)
                    print('initial pool balance: ', balance0)
                    print('final pool balance: ', balance0_updated)
                    print('balance_added: ', balance_added )
                    print('amount0: ', amount0)
                    print('Discrepancy: ', balance_added - amount0)
            else: 
                break
    
        except Exception as e:
            print("\n* Printing error: ", e)



    

    
