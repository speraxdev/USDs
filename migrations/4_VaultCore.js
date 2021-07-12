var USDs = artifacts.require("../contracts/token/USDs.sol");
var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");
var Oracle = artifacts.require("../contracts/oracle/Oracle.sol");


module.exports = async function(deployer) {
	deployer.deploy(VaultCore, USDs.address, Oracle.address, "0x0f27662A7e4033eB4549a4E6Bd42a35a96979BdC");
};
