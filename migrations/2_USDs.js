const { deployProxy, upgradeProxy, prepareUpgrade } = require('@openzeppelin/truffle-upgrades');

var USDs = artifacts.require("../contracts/token/USDs.sol");
var Oracle = artifacts.require("../contracts/oracle/Oracle.sol");
var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");


let BancorFormulaAddr = "0x0f27662A7e4033eB4549a4E6Bd42a35a96979BdC";
let SPAandWETHPair = "0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0";


module.exports = async function(deployer) {

	const usds = await deployProxy(USDs, ["USDs", "USDS", "0x0000000000000000000000000000000000000000"], { deployer });
	const oracle = await deployProxy(Oracle, [SPAandWETHPair, usds.address], { deployer });
	const vaultCore = await deployProxy(VaultCore, [usds.address, oracle.address, BancorFormulaAddr], { deployer });
	console.log('USDs deployed', usds.address);
	console.log('Oracle deployed', oracle.address);
	console.log('VaultCore deployed', vaultCore.address);
	//
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