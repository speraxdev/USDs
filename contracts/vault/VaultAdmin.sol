pragma solidity ^0.6.12;

import "./VaultStorage.sol";
import "../libraries/Ownable.sol";

contract VaultAdmin is VaultStorage, Ownable {
	function pauseMintBurn() external onlyOwner {
		mintRedeemAllowed = false;
	}
	function unpauseMintBurn() external onlyOwner {
		mintRedeemAllowed = true;
	}
}
