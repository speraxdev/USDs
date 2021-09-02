const { deployProxy, upgradeProxy, prepareUpgrade } = require('@openzeppelin/truffle-upgrades');

var USDs = artifacts.require("../contracts/token/USDs.sol");
var Oracle = artifacts.require("../contracts/oracle/Oracle.sol");
var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");
var VaultCoreLibrary = artifacts.require("../contracts/libraries/VaultCoreLibrary.sol");
var AaveStrategy = artifacts.require("../contracts/strategies/AaveStrategy.sol");

//let BancorFormulaAddr = "0x0f27662A7e4033eB4549a4E6Bd42a35a96979BdC";
//let SPAandWETHPair = "0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0";


module.exports = async function(deployer) {
	await deployer.deploy(VaultCoreLibrary);
	await deployer.link(VaultCoreLibrary, VaultCore);
	const usds = await deployProxy(USDs, ["USDs", "USDS", "0x0000000000000000000000000000000000000000"], { deployer });
	const oracle = await deployProxy(Oracle, [usds.address], { deployer });
	const vaultCore = await deployProxy(VaultCore, [usds.address, oracle.address], { deployer, unsafeAllow: ['external-library-linking'] });
	//const vaultAdmin = await deployProxy(VaultAdmin, [] ,{ deployer });
	// const vaultCore = await deployProxy(VaultCore, ["0xb57aBEb4b8198BB5312E4b4c3e4Cf5b744E19B25", "0x9e74768EE7025b160909D2803adc2A7DE424bA65", BancorFormulaAddr], { deployer });


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
