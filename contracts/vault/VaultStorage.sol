pragma solidity ^0.6.12;

import { USDs } from "../token/USDs.sol";

contract VaultStorage {
	uint256 public constant Q112 = 0x10000000000000000000000000000;

	bool public mintRedeemAllowed = false;

	mapping(address => bool) supportedCollat;
	address[] allCollat;
	address[] allStrategies;

	address public SPATokenAddr;
	address public oracleAddr;
	address public collaValut;
	address public SPAValut;
	address public USDsFeeValut;
	address public USDsYieldValut;

	uint public chi = 95000;
	uint public constant chiPresion = 100000;
	uint public constant swapFeePresion = 1000000;

	USDs USDsInstance;

}
