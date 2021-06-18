var USDs = artifacts.require("../contracts/token/USDs.sol");

module.exports = function(deployer){
  deployer.deploy(USDs);
}
