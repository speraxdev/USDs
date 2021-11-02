const { deployProxy, upgradeProxy, prepareUpgrade } = require('@openzeppelin/truffle-upgrades');

var CompoundStrategy = artifacts.require("../contracts/vault/CompoundStrategy.sol");


let _platformAddress = "0x0000000000000000000000000000000000000000";
let _vaultAddress = "0x0000000000000000000000000000000000000000";
let _rewardTokenAddress = "0x0000000000000000000000000000000000000000";


module.exports = async function(deployer) {
	const compoundStrategy = await deployProxy(CompoundStrategy, [_platformAddress, _vaultAddress, _rewardTokenAddress, [], []], { deployer });
};
