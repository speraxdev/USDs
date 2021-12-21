import pytest
import json
import time
import brownie


def test_power(sperax, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax
    LIMIT_MAX_NUM = hex(0x200000000000000000000000000000001)
    LIMIT_MAX_NUM_2=hex(0x199999999999999999999999999999999)
    LIMIT_OPT_LOG_MAX_VAL = hex(0x15bf0a8b1457695355fb8ac404e7a79e3)
    tx = bancor.power(
        10,
        10,
        10,
        10,
        {'from': owner_l2.address})
    print("tx: ",tx)
    with brownie.reverts():
        tx = bancor.power(
            LIMIT_MAX_NUM,
            10,
            10,
            10,
            {'from': owner_l2.address})
    with brownie.reverts():
         tx = bancor.power(
            LIMIT_MAX_NUM_2,
            10,
            10,
            10,
            {'from': owner_l2.address})    
    with brownie.reverts():
         tx = bancor.power(
            LIMIT_OPT_LOG_MAX_VAL,
            1,
            1,
            1,
            {'from': owner_l2.address})    
def test_general_log(sperax, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax
    tx=bancor.generalLog(
    1,
     {'from': owner_l2.address}   
    )
    
    tx = bancor.generalLog(
             0,
            {'from': owner_l2.address})        

    tx = bancor.floorLog2(
             10,
            {'from': owner_l2.address})    

    tx = bancor.floorLog2(
             2,
            {'from': owner_l2.address})   
def test_general_floorLog2(sperax, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax

    tx = bancor.floorLog2(
             10,
            {'from': owner_l2.address})    

    tx = bancor.floorLog2(
             2,
            {'from': owner_l2.address})    
def test_general_find_position_in_max_exp_array(sperax, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax
    a= hex(0x03eab73b3bbfe282243ce2ffffffffffff)
    b= hex(0x03eab73b3bbfe282243ce1fffffffffffe)
    tx = bancor.findPositionInMaxExpArray(
             0,
            {'from': owner_l2.address})   
    print("tx0: ",tx) 
    tx = bancor.findPositionInMaxExpArray(
            a,
            {'from': owner_l2.address})
    print("tx a: ",tx)     
    tx = bancor.findPositionInMaxExpArray(
             b,
            {'from': owner_l2.address})
    print("tx b: ",tx)   

def test_general_exp(sperax, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax
    b= hex(0x03eab73b3bbfe282243ce1fffffffffffe)
    tx = bancor.generalExp(
             b,10,
            {'from': owner_l2.address})
    print("tx : ",tx)     
         
def test_optimal_log(sperax, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax
    a0= hex( 0xd3094c70f034de4b96ff7d5b6f99fcd9)
    tx = bancor.optimalLog(
             a0,
            {'from': owner_l2.address})   
    print("tx0: ",tx) 
    a1= hex(0xa45af1e1f40c333b3de1db4dd55f29a7)
    tx = bancor.optimalLog(
             a1,
            {'from': owner_l2.address})   
    print("tx1: ",tx)
    a1= hex(0x910b022db7ae67ce76b441c27035c6a1)
    tx = bancor.optimalLog(
             a1,
            {'from': owner_l2.address})   
    print("tx2: ",tx) 
    a1= hex(0x88415abbe9a76bead8d00cf112e4d4a8)
    tx = bancor.optimalLog(
             a1,
            {'from': owner_l2.address})   
    print("tx3: ",tx) 
    a1= hex(0x84102b00893f64c705e841d5d4064bd3)
    tx = bancor.optimalLog(
             a1,
            {'from': owner_l2.address})   
    print("tx4: ",tx) 
    a1= hex(0x8204055aaef1c8bd5c3259f4822735a2)
    tx = bancor.optimalLog(
             a1,
            {'from': owner_l2.address})   
    print("tx5: ",tx) 
    a1= hex(0x810100ab00222d861931c15e39b44e99)
    tx = bancor.optimalLog(
             a1,
            {'from': owner_l2.address})   
    print("tx6: ",tx) 
    a1= hex(0x808040155aabbbe9451521693554f733)
    tx = bancor.optimalLog(
             a1,
            {'from': owner_l2.address})   
    print("tx7: ",tx) 

def test_optimal_exp(sperax, owner_l2):
    (
        spa,
        usds_proxy,
        vault_core_tools,
        vault_proxy,
        oracle_proxy,
        strategy_proxy,
        buyback,
        buyback_multihop,
        bancor
    ) = sperax
    a0= hex( 0x010000000000000000000000000000001)
    tx = bancor.optimalExp(
             a0,
            {'from': owner_l2.address})   
    print("tx0: ",tx) 
    a0= hex( 0x020000000000000000000000000000001)
    tx = bancor.optimalExp(
             a0,
            {'from': owner_l2.address})   
    print("tx1: ",tx) 
    a0= hex( 0x040000000000000000000000000000001)
    tx = bancor.optimalExp(
             a0,
            {'from': owner_l2.address})   
    print("tx2: ",tx)
    a0= hex( 0x080000000000000000000000000000001)
    tx = bancor.optimalExp(
             a0,
            {'from': owner_l2.address})   
    print("tx3: ",tx) 
    a0= hex( 0x100000000000000000000000000000001)
    tx = bancor.optimalExp(
             a0,
            {'from': owner_l2.address})   
    print("tx4: ",tx) 
    a0= hex( 0x200000000000000000000000000000001)
    tx = bancor.optimalExp(
             a0,
            {'from': owner_l2.address})   
    print("tx5: ",tx) 
    a0= hex( 0x400000000000000000000000000000001)
    tx = bancor.optimalExp(
             a0,
            {'from': owner_l2.address})   
    print("tx6: ",tx) 