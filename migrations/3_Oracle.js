var Oracle = artifacts.require("../contracts/oracle/Oracle.sol");

module.exports = function(deployer){
  deployer.deploy(Oracle, "0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0")
}
