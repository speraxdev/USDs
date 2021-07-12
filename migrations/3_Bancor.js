var BancorFormula = artifacts.require("../contracts/libraries/BancorFormula.sol");


module.exports = async function(deployer) {
    let bancorformula = await deployer.deploy(BancorFormula);
};
