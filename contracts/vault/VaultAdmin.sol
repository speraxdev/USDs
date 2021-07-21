pragma solidity ^0.6.12;

import "./VaultStorage.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract VaultAdmin is VaultStorage, OwnableUpgradeable {
	function pauseMintBurn() external onlyOwner {
		mintRedeemAllowed = false;
	}
	function unpauseMintBurn() external onlyOwner {
		mintRedeemAllowed = true;
	}
}
