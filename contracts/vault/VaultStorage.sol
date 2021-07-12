pragma solidity ^0.6.12;

import { USDs } from "../token/USDs.sol";
import { BancorFormula } from "../libraries/BancorFormula.sol";

contract VaultStorage {
	bool public mintRedeemAllowed = true;

	bool public swapfeeInAllowed = true;
	bool public swapfeeOutAllowed = true;

	mapping(address => bool) supportedCollat;
	address[] allCollat;
	address[] allStrategies;

	address public SPATokenAddr = 0xFb931d41A744bE590E8B51e2e343bBE030aC4f93;
	address public oracleAddr;
	address public collaValut;
	address public SPAValut;
	address public USDsFeeValut;
	address public USDsYieldValut;

	uint public chiInit = 95000;
	uint public constant chiPresion = 100000;
	uint public constant chiAlpha = 200;
	uint public constant chiAlpha_Presion = 10000;
	uint public constant chiBeta = 1;
	uint public constant chiGamma = 1;

	uint public constant swapFeePresion = 1000000;
	uint public constant swapFee_P = 995;
	uint public constant swapFee_PPresion = 1000;
	uint public constant swapFeeTheta = 50;

	USDs USDsInstance;
	BancorFormula BancorInstance;

}
