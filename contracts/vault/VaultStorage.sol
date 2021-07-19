pragma solidity ^0.6.12;

import { USDs } from "../token/USDs.sol";
import { BancorFormula } from "../libraries/BancorFormula.sol";

contract VaultStorage {
	bool public mintRedeemAllowed;

	bool public swapfeeInAllowed;
	bool public swapfeeOutAllowed;

	mapping(address => bool) supportedCollat;
	address[] allCollat;
	address[] allStrategies;

	address public SPATokenAddr;
	address public oracleAddr;
	address public collaValut;
	address public SPAValut;
	address public USDsFeeValut;
	address public USDsYieldValut;

	uint public chiInit;
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
