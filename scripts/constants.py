import json
import os

cwd = os.getcwd()
wSPAL1_file = cwd + '/scripts/constants/wSPAL1.json'
SPAL2_file = cwd + '/scripts/constants/SPAL2.json'
USDs_file = cwd + '/scripts/constants/USDs.json'
Strategies_file = cwd + '/scripts/constants/Strategies.json'
with open(wSPAL1_file) as f:
    wSPAL1 = json.load(f)
with open(SPAL2_file) as f:
    SPAL2 = json.load(f)
with open(USDs_file) as f:
    USDs = json.load(f)
with open(Strategies_file) as f:
    Strategies = json.load(f)



class DeployAddresses:
    def __init__(self, L1_wSPA, L1_USDs, fee_vault, L2_SPA):
        self.L1_wSPA = L1_wSPA
        self.L1_USDs = L1_USDs
        self.fee_vault = fee_vault
        self.L2_SPA = L2_SPA

class UpgradeAddresses:
    def __init__(self, bancor_formula_address, vault_core_tools_proxy, vault_core_proxy, oracle_proxy, USDs_l2_proxy):
        self.bancor_formula_address = bancor_formula_address
        self.vault_core_tools_proxy = vault_core_tools_proxy
        self.vault_core_proxy = vault_core_proxy
        self.oracle_proxy = oracle_proxy
        self.USDs_l2_proxy = USDs_l2_proxy

class ThirdPartyAddresses:
    def __init__(self, l2_gateway, chainlink_usdc_price_feed, usdc_arbitrum, chainlink_flags):
        self.l2_gateway = l2_gateway
        self.chainlink_usdc_price_feed = chainlink_usdc_price_feed
        self.usdc_arbitrum = usdc_arbitrum
        self.chainlink_flags = chainlink_flags

class Addresses:
    def __init__(self, deploy, upgrade, third_party, collaterals):
        self.deploy = deploy
        self.upgrade = upgrade
        self.third_party = third_party
        self.collaterals = collaterals

# testnet
## Note: the feeVault can be anything in testnet. here it's 0xdeadbeef...
testnet_deploy_addresses = DeployAddresses(
    wSPAL1['testnet'], #L1_wSPA
    "0x0000000000000000000000000000000000000000", #L1_USDs
    ## Note: the feeVault can be anything in testnet. here it's 0xdeadbeef...
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef", #L1_feeVault
    SPAL2['testnet'] #L2_SPA
    )

## Note: these change after you deploy the contracts, so deploy first and then put those addresses here.
testnet_upgrade_addresses = UpgradeAddresses(
    USDs['testnet']['bancor_formula'], #bancor_formula_address
    USDs['testnet']['vault_core_tools_proxy'], #vault_core_tools_proxy
    USDs['testnet']['vault_core_proxy'], #vault_core_proxy
    USDs['testnet']['oracle_proxy'], #oracle_proxy
    USDs['testnet']['USDs_l2_proxy'] #USDs_l2_proxy
    )

testnet_third_party_addresses = ThirdPartyAddresses(
    '0x9b014455AcC2Fe90c52803849d0002aeEC184a06', #l2_gateway
    '0xe020609A0C31f4F96dCBB8DF9882218952dD95c4', #chainlink_usdc_price_feed
    '0x09b98f8b2395d076514037ff7d39a091a536206c', #usdc_arbitrum
    '0x491B1dDA0A8fa069bbC1125133A975BF4e85a91b'  #chainlink_flags
    )

testnet_collaterals = {
    # USDC
    '0x09b98f8b2395d076514037ff7d39a091a536206c': '0xe020609A0C31f4F96dCBB8DF9882218952dD95c4',
    # WETH
    '0xB47e6A5f8b33b3F17603C83a0535A9dcD7E32681': '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8',
    # Mock_USDT
    '0x396F40A99Ff1aD00d65864C309cd8b667baADFb8': '0xb1Ac85E779d05C2901812d812210F6dE144b2df0',
    # Mock_WBTC
    '0x58a86f5b3F1b9D4A6189D34fBa458414338e986a': '0x0c9973e7a27d00e656B9f153348dA46CaD70d03d',
    # Mock_DAI
    '0x2Bad5c5c33c560954481dF93Ed5ff35efA5f5410': '0xcAE7d280828cf4a0869b26341155E4E9b864C7b2'
    }

testnetAddresses = Addresses(
    testnet_deploy_addresses,
    testnet_upgrade_addresses,
    testnet_third_party_addresses,
    testnet_collaterals
    )

# mainnet

## TODO: Add mainnet addresses
## the deploy addresses are needed first
## then when deployed, you can put the proxy addresses here for upgrades

