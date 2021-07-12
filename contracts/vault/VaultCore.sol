//To-do: fix presion

pragma solidity ^0.6.12;
import "./VaultStorage.sol";
import "../libraries/Ownable.sol";
import "../libraries/SafeERC20.sol";
import "../libraries/MyMath.sol";
import "../libraries/Helpers.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/ISperaxToken.sol";

contract VaultCore is VaultStorage, Ownable {
	using SafeERC20 for IERC20;
	using SafeMath for uint;
	using MyMath for uint;

	modifier whenMintRedeemAllowed {
		require(mintRedeemAllowed, "Mint & redeem paused");
		_;
	}

	constructor(address USDsToken_, address oracleAddr_, address BancorFormulaAddr_) public {
		collaValut = address(this);
		SPAValut = address(this);
		USDsFeeValut = address(this);
		USDsYieldValut = address(this);
		supportedCollat[0xb7a4F3E9097C08dA09517b5aB877F7a917224ede] = true;
		USDsInstance = USDs(USDsToken_);
		oracleAddr = oracleAddr_;
		BancorInstance = BancorFormula(BancorFormulaAddr_);
	}


	/**
	 * @dev swapFeePresion = 1000000
	 */

	function calculateSwapFeeIn() public view returns (uint) {
		if (!swapfeeInAllowed) {
			return 0;
		}

		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice()); //TODO: change to 3 days average
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint smallPwithPrecision = swapFee_P.mul(precisionUSDs).div(swapFee_PPresion);
		if (smallPwithPrecision < priceUSDs) {
			return swapFeePresion / 1000; // 0.1%
		} else {
			uint temp = (smallPwithPrecision - priceUSDs).mul(swapFeeTheta); //precision: precisionUSDs
			uint temp2 = temp.mul(temp); //precision: precisionUSDs^2
			uint temp3 = temp2.mul(swapFeePresion).div(precisionUSDs).div(precisionUSDs);
			uint temp4 = temp3.div(100);
			return swapFeePresion / 1000 + temp4;
		}

	}

	function calculateSwapFeeOut() public view returns (uint) {
		if (!swapfeeOutAllowed) {
			return 0;
		}
		uint USDsInOutRatio = IOracle(oracleAddr).USDsInOutRatio();
		uint USDsInOutRatioPrecision = IOracle(oracleAddr).USDsInOutRatioPrecision();
		if (USDsInOutRatio <= uint(12).mul(USDsInOutRatioPrecision).div(10)) {
			return 1000; //0.1%
		} else {

			(uint powResWithPrec, uint8 powResPrec) = BancorInstance.power(uint(20), uint(1), uint32(12),uint32(10));
			return uint(powResWithPrec >> powResPrec).mul(10**4);
		}
	}

	function chiTarget(uint chiInit_, uint blockHeight, uint priceUSDs, uint precisionUSDs) public view returns (uint chiTarget_) {
		uint chiAdjustmentA = blockHeight.mul(chiAlpha).div(chiAlpha_Presion);
		uint chiAdjustmentB;
		if (priceUSDs > precisionUSDs) {
			chiAdjustmentB = chiBeta.mul(priceUSDs - precisionUSDs).mul(priceUSDs - precisionUSDs);
			chiTarget_ = chiInit_.sub(chiAdjustmentA).add(chiAdjustmentB);
		} else if (priceUSDs < precisionUSDs) {
			chiAdjustmentB = chiBeta.mul(precisionUSDs - priceUSDs).mul(precisionUSDs - priceUSDs);
			chiTarget_ = chiInit_.sub(chiAdjustmentA).sub(chiAdjustmentB);
		} else {
			chiTarget_ = chiInit_.sub(chiAdjustmentA);
		}
	}

	function chiMint() public view returns (uint)  {
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		return chiTarget(chiInit, block.number, priceUSDs, precisionUSDs);
	}

	function chiRedeem() public view returns (uint chiRedeem_) {
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint chiTarget_ = chiTarget(chiInit, block.number, priceUSDs, precisionUSDs);
		uint collateralRatio_ = collateralRatio();
		if (chiTarget_ > collateralRatio_) {
			chiRedeem_ = chiTarget_.add(chiGamma.mul(chiTarget_ - collateralRatio_));
		} else {
			chiRedeem_ = chiTarget_;
		}

	}

	function mint(address collaAddr, uint USDsAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr], "Collateral not supported");
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, USDsAmt, 0);
	}

	function mintWithSPA(address collaAddr, uint SPAAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr], "Collateral not supported");
		require(SPAAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, SPAAmt, 1);
	}

	function mintWithColla(address collaAddr, uint CollaAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr], "Collateral not supported");
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, CollaAmt, 2);
	}

	function _mint(
		address collaAddr,
		uint valueAmt,
		uint8 valueType
	) internal {
		uint priceColla = uint(IOracle(oracleAddr).collatPrice(collaAddr));
		uint precisionColla = IOracle(oracleAddr).collatPricePrecision(collaAddr);
		uint priceSPA = uint(IOracle(oracleAddr).getSPAPrice());
		uint precisionSPA = IOracle(oracleAddr).SPAPricePrecision();
		uint swapFee = calculateSwapFeeIn();
		uint chi = chiMint();
		uint SPABurnAmt;
		uint CollaDepAmt;
		uint USDsAmt;
		uint swapFeeAmount;
		uint CollaDepAmtDiv = chiPresion.mul(priceColla);

		if (valueType == 0) {
			USDsAmt = valueAmt;

			SPABurnAmt = USDsAmt.mul(chi).div(chiPresion).mul(precisionSPA).div(priceSPA);
			if (swapFee > 0) {
				SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(swapFeePresion));
			}

			//Deposit collaeral
			CollaDepAmt = USDsAmt.mul(chiPresion - chi).mul(precisionColla).div(CollaDepAmtDiv);
			if (swapFee > 0) {
				CollaDepAmt = CollaDepAmt.add(CollaDepAmt.mul(swapFee).div(swapFeePresion));
			}

			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		} else if (valueType == 1) {
			SPABurnAmt = valueAmt;

			USDsAmt = SPABurnAmt;
			if (swapFee > 0) {
				USDsAmt = USDsAmt.div(1 + swapFee.div(swapFeePresion));
			}
			USDsAmt = USDsAmt.mul(chiPresion).div(chi).mul(priceSPA).div(precisionSPA);

			//Deposit collaeral
			CollaDepAmt = USDsAmt.mul(chiPresion - chi).mul(precisionColla).div(CollaDepAmtDiv);
			if (swapFee > 0) {
				CollaDepAmt = CollaDepAmt.add(CollaDepAmt.mul(swapFee).div(swapFeePresion));
			}

			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		} else if (valueType == 2) {
			CollaDepAmt = valueAmt;

			USDsAmt = CollaDepAmt.mul(CollaDepAmtDiv).div(precisionColla).div(chiPresion - chi);

			SPABurnAmt = USDsAmt.mul(chi).div(chiPresion).mul(precisionSPA).div(priceSPA);
			if (swapFee > 0) {
				SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(swapFeePresion));
			}

			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		}
		ISperaxToken(SPATokenAddr).burnFrom(msg.sender, SPABurnAmt);

		IERC20 collaAddrERC20 = IERC20(collaAddr);
		collaAddrERC20.safeTransferFrom(msg.sender, collaValut, CollaDepAmt);

		//Mint USDs
		USDsInstance.mint(msg.sender, USDsAmt);
		USDsInstance.mint(USDsFeeValut, swapFeeAmount);
	}

	function redeem(address collaAddr, uint USDsAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr], "Collateral not supported");
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_redeem(collaAddr, USDsAmt);
	}


	function _redeem(
		address collaAddr,
		uint USDsAmt
	) internal whenMintRedeemAllowed {
		uint priceColla = uint(IOracle(oracleAddr).collatPrice(collaAddr));
		uint precisionColla = IOracle(oracleAddr).collatPricePrecision(collaAddr);
		uint priceSPA = uint(IOracle(oracleAddr).getSPAPrice());
		uint precisionSPA = IOracle(oracleAddr).SPAPricePrecision();
		uint swapFee = calculateSwapFeeOut();
		uint chi = chiRedeem();
		uint SPAMintAmt = USDsAmt.mul(chi).div(chiPresion).mul(precisionSPA).div(priceSPA);
		if (swapFee > 0) {
			SPAMintAmt = SPAMintAmt.sub(SPAMintAmt.mul(swapFee).div(swapFeePresion));
		}
		IERC20(collaAddr).safeTransferFrom(SPAValut, msg.sender, SPAMintAmt);

		//Unlock collaeral
		uint CollaUnlockAmtDiv = chiPresion.mul(priceColla);
		uint CollaUnlockAmt = USDsAmt.mul(chiPresion - chi).mul(precisionColla).div(CollaUnlockAmtDiv);
		if (swapFee > 0) {
			CollaUnlockAmt = CollaUnlockAmt.sub(CollaUnlockAmt.mul(swapFee).div(swapFeePresion));
		}
		IERC20(collaAddr).safeTransferFrom(collaValut, msg.sender, CollaUnlockAmt);

		//Burn USDs
		uint swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		USDsInstance.burn(msg.sender, USDsAmt.sub(swapFeeAmount));
		USDsInstance.transfer(USDsFeeValut, swapFeeAmount);
	}

	/**
	 * @dev Calculate the total value of assets held by the Vault and all
	 *      strategies and update the supply of USDs.
	 */
	function rebase() public {
		_rebase();
	}

	/**
	 * @dev Calculate the total value of assets held by the Vault and all
	 *      strategies and update the supply of USDs, optionaly sending a
	 *      portion of the yield to the trustee.
	 */
	function _rebase() internal {
		uint256 totalSupply = USDsInstance.totalSupply();
		uint256 vaultValue = _totalValue();

		if (vaultValue > totalSupply && totalSupply != 0) {
			USDsInstance.changeSupply(vaultValue);
		}
	}

	/**
	 * @dev  Precision: same as chi
	 */

	function collateralRatio() public view returns (uint256 ratio) {
        uint totalValue = _totalValue();
		uint USDsSupply =  USDsInstance.totalSupply();
		ratio = totalValue.mul(chiPresion).div(USDsSupply);
    }

	/**
     * @dev Determine the total value of assets held by the vault and its
     *         strategies.
     * @return value Total value in USD (1e18)
     */
    function totalValue() external view returns (uint256 value) {
        value = _totalValue();
    }

    /**
     * @dev Internal Calculate the total value of the assets held by the
     *         vault and its strategies.
     * @return value Total value in USD (1e18)
     */
    function _totalValue() internal view returns (uint256 value) {
        return _totalValueInVault().add(_totalValueInStrategies());
    }

    /**
     * @dev Internal to calculate total value of all assets held in Vault.
     * @return value in ETH (1e18)
     */
    function _totalValueInVault() internal view returns (uint256 value) {
        // for (uint256 y = 0; y < allCollat.length; y++) {
        //     IERC20 asset = IERC20(allCollat[y]);
        //     uint256 assetDecimals = Helpers.getDecimals(allCollat[y]);
        //     uint256 balance = asset.balanceOf(address(this));
        //     if (balance > 0) {
        //         value = value.add(balance.scaleBy(int8(18 - assetDecimals)));
        //     }
        // }
    }

    /**
     * @dev Internal to calculate total value of all assets held in Strategies.
     * @return value in ETH (1e18)
     */
    function _totalValueInStrategies() internal view returns (uint256 value) {
        for (uint256 i = 0; i < allStrategies.length; i++) {
            value = value.add(_totalValueInStrategy(allStrategies[i]));
        }
    }

    /**
     * @dev Internal to calculate total value of all assets held by strategy.
     * @param _strategyAddr Address of the strategy
     * @return value in ETH (1e18)
     */
    function _totalValueInStrategy(address _strategyAddr)
        internal
        view
        returns (uint256 value)
    {
        value = 0;
    }

	/**
     * @notice Get the balance of an asset held in Vault and all strategies.
     * @param _asset Address of asset
     * @return uint256 Balance of asset in decimals of asset
     */
    function checkBalance(address _asset) external view returns (uint256) {
        return _checkBalance(_asset);
    }

    /**
     * @notice Get the balance of an asset held in Vault and all strategies.
     * @param _asset Address of asset
     * @return balance Balance of asset in decimals of asset
     */
    function _checkBalance(address _asset)
        internal
        view
        returns (uint256 balance)
    {
        IERC20 asset = IERC20(_asset);
        balance = asset.balanceOf(address(this));
        // for (uint256 i = 0; i < allStrategies.length; i++) {
        //     IStrategy strategy = IStrategy(allStrategies[i]);
        //     if (strategy.supportsAsset(_asset)) {
        //         balance = balance.add(strategy.checkBalance(_asset));
        //     }
        // }
    }

    //
    // Owner Only Function: change swap fee allowance
    //

    function toggleSwapfeeInAllowed(bool newAllowance) external onlyOwner {
      swapfeeInAllowed = newAllowance;
    }

    function toggleSwapfeeOutAllowed(bool newAllowance) external onlyOwner {
      swapfeeOutAllowed = newAllowance;
    }
}
