const { deployProxy, upgradeProxy, prepareUpgrade } = require('@openzeppelin/truffle-upgrades');

var USDs = artifacts.require("../contracts/token/USDs.sol");
var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");
var Oracle = artifacts.require("../contracts/oracle/Oracle.sol");


module.exports = async function(deployer) {
	// deploy MyERC20 and store return value
	// const usds = await deployProxy(USDs, ["USDs", "USDS", "0xe8A06462628b49eb70DBF114EA510EB3BbBDf559"], { deployer });
	// const oracle = await deployProxy(Oracle, ["0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0", usds.address], { deployer });
	// const vaultCore = await deployProxy(VaultCore, ["0xc9490D581FF50a17ABC8FAA8e98E74D9E279Fb2c", "0x707ABED42BF51Daa8E54CBaB2e4483bc1de0Ee6A", "0x0f27662A7e4033eB4549a4E6Bd42a35a96979BdC"], { deployer });

	// Upgrade Proxy Contract
	// const upgradedUsds = await upgradeProxy("0xc9490D581FF50a17ABC8FAA8e98E74D9E279Fb2c", USDs, { deployer });
	// const upgradedUsds = await upgradeProxy(usds.address, USDs, { deployer });
	// const upgradedOracle = await upgradeProxy("0x707ABED42BF51Daa8E54CBaB2e4483bc1de0Ee6A", Oracle, { deployer });
	// const upgradedVaultCore = await upgradeProxy("0xEBfCd7f7F424f5A72939aAed18939c90733b6379", VaultCore, { deployer });
};
