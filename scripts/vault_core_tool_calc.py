from brownie import (
    VaultCoreTools,
    accounts,
    interface
)
import sys
import os

vaultCoreAddr = '0xF783DD830A4650D2A8594423F123250652340E3f'
vaultCoreTools = None

def custom_print(message, value):
    print(message, '{:.2e}'.format(value))

def print_events(txn):
    print('\n**Printing events**')
    for ev in txn.events['Debug']:
        print(ev[0]['func'], '-> ', ev[0]['info'], ': ', '{:.3e}'.format(ev[0]['value']))  

def assert_calculation(expected, actual):
    if expected == actual: 
        print('*** calculations match yay!!! ***')
    else:
        print('*** Calculation mismatch :( ***')

def main(): 
    print('\nRunning script')
    owner = accounts.add(os.getenv('LOCAL_ACCOUNT_PRIVATE_KEY')) # minter: '0x07e3180be78c83d77dfa4dfee2debe9e301a84f67549e9b2a2b0043125015218'
    vaultCore = interface.IVaultCore(vaultCoreAddr)
    oracle = interface.IOracle(vaultCore.oracleAddr())
    # Vault core constants
    chi_alpha = vaultCore.chi_alpha()
    chi_beta = vaultCore.chi_beta() 
    chi_prec = vaultCore.chi_prec()
    chi_beta_prec = vaultCore.chi_beta_prec()
    chi_init = vaultCore.chiInit()
    chi_gamma = vaultCore.chi_gamma()
    chi_gamma_prec = vaultCore.chi_gamma_prec()
    swap_fee_a = vaultCore.swapFee_a()
    swap_fee_a_prec = vaultCore.swapFee_a_prec()
    swap_fee_prec = vaultCore.swapFee_prec()
    swap_fee_A = vaultCore.swapFee_A()
    swap_fee_A_prec = vaultCore.swapFee_A_prec()
    swap_fee_p = vaultCore.swapFee_p()
    swap_fee_p_prec = vaultCore.swapFee_p_prec()
    swap_fee_theta = vaultCore.swapFee_theta() 
    swap_fee_theta_prec = vaultCore.swapFee_theta_prec()
    usds_in_out_ratio_prec = oracle.USDsInOutRatio_prec()
        
    print(f'contract owner account: {owner.address}\n')
    global vaultCoreTools 
    if not vaultCoreTools:
        vaultCoreTools = VaultCoreTools.deploy({'from': owner});
    print('vaultCoreTools deployed at: ', vaultCoreTools)
    while(True):
        try:
            choice = int(input('\nOption:- \n0 -> To end test \n1 -> To test with custom val \n2 -> To test with pool value \n3 -> To interact in console \n-> '))
            if(choice == 0):
                sys.exit()
            
            elif(choice == 1):
                usds_price = int(float(input('Enter priceUSDs: ')))
                usds_prec = int(float(input('Enter precisionUSDs: ')))
                usds_price_avg = int(float(input('Enter priceUSDs_Average: ')))
                block_passed = int(float(input('Enter blockPassed: ')))
                collateral_ratio = int(float(input('Enter collateralRatio: ')))
                usds_in_out_ratio = int(float(input('Enter USDsInOutRatio: ')))
                vaultCoreTools.setPriceUSDs(usds_price)
                vaultCoreTools.setPrecisionUSDs(usds_prec)
                vaultCoreTools.setAvgPriceUSDs(usds_price_avg)
                vaultCoreTools.setBlockPassed(block_passed)
                vaultCoreTools.setCollateralRatio(collateral_ratio)
                vaultCoreTools.setUSDsInOutRatio(usds_in_out_ratio)
                           
            elif(choice == 2):
                vaultCoreTools.getOriginalValues(vaultCoreAddr)
                usds_price = vaultCoreTools.priceUSDs()
                usds_prec = vaultCoreTools.precisionUSDs()
                usds_price_avg = vaultCoreTools.priceUSDs_Average()
                block_passed = vaultCoreTools.blockPassed()
                collateral_ratio = vaultCoreTools.collateralRatio()
                usds_in_out_ratio = vaultCoreTools.USDsInOutRatio()
                print('\nValues reverted to original')
            
            else:
                print('\n*** NOTE: You can resume by calling main() **\n')
                break
            
            print('\n*** Printing vaultCoreTool values ***\n')
            custom_print('priceUSDs: ', usds_price)
            custom_print('priceUSDs_Average: ', usds_price_avg)
            custom_print('precisionUSDs: ', usds_prec)
            custom_print('blockPassed: ', block_passed)
            custom_print('collateralRatio: ', collateral_ratio)
            custom_print('USDsInOutRatio: ', usds_in_out_ratio)
            
            print('\n*** Printing vaultCore values ***\n')
            custom_print('chi_alpha: ', chi_alpha)
            custom_print('chi_beta: ', chi_beta)
            custom_print('chi_prec: ', chi_prec)
            custom_print('chi_beta_prec: ', chi_beta_prec)
            custom_print('chi_init: ', chi_init)
            custom_print('chi_gamma: ', chi_gamma)
            custom_print('chi_gamma_prec: ', chi_gamma_prec)
            custom_print('swap_fee_a: ', swap_fee_a)
            custom_print('swap_fee_a_prec: ', swap_fee_a_prec)
            custom_print('swap_fee_prec: ', swap_fee_prec)
            custom_print('swap_fee_A: ', swap_fee_A)
            custom_print('swap_fee_A_prec: ', swap_fee_A_prec)
            custom_print('swap_fee_p: ', swap_fee_p)
            custom_print('swap_fee_p_prec: ', swap_fee_p_prec)
            custom_print('swap_fee_theta: ', swap_fee_theta)
            custom_print('swap_fee_theta_prec: ', swap_fee_theta_prec)
            custom_print('usds_in_out_ratio_prec: ', usds_in_out_ratio_prec)

            calc_chi_target = 0
            alpha_adjustment = chi_alpha * block_passed
            beta_adjustment =  int (chi_beta * chi_prec * int((usds_prec - usds_price) ** 2)) / int(chi_beta_prec * usds_prec * usds_prec)
            if(usds_price >= usds_prec):
                calc_chi_target =  chi_init + beta_adjustment - alpha_adjustment                      
            else:
                calc_chi_target = chi_init - beta_adjustment - alpha_adjustment
            
            if(calc_chi_target > chi_prec):
                calc_chi_target = chi_prec
                                
            txn = vaultCoreTools.chiMint(vaultCoreAddr)
            custom_print('\nchiMint: ', txn.return_value)
            custom_print('calc_chi_target', calc_chi_target)
            assert_calculation(calc_chi_target, txn.return_value)
            print_events(txn)
            
            calc_chi_redeem = calc_chi_target - (chi_gamma * max(0,(calc_chi_target - collateral_ratio))/int(chi_gamma_prec))  
            txn = vaultCoreTools.chiRedeem(vaultCoreAddr)
            custom_print('\nchiRedeem: ', txn.return_value)
            custom_print('calc_chi_redeem', calc_chi_redeem) 
            assert_calculation(calc_chi_redeem, txn.return_value)
            print_events(txn)
            
            p = swap_fee_p * usds_prec / swap_fee_p_prec
            calc_swap_fee_in = swap_fee_prec / 1000
            if(p > usds_price_avg):
                t = (((p - usds_price_avg) * swap_fee_theta / swap_fee_theta_prec) ** 2 ) 
                t = (t * swap_fee_prec) / (usds_prec ** 2)
                t = t / 100
                calc_swap_fee_in += t
                
                if (calc_swap_fee_in >= swap_fee_prec):
                    calc_swap_fee_in = swap_fee_prec
                
                                
            txn = vaultCoreTools.calculateSwapFeeIn(vaultCoreAddr)
            custom_print('\ncalculateSwapFeeIn: ', txn.return_value)
            custom_print('calc_swap_fee_in: ', calc_swap_fee_in)
            assert_calculation(calc_swap_fee_in, txn.return_value)
            print_events(txn)
            
            a = swap_fee_a * usds_in_out_ratio_prec / swap_fee_a_prec
            calc_swap_fee_out = swap_fee_prec / 1000
            if(usds_in_out_ratio > a): 
                calc_swap_fee_out = min(swap_fee_prec, swap_fee_A ** (usds_in_out_ratio - a) )
            
            txn = vaultCoreTools.calculateSwapFeeOut(vaultCoreAddr)
            custom_print('\ncalculateSwapFeeOut: ', txn.return_value)
            custom_print('calc_swap_fee_out: ', calc_swap_fee_out)
            assert_calculation(calc_swap_fee_out, txn.return_value)
            print_events(txn)
            
            
        except Exception as e:
            print("\n* Printing error: ", e)
    
    