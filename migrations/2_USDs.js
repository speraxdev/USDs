const { deployProxy, upgradeProxy, prepareUpgrade } = require('@openzeppelin/truffle-upgrades');

// var USDsL1 = artifacts.require("../contracts/token/USDsL1.sol");
var USDsL2 = artifacts.require("../contracts/token/USDsL2.sol");

//let BancorFormulaAddr = "0x0f27662A7e4033eB4549a4E6Bd42a35a96979BdC";
//let SPAandWETHPair = "0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0";


module.exports = async function(deployer) {

	// Rinkeby
	// const usdsL1 = await deployProxy(USDsL1, ["USDs", "USDS"], { deployer });

	// Arbitrum
	const usdsL2 = await deployProxy(USDsL2, ["USDs", "USDS", "0x0000000000000000000000000000000000000000"], { deployer });


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
