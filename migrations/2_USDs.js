var USDs = artifacts.require("../contracts/token/USDs.sol");
var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");
var Oracle = artifacts.require("../contracts/oracle/Oracle.sol");


module.exports = async function(deployer) {
	// deploy MyERC20 and store return value
	let usds = await deployer.deploy(USDs);
    let oracle = await deployer.deploy(Oracle, "0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0", USDs.address);
  	// deploy the Exchange and pass erc20
	deployer.deploy(VaultCore, USDs.address, Oracle.address, "0x0f27662A7e4033eB4549a4E6Bd42a35a96979BdC");
};
