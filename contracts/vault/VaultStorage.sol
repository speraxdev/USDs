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

	uint public startBlockHeight;

	uint public chiInit = 95000;
	uint public constant chiPrec = 100000;
	uint public constant chi_alpha = 5130573085013596;
	uint public constant chi_alpha_Prec = 10**23;
	uint public constant chi_beta = 9;
	uint public constant chi_beta_Prec = 1;
	uint public constant chi_gamma = 1;
	uint public constant chi_gamma_Prec = 1;


	uint public constant swapFeePresion = 1000000;
	uint public constant swapFee_p = 99;
	uint public constant swapFee_p_Prec = 100;
	uint public constant swapFee_theta = 50;
	uint public constant swapFee_theta_Prec = 1;
	uint32 public constant swapFee_a = 12;
	uint32 public constant swapFee_a_Prec = 10;
	uint public constant swapFee_A = 20;
	uint public constant swapFee_A_Prec = 1;


	USDs USDsInstance;
	BancorFormula BancorInstance;

}
