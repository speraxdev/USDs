class DeployAddresses:
    def __init__(self, L1_wSPA, L1_USDs, fee_vault):
        self.L1_wSPA = L1_wSPA
        self.L1_USDs = L1_USDs
        self.fee_vault = fee_vault

class UpgradeAddresses:
    def __init__(self, bancor_formula_address, vault_core_tools_proxy, vault_core_proxy, oracle_proxy, USDs_l2_proxy):
        self.bancor_formula_address = bancor_formula_address
        self.vault_core_tools_proxy = vault_core_tools_proxy
        self.vault_core_proxy = vault_core_proxy
        self.oracle_proxy = oracle_proxy
        self.USDs_l2_proxy = USDs_l2_proxy

class ThirdPartyAddresses:
    def __init__(self, l2_gateway, chainlink_eth_price_feed, weth_arbitrum, chainlink_flags):
        self.l2_gateway = l2_gateway
        self.chainlink_eth_price_feed = chainlink_eth_price_feed
        self.weth_arbitrum = weth_arbitrum
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
    "0x24cA7C7aD824D0fD8c0375436a931931239d342D",
    "0x377ff873b648b678608b216467ee94713116c4cd", 
    ## Note: the feeVault can be anything in testnet. here it's 0xdeadbeef... 
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    ) 

## Note: these change after you deploy the contracts, so deploy first and then put those addresses here.
testnet_upgrade_addresses = UpgradeAddresses(
    "0xbc81f60F49cAAD84E3d4557D60c0333835F680e3",
    "0xAe990Cd681C82D9EfB4c12061c2cecB3f7675e83", 
    "0x828B7cA9f1eb2E1e67085Bb51c85f518065CcA57",
    "0x1A6B1de5A5dF710D50A5af781a66a55F14634455",
    "0x111e55F142e0611492D07eE761531841A0e86146"
    )

testnet_third_party_addresses = ThirdPartyAddresses(
    '0x9b014455AcC2Fe90c52803849d0002aeEC184a06',
    '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8',
    '0xb47e6a5f8b33b3f17603c83a0535a9dcd7e32681',
    '0x491B1dDA0A8fa069bbC1125133A975BF4e85a91b'
    )

testnet_collaterals = {
    # USDC
    '0x09b98f8b2395d076514037ff7d39a091a536206c': '0xe020609A0C31f4F96dCBB8DF9882218952dD95c4',
    # WETH
    '0xB47e6A5f8b33b3F17603C83a0535A9dcD7E32681': '0x5f0423B1a6935dc5596e7A24d98532b67A0AeFd8'
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
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef", 
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    )

mainnet_upgrade_address = UpgradeAddresses(
    ## Note: these need to be added. here it's  0xdeadbeef in the meantime... 
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    )

mainnet_third_party_address = ThirdPartyAddresses(
    '0x096760F208390250649E3e8763348E783AEF5562',
    '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612',
    '0x82af49447d8a07e3bd95bd0d56f35241523fbab1',
    '0x3C14e07Edd0dC67442FA96f1Ec6999c57E810a83'
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
    testnet_third_party_addresses,
    mainnet_collaterals
    )

class TokenDetails:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

USDs_token_details = TokenDetails("Sperax USD", "USDs")

wSPAL1_token_details = TokenDetails("Wrapped Sperax", "wSPA")

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
