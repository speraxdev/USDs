class DeployAddresses:
    def __init__(self, L1_wSPA, L1_USDs, fee_vault):
        self.L1_wSPA = L1_wSPA
        self.L1_USDs = L1_USDs
        self.fee_vault = fee_vault

class UpgradeAddresses:
    def __init__(self, vault_core_proxy, oracle_proxy, USDs_l2_proxy):
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
    "0x53012655C4eDA87a2cE603e65Cb53c6aF8e5F674",
    "0x377ff873b648b678608b216467ee94713116c4cd", 
    "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    ) 

## Note: these change after you deploy the contracts, so deploy first and then put those addresses here.
testnet_upgrade_addresses = UpgradeAddresses(
    "0xa3E29E7A7E1A712783d53e3f2b45F22f09bc7d2A",
    "0x684c186c6Cd227dF3288D0A422B22Ae6BE8324FC",
    "0x716Cb4d17245eA6d99014b56b566F46878f12106"
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
    "0xgibberish",
    "0xgibberish", 
    "0xgibberish"
    )

mainnet_upgrade_address = UpgradeAddresses(
    "0xgibberish",
    "0xgibberish",
    "0xgibberish"
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
    mainnet_deploy_address, 
    mainnet_collaterals
    )

class TokenDetails:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

USDs_token_details = TokenDetails("Sperax USD", "USDs")
    
