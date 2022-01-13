// SPDX-License-Identifier: MIT
pragma solidity >=0.6.12;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "../utils/BancorFormula.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IVaultCore.sol";
import "../libraries/StableMath.sol";
import "../utils/BancorFormula.sol";


/**
 * @title supporting VaultCore of USDs protocol
 * @dev calculation of chi, swap fees associated with USDs's mint and redeem
 * @dev view functions of USDs's mint and redeem
 * @author Sperax Foundation
 */
contract VaultCoreTools is Initializable {
	using SafeERC20Upgradeable for ERC20Upgradeable;
	using SafeMathUpgradeable for uint;
	using StableMath for uint;

	// Testing utilities --------------
	uint public priceUSDs;
	uint public precisionUSDs;
	uint public blockPassed;
	uint public collateralRatio;
	uint public USDsInOutRatio;
	uint public priceUSDs_Average;
	// Get value from system : 

	function setUSDsInOutRatio(uint val) external {
		USDsInOutRatio = val;
	}

	function setBlockPassed(uint val) external {
		blockPassed = val;
	}

	function setPriceUSDs(uint val) external {
		priceUSDs = val;
	}

	function setPrecisionUSDs(uint val)external {
		precisionUSDs = val;
	}

	function setAvgPriceUSDs(uint val) external {
		priceUSDs_Average = val;
	}

	function setCollateralRatio(uint val) external {
		collateralRatio = val;
	}

	function getBlockNum(address _VaultCoreContract) external view returns(uint, uint) {
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		return (block.number, _vaultContract.startBlockHeight());
	}

	function getOriginalValues(address _VaultCoreContract) external {
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		priceUSDs = uint(IOracle(_vaultContract.oracleAddr()).getUSDsPrice());
		precisionUSDs = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_prec();
		priceUSDs_Average = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_average();
		blockPassed = 1000;
		collateralRatio = _vaultContract.collateralRatio();
		USDsInOutRatio = IOracle(_vaultContract.oracleAddr()).USDsInOutRatio();
	}	


	event Debug(string func, string info, uint value);

	// --------------------------------

	BancorFormula public BancorInstance;

	function initialize(address _BancorFormulaAddr) public initializer {
		BancorInstance = BancorFormula(_BancorFormulaAddr);
	}

	/**
	 * @dev calculate chiTarget by the formula in section 2.2 of the whitepaper
	 * @param blockPassed_ the number of blocks that have passed since USDs is launched, i.e. "Block Height"
	 * @param priceUSDs_ the price of USDs, i.e. "USDs Price"
	 * @param precisionUSDs_ the precision used in the variable "priceUSDs"
	 * @return chiTarget_ the value of chiTarget
	 */
	function chiTarget(
			uint blockPassed_, uint priceUSDs_, uint precisionUSDs_, address _VaultCoreContract
		) public /*view*/ returns (uint chiTarget_) {
		string memory func = "chiTarget";
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		uint chiAdjustmentA = blockPassed_.mul(_vaultContract.chi_alpha());
		emit Debug(func, "chiAdjustmentA", chiAdjustmentA);
		uint afterB;
		if (priceUSDs_ >= precisionUSDs_) {
			uint chiAdjustmentB = uint(_vaultContract.chi_beta())
				.mul(uint(_vaultContract.chi_prec()))
				.mul(priceUSDs_ - precisionUSDs_)
				.mul(priceUSDs_ - precisionUSDs_);

			emit Debug(func, "if_chiAdjustmentB_1", chiAdjustmentB);

			chiAdjustmentB = chiAdjustmentB
				.div(_vaultContract.chi_beta_prec())
				.div(precisionUSDs_)
				.div(precisionUSDs_);
			
			emit Debug(func, "if_chiAdjustmentB_2", chiAdjustmentB);

			afterB = _vaultContract.chiInit().add(chiAdjustmentB);
			emit Debug(func, "if_afterB", afterB);

		} else {
			uint chiAdjustmentB = uint(_vaultContract.chi_beta())
				.mul(uint(_vaultContract.chi_prec()))
				.mul(precisionUSDs_ - priceUSDs_)
				.mul(precisionUSDs_ - priceUSDs_);
			
			emit Debug(func, "else_chiAdjustmentB_1", chiAdjustmentB);

			chiAdjustmentB = chiAdjustmentB
				.div(_vaultContract.chi_beta_prec())
				.div(precisionUSDs_)
				.div(precisionUSDs_);
			
			emit Debug(func, "else_chiAdjustmentB_2", chiAdjustmentB);

			(, afterB) = _vaultContract.chiInit().trySub(chiAdjustmentB);

			emit Debug(func, "else_afterB", afterB);
		}
		(, chiTarget_) = afterB.trySub(chiAdjustmentA);

		emit Debug(func, "chiTarget_", chiTarget_);

		if (chiTarget_ > _vaultContract.chi_prec()) {
			chiTarget_ = _vaultContract.chi_prec();
			emit Debug(func, "if_chiTarget_", chiTarget_);
		}
	}

	function multiplier(uint original, uint price, uint precision) public pure returns (uint) {
		return original.mul(price).div(precision);
	}

	/**
	 * @dev calculate chiMint
	 * @return chiMint, i.e. chiTarget, since they share the same value
	 */
	function chiMint(address _VaultCoreContract) public /*view*/ returns (uint)	{
		string memory func = "chiMint";
		// IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		// uint priceUSDs = uint(IOracle(_vaultContract.oracleAddr()).getUSDsPrice());
		// uint precisionUSDs = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_prec();
		// uint blockPassed = uint(block.number).sub(_vaultContract.startBlockHeight());
		uint chiMint_ = chiTarget(blockPassed, priceUSDs, precisionUSDs, _VaultCoreContract);
		emit Debug(func, "chiMint_", chiMint_);
		return chiMint_;
	}


	/**
	 * @dev calculate chiRedeem based on the formula at the end of section 2.2
	 * @return chiRedeem_
	 */
	function chiRedeem(address _VaultCoreContract) public /*view*/ returns (uint chiRedeem_) {
		string memory func = "chiRedeem";
		// calculate chiTarget
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		// uint priceUSDs = uint(IOracle(_vaultContract.oracleAddr()).getUSDsPrice());
		// uint precisionUSDs = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_prec();
		// uint blockPassed = uint(block.number).sub(_vaultContract.startBlockHeight());
		uint chiTarget_ = chiTarget(blockPassed, priceUSDs, precisionUSDs, _VaultCoreContract);
		// calculate chiRedeem
		// uint collateralRatio_ = _vaultContract.collateralRatio();
		if (chiTarget_ > collateralRatio) {
			chiRedeem_ = chiTarget_.sub(uint(_vaultContract.chi_gamma()).mul(chiTarget_ - collateralRatio).div(uint(_vaultContract.chi_gamma_prec())));
			emit Debug(func, "if_chiRedeem_", chiRedeem_);
		} else {
			chiRedeem_ = chiTarget_;
			emit Debug(func, "else_chiRedeem_", chiRedeem_);
		}
	}


	/**
	 * @dev calculate the OutSwap fee, i.e. fees for redeeming USDs
	 * @return the OutSwap fee
	 */
	function calculateSwapFeeOut(address _VaultCoreContract) public /*view*/ returns (uint) {
		string memory func = "calculateSwapFeeOut";
		uint fee = 0;
		// if the OutSwap fee is diabled, return 0
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		if (!_vaultContract.swapfeeOutAllowed()) {
			return 0;
		}
		// implement the formula in Section 4.3.2 of whitepaper
		// uint USDsInOutRatio = IOracle(_vaultContract.oracleAddr()).USDsInOutRatio();
		uint32 USDsInOutRatio_prec = IOracle(_vaultContract.oracleAddr()).USDsInOutRatio_prec();
		if (USDsInOutRatio <= uint(_vaultContract.swapFee_a()).mul(uint(USDsInOutRatio_prec)).div(uint(_vaultContract.swapFee_a_prec()))) {
			fee = uint(_vaultContract.swapFee_prec()) / 1000; //0.1%
			emit Debug(func, "if_fee", fee);
			return fee;
		} else {
			uint exponentWithPrec = USDsInOutRatio - uint(_vaultContract.swapFee_a()).mul(uint(USDsInOutRatio_prec)).div(uint(_vaultContract.swapFee_a_prec()));
			if (exponentWithPrec >= 2^32) {
				fee = uint(_vaultContract.swapFee_prec());
				emit Debug(func, "else_if1_fee", fee);
				return fee;
			}
			emit Debug(func, "else_exponentWithPrec", exponentWithPrec);
			(uint powResWithPrec, uint8 powResPrec) = BancorInstance.power(
				uint(_vaultContract.swapFee_A()), uint(_vaultContract.swapFee_A_prec()), uint32(exponentWithPrec), USDsInOutRatio_prec
			);
			emit Debug(func, "else_powResWithPrec", powResWithPrec);
			emit Debug(func, "else_powResPrec", uint(powResPrec));
			uint toReturn = uint(powResWithPrec.mul(uint(_vaultContract.swapFee_prec())) >> powResPrec) / 100;
			emit Debug(func, "else_toReturn", toReturn);
			if (toReturn >= uint(_vaultContract.swapFee_prec())) {
				fee = uint(_vaultContract.swapFee_prec());
				emit Debug(func, "else_if2_fee", fee);
			} else {
				return toReturn;
			}
		}
	}

	function redeemView(
		address _collaAddr,
		uint USDsAmt,
		address _VaultCoreContract,
		address _oracleAddr
	) public /*view*/ returns (uint SPAMintAmt, uint collaUnlockAmt, uint USDsBurntAmt, uint swapFeeAmount) {
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		uint swapFee = calculateSwapFeeOut(_VaultCoreContract);
		collaUnlockAmt = 0;
		USDsBurntAmt = 0;
		swapFeeAmount = 0;
		SPAMintAmt = multiplier(USDsAmt, (uint(_vaultContract.chi_prec()) - chiRedeem(_VaultCoreContract)), uint(_vaultContract.chi_prec()));
		SPAMintAmt = multiplier(SPAMintAmt, IOracle(_oracleAddr).getSPAprice_prec(), IOracle(_oracleAddr).getSPAprice());
		if (swapFee > 0) {
			SPAMintAmt = SPAMintAmt.sub(multiplier(SPAMintAmt, swapFee, uint(_vaultContract.swapFee_prec())));
		}

		// Unlock collaeral
		collaUnlockAmt = multiplier(USDsAmt, chiRedeem(_VaultCoreContract), uint(_vaultContract.chi_prec()));
		collaUnlockAmt = multiplier(collaUnlockAmt, IOracle(_oracleAddr).getCollateralPrice_prec(_collaAddr), IOracle(_oracleAddr).getCollateralPrice(_collaAddr));
		collaUnlockAmt = collaUnlockAmt.div(10**(uint(18).sub(uint(ERC20Upgradeable(_collaAddr).decimals()))));

		if (swapFee > 0) {
			collaUnlockAmt = collaUnlockAmt.sub(multiplier(collaUnlockAmt, swapFee, uint(_vaultContract.swapFee_prec())));
		}

		// //Burn USDs
		swapFeeAmount = multiplier(USDsAmt, swapFee, uint(_vaultContract.swapFee_prec()));
		USDsBurntAmt = USDsAmt.sub(swapFeeAmount);
	}

	/**
	 * @dev calculate the InSwap fee, i.e. fees for minting USDs
	 * @return the InSwap fee
	 */
	function calculateSwapFeeIn(address _VaultCoreContract) public /*view*/ returns (uint) {
		string memory func = "calculateSwapFeeIn";
		// if InSwap fee is disabled, return 0
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		if (!_vaultContract.swapfeeInAllowed()) {
			return 0;
		}
		uint fee;
		// implement the formula in Section 4.3.1 of whitepaper
		// uint priceUSDs_Average = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_average();
		// uint precisionUSDs = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_prec();
		uint smallPwithPrecision = uint(_vaultContract.swapFee_p()).mul(precisionUSDs).div(_vaultContract.swapFee_p_prec());
		emit Debug(func, "smallPwithPrecision", smallPwithPrecision);
		uint swapFee_prec = uint(_vaultContract.swapFee_prec());
		if (smallPwithPrecision < priceUSDs_Average) {
			fee = swapFee_prec / 1000; // 0.1%
			emit Debug(func, "if_fee", fee);
		} else {
			uint temp = (smallPwithPrecision - priceUSDs_Average).mul(_vaultContract.swapFee_theta()).div(_vaultContract.swapFee_theta_prec()); //precision: precisionUSDs
			uint temp2 = temp.mul(temp); //precision: precisionUSDs^2
			uint temp3 = temp2.mul(swapFee_prec).div(precisionUSDs).div(precisionUSDs);
			uint temp4 = temp3.div(100);
			uint temp5 = swapFee_prec / 1000 + temp4;
			emit Debug(func, "else_temp", temp);
			emit Debug(func, "else_temp2", temp2);
			emit Debug(func, "else_temp3", temp3);
			emit Debug(func, "else_temp4", temp4);
			emit Debug(func, "else_temp5", temp5);
			
			if (temp5 >= swapFee_prec) {
				fee = swapFee_prec;
				emit Debug(func, "else_if_fee", fee);
			} else {
				fee = temp5;
				emit Debug(func, "else_else_fee", fee);
			}
		}
		return fee;
	}

	/**
	 * @dev the general mintView function that display all related quantities based on mint types
	 *		valueType = 0: mintWithUSDs
	 *		valueType = 1: mintWithSPA
	 *		valueType = 2: mintWithColla
	 * @param collaAddr the address of user's chosen collateral
	 * @param valueAmt the amount of user input whose specific meaning depends on valueType
	 * @param valueType the type of user input whose interpretation is listed above in @dev
	 * @return SPABurnAmt the amount of SPA to burn
	 *			collaDeptAmt the amount of collateral to stake
	 *			USDsAmt the amount of USDs to mint
	 *			swapFeeAmount the amount of Inswapfee to pay
	 */
	function mintView(
		address collaAddr,
		uint valueAmt,
		uint8 valueType,
		address _VaultCoreContract
	) public /*view*/ returns (uint SPABurnAmt, uint collaDeptAmt, uint USDsAmt, uint swapFeeAmount) {
		// obtain the price and pecision of the collateral
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);

		// obtain other necessary data
		uint swapFee = calculateSwapFeeIn(_VaultCoreContract);

		if (valueType == 0) { // when mintWithUSDs
			// calculate USDsAmt
			USDsAmt = valueAmt;
			// calculate SPABurnAmt
			SPABurnAmt = SPAAmountCalculator(valueType, USDsAmt, _VaultCoreContract, swapFee);
			// calculate collaDeptAmt
			collaDeptAmt = collaDeptAmountCalculator(valueType, USDsAmt, _VaultCoreContract, collaAddr, swapFee);

			// calculate swapFeeAmount
			swapFeeAmount = USDsAmt.mul(swapFee).div(uint(_vaultContract.swapFee_prec()));

		} else if (valueType == 1) { // when mintWithSPA
			// calculate SPABurnAmt
			SPABurnAmt = valueAmt;
			// calculate USDsAmt
			USDsAmt = USDsAmountCalculator(valueType, valueAmt, _VaultCoreContract, collaAddr, swapFee);
			// calculate collaDeptAmt

			collaDeptAmt = collaDeptAmountCalculator(valueType, USDsAmt, _VaultCoreContract, collaAddr, swapFee);
			// calculate swapFeeAmount
			swapFeeAmount = USDsAmt.mul(swapFee).div(uint(_vaultContract.swapFee_prec()));

		} else if (valueType == 2) { // when mintWithColla
			// calculate collaDeptAmt
			collaDeptAmt = valueAmt;
			// calculate USDsAmt
			USDsAmt = USDsAmountCalculator(valueType, valueAmt, _VaultCoreContract, collaAddr, swapFee);
			// calculate SPABurnAmt
			SPABurnAmt = SPAAmountCalculator(valueType, USDsAmt, _VaultCoreContract, swapFee);
			// calculate swapFeeAmount
			swapFeeAmount = USDsAmt.mul(swapFee).div(uint(_vaultContract.swapFee_prec()));
		}
	}

	function collaDeptAmountCalculator(
		uint valueType, uint USDsAmt, address _VaultCoreContract, address collaAddr, uint swapFee
	) public /*view*/ returns (uint256 collaDeptAmt) {
		require(valueType == 0 || valueType == 1, 'invalid valueType');
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		uint collaAddrDecimal = uint(ERC20Upgradeable(collaAddr).decimals());
		if (valueType == 1) {
			collaDeptAmt = USDsAmt.mul(chiMint(_VaultCoreContract)).mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice_prec(collaAddr)).div(uint(_vaultContract.chi_prec()).mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice(collaAddr))).div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				collaDeptAmt = collaDeptAmt.add(collaDeptAmt.mul(swapFee).div(uint(_vaultContract.swapFee_prec())));
			}
		} else if (valueType == 0) {
			collaDeptAmt = USDsAmt.mul(chiMint(_VaultCoreContract)).mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice_prec(collaAddr)).div(uint(_vaultContract.chi_prec()).mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice(collaAddr))).div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				collaDeptAmt = collaDeptAmt.add(collaDeptAmt.mul(swapFee).div(uint(_vaultContract.swapFee_prec())));
			}
		}
	}

	function SPAAmountCalculator(
		uint valueType, uint USDsAmt, address _VaultCoreContract, uint swapFee
	) public /*view*/ returns (uint256 SPABurnAmt) {
		require(valueType == 0 || valueType == 2, 'invalid valueType');
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		uint priceSPA = IOracle(_vaultContract.oracleAddr()).getSPAprice();
		uint precisionSPA = IOracle(_vaultContract.oracleAddr()).getSPAprice_prec();
		SPABurnAmt = USDsAmt.mul(uint(_vaultContract.chi_prec()) - chiMint(_VaultCoreContract)).mul(precisionSPA).div(priceSPA.mul(uint(_vaultContract.chi_prec())));
		if (swapFee > 0) {
			SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(uint(_vaultContract.swapFee_prec())));
		}
	}

	function USDsAmountCalculator(
		uint valueType, uint valueAmt, address _VaultCoreContract, address collaAddr, uint swapFee
	) public /*view*/ returns (uint256 USDsAmt) {
		require(valueType == 1 || valueType == 2, 'invalid valueType');
		IVaultCore _vaultContract = IVaultCore(_VaultCoreContract);
		uint priceSPA = IOracle(_vaultContract.oracleAddr()).getSPAprice();
		uint precisionSPA = IOracle(_vaultContract.oracleAddr()).getSPAprice_prec();
		if (valueType == 2) {
			USDsAmt = valueAmt;
			if (swapFee > 0) {
				USDsAmt = USDsAmt.mul(uint(_vaultContract.swapFee_prec())).div(uint(_vaultContract.swapFee_prec()).add(swapFee));
			}
			USDsAmt = USDsAmt.mul(10**(uint(18).sub(uint(ERC20Upgradeable(collaAddr).decimals())))).mul(uint(_vaultContract.chi_prec()).mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice(collaAddr))).div(IOracle(_vaultContract.oracleAddr()).getCollateralPrice_prec(collaAddr)).div(chiMint(_VaultCoreContract));
		} else if (valueType == 1) {
			USDsAmt = valueAmt;
			if (swapFee > 0) {
				USDsAmt = USDsAmt.mul(uint(_vaultContract.swapFee_prec())).div(uint(_vaultContract.swapFee_prec()).add(swapFee));
			}
			USDsAmt = USDsAmt.mul(uint(_vaultContract.chi_prec())).mul(priceSPA).div(precisionSPA.mul(uint(_vaultContract.chi_prec()) - chiMint(_VaultCoreContract)));
		}
	}
}
