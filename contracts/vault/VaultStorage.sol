pragma solidity ^0.6.12;

import { USDs } from "../token/USDs.sol";

contract VaultStorage {
	uint256 public constant Q112 = 0x10000000000000000000000000000;

	bool public mintRedeemAllowed = true;

	mapping(address => bool) supportedCollat;
	address[] allCollat;
	address[] allStrategies;

	address public SPATokenAddr = 0xFb931d41A744bE590E8B51e2e343bBE030aC4f93;
	address public oracleAddr = 0x512F1301324c8a64ECEb018089A2BD7D22b89Af7;
	address public collaValut;
	address public SPAValut;
	address public USDsFeeValut;
	address public USDsYieldValut;

	uint public chi = 95000;
	uint public constant chiPresion = 100000;
	uint public constant swapFeePresion = 1000000;

	USDs USDsInstance = USDs(0x18BB68CBCF3D2B70257Df866591499B5DA4F4b29);

}
