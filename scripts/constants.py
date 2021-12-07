class DeployAddresses:
    def __init__(self, L1wSPA, L1USDs):
        self.L1wSPA = L1wSPA
        self.L1USDs = L1USDs

class UpgradeAddresses:
    def __init__(self, VaultCoreProxy, OracleProxy, USDsL2Proxy):
        self.VaultCoreProxy = VaultCoreProxy
        self.OracleProxy = OracleProxy
        self.USDsL2Proxy = USDsL2Proxy

class Addresses:
    def __init__(self, deploy, upgrade):
        self.deploy = deploy
        self.upgrade = upgrade

# testnet

testnet_deploy_addresses = DeployAddresses("0x53012655C4eDA87a2cE603e65Cb53c6aF8e5F674",
"0x377ff873b648b678608b216467ee94713116c4cd")

testnet_upgrade_addresses = UpgradeAddresses("0x6939b8879E3895F7166b4d8A4AAdD9EE84c477b4",
"0x9a3510CA042F403256d51399f8133AF72d5aD24d",
"0xa09AA8d760A1fB88E4dd738e8d4128B520B77449")

testnetAddresses = Addresses(testnet_deploy_addresses, testnet_upgrade_addresses)

# mainnet

## TODO: Add mainnet addresses
## the deploy addresses are needed first
## then when deployed, you can put the proxy addresses here for upgrades

mainnet_deploy_address = DeployAddresses("0xgibberish",
"0xgibberish")

mainnet_upgrade_address = UpgradeAddresses("0xgibberish",
"0xgibberish",
"0xgibberish")

mainnetAddresses = Addresses(mainnet_deploy_address, mainnet_upgrade_address)

class TokenDetails:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

USDs_token_details = TokenDetails("Sperax USD", "USDs")
    

