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
To upgrade the upgradeable smart contracts: Oracle, TwoPoolStrategy, USDsL2, VaultCoreTools and VaultCore
1. In the upgrade-history folder, make a copy of the existing contract of the highest version number; rename it with increased version number. (i.e. to upgrade Oracle whose highest version number is 4, copy OracleV4.sol to OracleV5.sol)
2. Modify the new .sol file produced by step 1; make the same modification on the original contract .sol file (not in upgrade-history folder). (i.e. modify upgrade-history/OracleV5.sol and oracle/Oracle.sol)
3. Run scripts/upgrade.py to upgrade the deployed contract.
Arbitrum Mainnet Fork:
```
brownie run upgrade --network arbitrum-main-fork
```
Arbitrum Mainnet:
```
brownie run upgrade --network arbitrum-one
```
4. Modify the comments on top of the two modifed .sol files in step 2 to keep record of the upgrade dates, commits, changes and addresses.

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

## External Imports
The following files are imported in order to create a uniswap v3 pool for testing purposes. This uniswap pool is created in conftest.py. See function called: create_uniswap_v3_pool().

These files are not integral to building and deploying USDs.

- contracts/interface/IERC721Permit.sol
- contracts/interface/INonfungiblePositionManager.sol
- contracts/interface/IPeripheryImmutableState.sol
- contracts/interface/IPeripheryPayments.sol
- contracts/interface/IPoolInitializer.sol
- contracts/libraries/PoolAddress.sol