mainnet_deploy_address = DeployAddresses(
    ## Note: these need to be added. here it's  0xdeadbeef in the meantime...
    wSPAL1['mainnet'], #L1_wSPA NOTE: this is a wrong address. only here for testing purpose
    "0x0000000000000000000000000000000000000000", #L1_USDs NOTE: this is a wrong address. only here for testing purpose
    "0x4F987B24bD2194a574bB3F57b4e66B7f7eD36196", #L2_feeVault NOTE: this is a wrong address. only here for testing purpose
    SPAL2['mainnet'] #L2_SPA. NOTE: this is a wrong address. only here for testing purpose
    )

mainnet_upgrade_address = UpgradeAddresses(
    ## Note: these need to be added. here it's  0xdeadbeef in the meantime...
    USDs['mainnet']['bancor_formula'], #bancor_formula_address
    USDs['mainnet']['vault_core_tools_proxy'], #vault_core_tools_proxy
    USDs['mainnet']['vault_core_proxy'], #vault_core_proxy
    USDs['mainnet']['oracle_proxy'], #oracle_proxy
    USDs['mainnet']['USDs_l2_proxy'] #USDs_l2_proxy
    )

mainnet_third_party_address = ThirdPartyAddresses(
    '0x096760F208390250649E3e8763348E783AEF5562', #l2_gateway
    '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3', #chainlink_usdc_price_feed
    '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', #usdc_arbitrum
    '0x3C14e07Edd0dC67442FA96f1Ec6999c57E810a83' #chainlink_flags
    )

mainnet_collaterals = {
    # USDC
    '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8': '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3',
    # USDT
    '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9': '0x3f3f5dF88dC9F13eac63DF89EC16ef6e7E25DdE7',
    # DAI
    '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1': '0xc5C8E77B397E531B8EC06BFb0048328B30E9eCfB',
    # WBTC
    '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f': '0x6ce185860a4963106506C203335A2910413708e9',
    # WETH
    '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1': '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612'
    }

mainnetAddresses = Addresses(
    mainnet_deploy_address,
    mainnet_upgrade_address,
    mainnet_third_party_address,
    mainnet_collaterals
    )

class TokenDetails:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

USDs_token_details = TokenDetails("Sperax USD", "USDs")

wSPAL1_token_details = TokenDetails("Wrapped Sperax", "wSPA")

SPAL2_token_details = TokenDetails("Sperax", "SPA")

class L1DeployAddresses:
    def __init__(self, L1_SPA, bridge, router):
        self.L1_SPA = L1_SPA
        self.bridge = bridge
        self.router = router


# Arbitrum addresses from: https://developer.offchainlabs.com/docs/useful_addresses
testnet_L1_addresses = L1DeployAddresses(
    # SPA: https://rinkeby.etherscan.io/address/0x53012655C4eDA87a2cE603e65Cb53c6aF8e5F674#readContract
    "0x7776B097f723eBbc8cd1a17f1fe253D11235cCE1", # SPA
    "0x917dc9a69f65dc3082d518192cd3725e1fa96ca2", # Bridge
    "0x70c143928ecffaf9f5b406f7f4fc28dc43d68380" # Router
    )

mainnet_L1_addresses = L1DeployAddresses(
    # SPA: https://etherscan.io/token/0xb4a3b0faf0ab53df58001804dda5bfc6a3d59008#readContract
    "0xB4A3B0Faf0Ab53df58001804DdA5Bfc6a3D59008", # SPA
    "0xcEe284F754E854890e311e3280b767F80797180d", # Bridge
    "0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef" # Router
    )

class StrategyAddresses:
    def __init__(self, usdc, usdt, weth, crv):
        self.usdc = usdc
        self.usdt = usdt
        self.weth = weth
        self.crv = crv

strategy_addresses = StrategyAddresses(
    '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', #USDC
    '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', #USDT
    '0x82af49447d8a07e3bd95bd0d56f35241523fbab1', #WETH
    '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978' #CRV
)

class StrategyVars:
    def __init__(self, platform_address, vault_proxy_address, reward_token_address, assets, lp_tokens, crv_gauge_address, index, oracle_proxy_address):
        self.platform_address = platform_address
        self.vault_proxy_address = vault_proxy_address
        self.reward_token_address = reward_token_address
        self.assets = assets
        self.lp_tokens = lp_tokens
        self.crv_gauge_address = crv_gauge_address
        self.index = index
        self.oracle_proxy_address = oracle_proxy_address

strategy_vars_base = StrategyVars(
    '0x7f90122BF0700F9E7e1F688fe926940E8839F353', # platform address
    USDs['mainnet']['vault_core_proxy'], # vault address NEED TO INITIALIZE IN SCRIPT
    '0x11cdb42b0eb46d95f990bedd4695a6e3fa034978', # reward token address
    [
            '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
            '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
    ], # assets
    [
            '0x7f90122bf0700f9e7e1f688fe926940e8839f353',
            '0x7f90122bf0700f9e7e1f688fe926940e8839f353'
    ], # LP tokens
    '0xbF7E49483881C76487b0989CD7d9A8239B20CA41', # crv gauge address
    0, # index NEED TO INITIALIZE IN SCRIPT
    "", # oracle address NEED TO INITIALIZE IN SCRIPT
    )
