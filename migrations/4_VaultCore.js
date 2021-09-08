const { deployProxy, upgradeProxy, prepareUpgrade } = require('@openzeppelin/truffle-upgrades');

var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");
var VaultCoreLibrary = artifacts.require("../contracts/libraries/VaultCoreLibrary.sol");


//let BancorFormulaAddr = "0x0f27662A7e4033eB4549a4E6Bd42a35a96979BdC";
//let SPAandWETHPair = "0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0";


module.exports = async function(deployer) {
	await deployer.deploy(VaultCoreLibrary);
	await deployer.link(VaultCoreLibrary, VaultCore);
	const vaultCore = await deployProxy(VaultCore, [], { deployer, unsafeAllow: ['external-library-linking'] });

	//
	// // Upgrade Proxy Contract
	// const usdsExisting = await USDs.deployed();
	// const oracleExisting = await Oracle.deployed();
	// const vaultExisting = await VaultCore.deployed();
	//
	// const upgradedUsds = await upgradeProxy(usdsExisting, USDs, { deployer });
	// const upgradedOracle = await upgradeProxy(oracleExisting, Oracle, { deployer });
	// const upgradedVaultCore = await upgradeProxy(vaultExisting, VaultCore, { deployer });
};
