var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");

module.exports = function(deployer){
  deployer.deploy(VaultCore);
}
