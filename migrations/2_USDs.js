var USDs = artifacts.require("../contracts/token/USDs.sol");
var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");
var Oracle = artifacts.require("../contracts/oracle/Oracle.sol");

module.exports = function(deployer){
    deployer.deploy(USDs).then(function() {
        deployer.deploy(Oracle, "0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0")
        return deployer.deploy(VaultCore, USDs.address, Oracle.address);
     });
}
