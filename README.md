# USDs

## Deploy 
To deploy and configure the smart contracts, run the script/deploy.py script:

Testnet (Arbitrum rinkeby):
```
brownie run deploy --network arbitrum-rinkeby
```

Testnet (Ethereum rinkeby):
```
brownie run deploy --network rinkeby
```
## Upgrade
To upgrade the two upgradeable smart contracts, Vault and Oracle, run the script/upgrade.py script:

Testnet:
```
brownie run upgrade --network arbitrum-rinkeby
```

## Testing
To run the tests, execute the following command:

```
brownie test -I -s
```

To test only the upgrade path for VaultCore -> VaultCoreV2, run the following:

```
brownie test tests/test_upgrade_vault.py -I -s
```

To test only the upgrade path for Oracle -> OracleV2, run the following:

```
brownie test tests/test_upgrade_oracle.py -I -s
```

## Configure Arbitrum Gateway

L1 Rinkeby: https://rinkeby.etherscan.io/address/0x53012655C4eDA87a2cE603e65Cb53c6aF8e5F674#writeContract

Select Contract -> Write Contract -> Connect to Web3
select API 10 registerTokenOnL2()

```
SPA L2 address: 0x59d51ef2cbB1Ae4de94D362045f013B3cAFe5563
maxSubmissionsCost*: 
maxGas: 0
gasPriceBid: 0
creditBackAddress: 0xe0C97480CA7BDb33B2CD9810cC7f103188de4383 (address of minter on rinkeby)
```

## NPM configuration
The Arbitrum packages are currently not on NPM list. they must be installed manually.
create a folder called 'packages' at the root of this project, and copy the Arbitrum packages into the 'packages' folder. Install these packages with the following commands:

```
npm install arbos-contracts
npm install arb-bridge-eth
npm install arb-bridge-peripherals
```

## Brownie Framework configuraton
Install the required libraries:

```
brownie pm install Uniswap/uniswap-v3-core@1.0.0
brownie pm install OpenZeppelin/openzeppelin-contracts-upgradeable@3.4.0
brownie pm install OpenZeppelin/openzeppelin-contracts@3.4.0
```

### Configure Arbitrum network
Brownie must be configured so it can access the Arbitrum network. 

public testnet guide: https://developer.offchainlabs.com/docs/public_testnet

```
Network Name: Arbitrum Testnet
RPC URL: https://rinkeby.arbitrum.io/rpc
ChainID: 421611
Symbol: ETH
Block Explorer URL: https://rinkeby-explorer.arbitrum.io/#/
```

Add Arbitrum testnet configuration to Brownie:
```
brownie networks add Arbitrum arbitrum-rinkeby host=https://rinkeby.arbitrum.io/rpc name='Arbitrum Testnet' chainid=421611 explorer=https://rinkeby-explorer.arbitrum.io/#/
```
