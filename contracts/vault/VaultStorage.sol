pragma solidity ^0.6.12;

import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import { USDs } from "../token/USDs.sol";
import { BancorFormula } from "../libraries/BancorFormula.sol";

contract VaultStorage is Initializable {
	event AssetSupported(address _asset);
	bool public mintRedeemAllowed;
	bool public capitalAllowed;

	bool public swapfeeInAllowed;
	bool public swapfeeOutAllowed;

	mapping(address => uint256) supportedCollat;
	mapping(address => address) public assetDefaultStrategies;
	address[] allCollat;
	address[] allStrategies;
	uint256 public vaultBuffer;

	address public SPATokenAddr;
	address public oracleAddr;
	address public collaValut;
	address public SPAValut;
	address public USDsFeeValut;
	address public USDsYieldValut;

	uint public startBlockHeight;

	uint public chiInit;
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
