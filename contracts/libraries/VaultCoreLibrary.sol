pragma solidity ^0.6.12;

import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";
import { BancorFormula } from "../libraries/BancorFormula.sol";
import { IBasicToken } from "../interfaces/IBasicToken.sol";
import "../interfaces/IOracle.sol";
import "../vault/VaultCore.sol";
import "../libraries/MyMath.sol";
import "../libraries/StableMath.sol";

library VaultCoreLibrary {
	using SafeERC20Upgradeable for ERC20Upgradeable;
	using SafeMathUpgradeable for uint;
	using MyMath for uint;
	using StableMath for uint;

	// note: chi_alpha_prec = chi_prec
	/**
	 * @dev calculate chiTarget by the formula in section 2.2 of the whitepaper
	 * @param blockPassed the number of blocks that have passed since USDs is launched, i.e. "Block Height"
	 * @param priceUSDs the price of USDs, i.e. "USDs Price"
	 * @param precisionUSDs the precision used in the variable "priceUSDs"
	 * @return chiTarget_ the value of chiTarget
	 */
	function chiTarget(
      uint blockPassed, uint priceUSDs, uint precisionUSDs, address _VaultCoreContract
    ) public view returns (uint chiTarget_) {
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		uint chiAdjustmentA = blockPassed.mul(_vaultContract.chi_prec()).mul(_vaultContract.chi_alpha()).div(_vaultContract.chi_alpha_prec());
		uint chiAdjustmentB;
		uint afterB;
		if (priceUSDs >= precisionUSDs) {
			chiAdjustmentB = _vaultContract.chi_beta().mul(_vaultContract.chi_prec()).mul(priceUSDs - precisionUSDs).mul(priceUSDs - precisionUSDs).div(_vaultContract.chi_beta_prec());
			afterB = _vaultContract.chiInit().add(chiAdjustmentB);
		} else {
			chiAdjustmentB = _vaultContract.chi_beta().mul(_vaultContract.chi_prec()).mul(precisionUSDs - priceUSDs).mul(precisionUSDs - priceUSDs).div(_vaultContract.chi_beta_prec());
			(, afterB) = _vaultContract.chiInit().trySub(chiAdjustmentB);
		}
		(, chiTarget_) = afterB.trySub(chiAdjustmentA);
	}

  function multiplier(uint original, uint price, uint precision) public pure returns (uint) {
    return original.mul(price).div(precision);
  }

	/**
	 * @dev calculate chiMint
	 * @return chiMint, i.e. chiTarget, since they share the same value
	 */
	function chiMint(address _VaultCoreContract) public view returns (uint)  {
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		uint priceUSDs = uint(IOracle(_vaultContract.oracleAddr()).getUSDsPrice());
		uint precisionUSDs = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_prec();
		uint blockPassed = uint(block.number).sub(_vaultContract.startBlockHeight());
		return chiTarget(blockPassed, priceUSDs, precisionUSDs, _VaultCoreContract);
	}


	/**
	 * @dev calculate chiRedeem based on the formula at the end of section 2.2
	 * @return chiRedeem_
	 */
	function chiRedeem(address _VaultCoreContract) public view returns (uint chiRedeem_) {
		// calculate chiTarget
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		uint priceUSDs = uint(IOracle(_vaultContract.oracleAddr()).getUSDsPrice());
		uint precisionUSDs = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_prec();
		uint blockPassed = uint(block.number).sub(_vaultContract.startBlockHeight());
		uint chiTarget_ = chiTarget(blockPassed, priceUSDs, precisionUSDs, _VaultCoreContract);
		// calculate chiRedeem
		uint collateralRatio_ = _vaultContract.collateralRatio();
		if (chiTarget_ > collateralRatio_) {
			chiRedeem_ = chiTarget_.add(_vaultContract.chi_gamma().mul(chiTarget_ - collateralRatio_).div(_vaultContract.chi_gamma_prec()));
		} else {
			chiRedeem_ = chiTarget_;
		}
	}

	// Note: need to be less than (2^32 - 1)
	// Note: assuming when exponentWithPrec >= 2^32, toReturn >= swapFeePresion () (TO-DO: work out the number)
	/**
	 * @dev calculate the OutSwap fee, i.e. fees for redeeming USDs
	 * @return the OutSwap fee
	 */
	function calculateSwapFeeOut(address _VaultCoreContract) public view returns (uint) {
		// if the OutSwap fee is diabled, return 0
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		if (!_vaultContract.swapfeeOutAllowed()) {
			return 0;
		}

		// implement the formula in Section 4.3.2 of whitepaper
		uint USDsInOutRatio = IOracle(_vaultContract.oracleAddr()).USDsInOutRatio();
		uint USDsInOutRatio_prec = IOracle(_vaultContract.oracleAddr()).USDsInOutRatio_prec();
		if (USDsInOutRatio <= uint(12).mul(USDsInOutRatio_prec).div(10)) {
			return _vaultContract.swapFeePresion() / 1000; //0.1%
		} else {
			uint exponentWithPrec = USDsInOutRatio - uint(12).mul(USDsInOutRatio_prec).div(10);
			if (exponentWithPrec >= 2^32) {
				return _vaultContract.swapFeePresion();
			}
			(uint powResWithPrec, uint8 powResPrec) = BancorFormula(_vaultContract.BancorInstance()).power(
        _vaultContract.swapFee_A(), _vaultContract.swapFee_A_prec(), uint32(exponentWithPrec), uint32(USDsInOutRatio_prec)
      );
			uint toReturn = uint(powResWithPrec >> powResPrec).mul(_vaultContract.swapFeePresion()).div(100);
			if (toReturn >= _vaultContract.swapFeePresion()) {
				return _vaultContract.swapFeePresion();
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
	) public view returns (uint SPAMintAmt, uint collaUnlockAmt, uint USDsBurntAmt, uint swapFeeAmount) {
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		uint swapFee = calculateSwapFeeOut(_VaultCoreContract);
    collaUnlockAmt = 0;
    USDsBurntAmt = 0;
    swapFeeAmount = 0;
		SPAMintAmt = multiplier(USDsAmt, (_vaultContract.chi_prec() - chiRedeem(_VaultCoreContract)), _vaultContract.chi_prec());
    SPAMintAmt = multiplier(SPAMintAmt, IOracle(_oracleAddr).getSPAprice_prec(), IOracle(_oracleAddr).getSPAprice());
		if (swapFee > 0) {
			SPAMintAmt = SPAMintAmt.sub(multiplier(SPAMintAmt, swapFee, _vaultContract.swapFeePresion()));
		}

		// //Unlock collaeral
		collaUnlockAmt = multiplier(USDsAmt, chiMint(_VaultCoreContract), _vaultContract.chi_prec());
		collaUnlockAmt = multiplier(collaUnlockAmt, IOracle(_oracleAddr).getCollateralPrice_prec(_collaAddr), IOracle(_oracleAddr).getCollateralPrice(_collaAddr));
		collaUnlockAmt = collaUnlockAmt.div(10**(uint(18).sub(uint(ERC20Upgradeable(_collaAddr).decimals()))));

		if (swapFee > 0) {
			collaUnlockAmt = collaUnlockAmt.sub(multiplier(collaUnlockAmt, swapFee, _vaultContract.swapFeePresion()));
		}

		// //Burn USDs
		swapFeeAmount = multiplier(USDsAmt, swapFee, _vaultContract.swapFeePresion());
		USDsBurntAmt =  USDsAmt.sub(swapFeeAmount);
	}

	/**
	 * @dev calculate the InSwap fee, i.e. fees for minting USDs
	 * @return the InSwap fee
	 */
	function calculateSwapFeeIn(address _VaultCoreContract) public view returns (uint) {
		// if InSwap fee is disabled, return 0
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		if (!_vaultContract.swapfeeInAllowed()) {
			return 0;
		}

		// implement the formula in Section 4.3.1 of whitepaper
		uint priceUSDs_Average = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_average();
		uint precisionUSDs = IOracle(_vaultContract.oracleAddr()).getUSDsPrice_prec();
		uint smallPwithPrecision = _vaultContract.swapFee_p().mul(precisionUSDs).div(_vaultContract.swapFee_p_prec());
    uint swapFeePresion = _vaultContract.swapFeePresion();
		if (smallPwithPrecision < priceUSDs_Average) {
			return swapFeePresion / 1000; // 0.1%
		} else {
			uint temp = (smallPwithPrecision - priceUSDs_Average).mul(_vaultContract.swapFee_theta()).div(_vaultContract.swapFee_theta_prec()); //precision: precisionUSDs
			uint temp2 = temp.mul(temp); //precision: precisionUSDs^2
			uint temp3 = temp2.mul(swapFeePresion).div(precisionUSDs).div(precisionUSDs);
			uint temp4 = temp3.div(100);
			uint temp5 =  swapFeePresion / 1000 + temp4;
			if (temp5 >= swapFeePresion) {
				return swapFeePresion;
			} else {
				return temp5;
			}
		}

	}

	/**
	 * @dev the general mintView function that display all related quantities based on mint types
	 *		valueType = 0: mintWithUSDs
	 *		valueType = 1: mintWithSPA
	 *		valueType = 2: mintWithColla
	 *		valueType = 3: mintWithETH
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
	) public view returns (uint SPABurnAmt, uint collaDeptAmt, uint USDsAmt, uint swapFeeAmount) {
		// obtain the price and pecision of the collateral
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);

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
			swapFeeAmount = USDsAmt.mul(swapFee).div(_vaultContract.swapFeePresion());

		} else if (valueType == 1) { // when mintWithSPA
			// calculate SPABurnAmt
			SPABurnAmt = valueAmt;
			// calculate USDsAmt
			USDsAmt = USDsAmountCalculator(valueType, valueAmt, _VaultCoreContract, collaAddr, swapFee);
			// calculate collaDeptAmt

      collaDeptAmt = collaDeptAmountCalculator(valueType, USDsAmt, _VaultCoreContract, collaAddr, swapFee);
			// calculate swapFeeAmount
			swapFeeAmount = USDsAmt.mul(swapFee).div(_vaultContract.swapFeePresion());

		} else if (valueType == 2 || valueType == 3) { // when mintWithColla or mintWithETH
			// calculate collaDeptAmt
			collaDeptAmt = valueAmt;
			// calculate USDsAmt
			USDsAmt = USDsAmountCalculator(valueType, valueAmt, _VaultCoreContract, collaAddr, swapFee);

			// calculate SPABurnAmt
			SPABurnAmt = SPAAmountCalculator(valueType, USDsAmt, _VaultCoreContract, swapFee);
			// calculate swapFeeAmount
			swapFeeAmount = USDsAmt.mul(swapFee).div(_vaultContract.swapFeePresion());
		}
	}

  function collaDeptAmountCalculator(
    uint valueType, uint USDsAmt, address _VaultCoreContract, address collaAddr, uint swapFee
) internal view returns (uint256 collaDeptAmt) {
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		uint collaAddrDecimal = uint(ERC20Upgradeable(collaAddr).decimals());
    if (valueType == 1) {
      collaDeptAmt = USDsAmt.mul(chiMint(_VaultCoreContract)).mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice_prec(collaAddr)).div(_vaultContract.chi_prec().mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice(collaAddr))).div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				collaDeptAmt = collaDeptAmt.add(collaDeptAmt.mul(swapFee).div(_vaultContract.swapFeePresion()));
			}
    } else if (valueType == 0) {
      collaDeptAmt = USDsAmt.mul(chiMint(_VaultCoreContract)).mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice_prec(collaAddr)).div(_vaultContract.chi_prec().mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice(collaAddr))).div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				collaDeptAmt = collaDeptAmt.add(collaDeptAmt.mul(swapFee).div(_vaultContract.swapFeePresion()));
			}
    }
  }

  function SPAAmountCalculator(
    uint valueType, uint USDsAmt, address _VaultCoreContract, uint swapFee
) internal view returns (uint256 SPABurnAmt) {
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		uint priceSPA = IOracle(_vaultContract.oracleAddr()).getSPAprice();
		uint precisionSPA = IOracle(_vaultContract.oracleAddr()).getSPAprice_prec();
    if (valueType == 2 || valueType == 3) {
      SPABurnAmt = USDsAmt.mul(_vaultContract.chi_prec() - chiMint(_VaultCoreContract)).mul(precisionSPA).div(priceSPA.mul(_vaultContract.chi_prec()));
			if (swapFee > 0) {
				SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(_vaultContract.swapFeePresion()));
			}
    } else if (valueType == 0) {
      SPABurnAmt = USDsAmt.mul(_vaultContract.chi_prec() - chiMint(_VaultCoreContract)).mul(precisionSPA).div(priceSPA.mul(_vaultContract.chi_prec()));
			if (swapFee > 0) {
				SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(_vaultContract.swapFeePresion()));
			}
    }
  }

  function USDsAmountCalculator(
    uint valueType, uint valueAmt, address _VaultCoreContract, address collaAddr, uint swapFee
) internal view returns (uint256 USDsAmt) {
    VaultCore _vaultContract = VaultCore(_VaultCoreContract);
		uint priceSPA = IOracle(_vaultContract.oracleAddr()).getSPAprice();
		uint precisionSPA = IOracle(_vaultContract.oracleAddr()).getSPAprice_prec();
    if (valueType == 2 || valueType == 3) {
      USDsAmt = valueAmt;
			if (swapFee > 0) {
				USDsAmt = USDsAmt.mul(_vaultContract.swapFeePresion()).div(_vaultContract.swapFeePresion().add(swapFee));
			}
      if (valueType == 3) {
        USDsAmt = USDsAmt.mul(10**(uint(18).sub(uint(ERC20Upgradeable(collaAddr).decimals())))).mul(_vaultContract.chi_prec().mul(IOracle(_vaultContract.oracleAddr()).getETHprice())).div(IOracle(_vaultContract.oracleAddr()).getETHprice_prec()).div(chiMint(_VaultCoreContract));
      } else {
        USDsAmt = USDsAmt.mul(10**(uint(18).sub(uint(ERC20Upgradeable(collaAddr).decimals())))).mul(_vaultContract.chi_prec().mul(IOracle(_vaultContract.oracleAddr()).getCollateralPrice(collaAddr))).div(IOracle(_vaultContract.oracleAddr()).getCollateralPrice_prec(collaAddr)).div(chiMint(_VaultCoreContract));
      }
    } else if (valueType == 1) {
      USDsAmt = valueAmt;
			if (swapFee > 0) {
				USDsAmt = USDsAmt.mul(_vaultContract.swapFeePresion()).div(_vaultContract.swapFeePresion().add(swapFee));
			}
			USDsAmt = USDsAmt.mul(_vaultContract.chi_prec()).mul(priceSPA).div(precisionSPA.mul(_vaultContract.chi_prec() - chiMint(_VaultCoreContract)));
    }
  }
}
