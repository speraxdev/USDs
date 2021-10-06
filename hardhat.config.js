require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-truffle5");
require("@nomiclabs/hardhat-etherscan");
require("@nomiclabs/hardhat-ethers");
require("solidity-coverage");
require("hardhat-deploy");
require("hardhat-gas-reporter");
require("hardhat-contract-sizer");
require("@openzeppelin/hardhat-upgrades");
const {removeConsoleLog} = require("hardhat-preprocessor");
require("dotenv").config();

module.exports = {
  defaultNetwork: "hardhat",
  solidity: {
    compilers: [
      {
        version: "0.6.12",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      }
    ],
  },
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    hardhat: {
      forking: {
        url: `https://eth-kovan.alchemyapi.io/v2/${process.env.ALCHEMY_KOVAN_KEY}`,
      },
      accounts: {
        mnemonic: process.env.MNEMONIC,
      },
      allowUnlimitedContractSize: true,
      hardfork: "london",
      gasPrice: "auto",
    },
    rinkeby: {
      url: `https://rinkeby.infura.io/v3/${process.env.INFURA_KEY}`,
      accounts: {
        mnemonic: process.env.MNEMONIC,
      },
      hardfork: "london",
      gasPrice: "auto",
    },
    mainnet: {
      url: `https://mainnet.infura.io/v3/${process.env.INFURA_KEY}`,
      accounts: {
        mnemonic: process.env.MNEMONIC,
      },
      hardfork: "london",
      gasPrice: "auto",
    },
    matic: {
      url: "https://keen-bell:chaste-gulf-chunk-aloe-deuce-copied@nd-654-291-805.p2pify.com/",
      accounts: {
        mnemonic: process.env.MNEMONIC,
      },
    },
  },
  contractSizer: {
    alphaSort: true,
    runOnCompile: true,
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_APIKEY,
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./build",
  },
  namedAccounts: {
    deployer: {
      default: 0,
    },
  },
  gasReporter: {
    enabled: true,
    coinmarketcap: process.env.COINMARKETCAP,
    currency: "USD",
    gasPrice: 89,
  },
  preprocess: {
    eachLine: removeConsoleLog((hre) => hre.network.name !== "hardhat" && hre.network.name !== "localhost"),
  },
  mocha: {
    timeout: 200000000,
  },
  vyper: {
    version: "0.2.7",
  },
};
