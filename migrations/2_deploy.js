var Oracle = artifacts.require("../contracts/Oracle.sol");
var Spark = artifacts.require("../contracts/Spark.sol");

module.exports = function(deployer){
  deployer.deploy(Oracle, "0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0").then(function() {
    return deployer.deploy(Spark,"0x06Ee09fF6f4c83eaB024173f5507515B0f810DB0", Oracle.address, "0xFb931d41A744bE590E8B51e2e343bBE030aC4f93", "0xcE80b3741Bb3bdecdacc7d6da2a4e77bF6D5c199", 1);
  });
}
