# USDs

## NPM configuration
The Arbitrum packages are currently not on NPM list. they must be installed manually.
create a folder called 'packages' at the root of this project, and copy the Arbitrum packages into the 'packages' folder. Install these packages with the following commands:

npm install arbos-contracts
npm install arb-bridge-eth
npm install arb-bridge-peripherals

## Brownie Framework configuraton
Install the required libraries:

brownie pm install Uniswap/uniswap-v3-core@1.0.0
brownie pm install OpenZeppelin/openzeppelin-contracts-upgradeable@3.4.0
brownie pm install OpenZeppelin/openzeppelin-contracts@3.4.0

### Configure Arbitrum network
Brownie must be configured so it can access the Arbitrum network. 

public testnet guide: https://developer.offchainlabs.com/docs/public_testnet

Network Name: Arbitrum Testnet
RPC URL: https://rinkeby.arbitrum.io/rpc
ChainID: 421611
Symbol: ETH
Block Explorer URL: https://rinkeby-explorer.arbitrum.io/#/

Add Arbitrum testnet configuration to Brownie:
brownie networks add Arbitrum arbitrum-testnet host=https://rinkeby.arbitrum.io/rpc name='Arbitrum Testnet' chainid=421611 explorer=https://rinkeby-explorer.arbitrum.io/#/
