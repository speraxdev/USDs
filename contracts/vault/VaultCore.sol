//To-do: fix presion

pragma solidity ^0.6.12;

import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/AddressUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";

import "./VaultStorage.sol";
import "../libraries/MyMath.sol";
import "../libraries/Helpers.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/ISperaxToken.sol";

contract VaultCore is Initializable, VaultStorage, OwnableUpgradeable {
	using SafeERC20Upgradeable for ERC20Upgradeable;
	using SafeMathUpgradeable for uint;
	using MyMath for uint;

	event USDSMinted(
		address indexed wallet,
		uint256 indexed USDsAmt,
		uint256 indexed SPAsAmt,
		uint256 feeAmt
	);

	event USDSRedeemed(
		address indexed wallet,
		uint256 indexed USDsAmt,
		uint256 indexed SPAsAmt,
		uint256 feeAmt
	);

	event TotalSupplyChanged(
		uint256 indexed oldSupply,
		uint256 indexed newSupply
	);

	event SwapFeeInAllowed(
		bool indexed allowance,
		uint256 time
	);

	event SwapFeeOutAllowed(
		bool indexed allowance,
		uint256 time
	);

	event CollateralUpdated(
		address indexed token,
		bool indexed allowance
	);

	modifier whenMintRedeemAllowed {
		require(mintRedeemAllowed, "Mint & redeem paused");
		_;
	}

	function initialize(address USDsToken_, address oracleAddr_, address BancorFormulaAddr_) public initializer {
		OwnableUpgradeable.__Ownable_init();
		// Initialize variables
		mintRedeemAllowed = true;
		swapfeeInAllowed = true;
		swapfeeOutAllowed = true;
		SPATokenAddr = 0x2B607b664A1012aD658b430E03603be1DC83EeCc;
		chiInit = 95000;

		collaValut = address(this);
		SPAValut = address(this);
		USDsFeeValut = address(this);
		USDsYieldValut = address(this);
		supportedCollat[0xb7a4F3E9097C08dA09517b5aB877F7a917224ede] = 1;
		allCollat.push(0xb7a4F3E9097C08dA09517b5aB877F7a917224ede);
		USDsInstance = USDs(USDsToken_);
		oracleAddr = oracleAddr_;
		BancorInstance = BancorFormula(BancorFormulaAddr_);
		startBlockHeight = block.number;
		// DAI
		// 0x4f96fe3b7a6cf9725f59d353f723c1bdb64ca6aa
		// 0x777A68032a88E5A84678A77Af2CD65A7b3c0775a
		// 8
		// USDC
		// 0xb7a4F3E9097C08dA09517b5aB877F7a917224ede
		// 0x9211c6b3BF41A10F78539810Cf5c64e1BB78Ec60
		// 8
		// USDT
		// 0x07de306ff27a2b630b1141956844eb1552b956b5
		// 0x2ca5A90D34cA333661083F89D831f757A9A50148
		// 8
	}


	function calculateSwapFeeIn() public returns (uint) {
		if (!swapfeeInAllowed) {
			return 0;
		}

		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice()); //TODO: change to 3 days average
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint smallPwithPrecision = swapFee_p.mul(precisionUSDs).div(swapFee_p_Prec);
		if (smallPwithPrecision < priceUSDs) {
			return swapFeePresion / 1000; // 0.1%
		} else {
			uint temp = (smallPwithPrecision - priceUSDs).mul(swapFee_theta).div(swapFee_theta_Prec); //precision: precisionUSDs
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

			(uint powResWithPrec, uint8 powResPrec) = BancorInstance.power(uint(swapFee_A), uint(swapFee_A_Prec), swapFee_a, swapFee_a_Prec);
			return uint(powResWithPrec >> powResPrec).mul(10**4);
		}
	}

	function chiTarget(uint chiInit_, uint blockPassed, uint priceUSDs, uint precisionUSDs) public view returns (uint chiTarget_) {
		uint chiAdjustmentA = blockPassed.mul(chi_alpha).div(chi_alpha_Prec);
		uint chiAdjustmentB;
		if (priceUSDs > precisionUSDs) {
			chiAdjustmentB = chi_beta.mul(priceUSDs - precisionUSDs).mul(priceUSDs - precisionUSDs).div(chi_beta_Prec);
			chiTarget_ = chiInit_.sub(chiAdjustmentA).add(chiAdjustmentB);
		} else if (priceUSDs < precisionUSDs) {
			chiAdjustmentB = chi_beta.mul(precisionUSDs - priceUSDs).mul(precisionUSDs - priceUSDs).div(chi_beta_Prec);
			chiTarget_ = chiInit_.sub(chiAdjustmentA).sub(chiAdjustmentB);
		} else {
			chiTarget_ = chiInit_.sub(chiAdjustmentA);
		}
	}

	function chiMint() public returns (uint)  {
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint blockPassed = uint(block.number).sub(startBlockHeight);
		return chiTarget(chiInit, blockPassed, priceUSDs, precisionUSDs);
	}

	function chiRedeem() public returns (uint chiRedeem_) {
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint blockPassed = uint(block.number).sub(startBlockHeight);
		uint chiTarget_ = chiTarget(chiInit, blockPassed, priceUSDs, precisionUSDs);
		//uint collateralRatio_ = collateralRatio();
		uint collateralRatio_ = chiTarget_;
		if (chiTarget_ > collateralRatio_) {
			chiRedeem_ = chiTarget_.add(chi_gamma.mul(chiTarget_ - collateralRatio_).div(chi_gamma_Prec));
		} else {
			chiRedeem_ = chiTarget_;
		}

	}

	function mintWithUSDs(address collaAddr, uint USDsMintAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(USDsMintAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, USDsMintAmt, 0);
	}

	function mintWithSPA(address collaAddr, uint SPAAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(SPAAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, SPAAmt, 1);
	}

	function mintWithColla(address collaAddr, uint CollaAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, CollaAmt, 2);
	}

	function mintWithEth() public payable whenMintRedeemAllowed {
    require(msg.value > 0, "Need to pay Ether");
		_mint(address(0), msg.value, 3);
	}

	//View functions

	function mintWithUSDsView(address collaAddr, uint USDsMintAmt)
		public returns (uint SPABurnAmt, uint CollaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(USDsMintAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, CollaDepAmt, USDsAmt, swapFeeAmount) = mintView(collaAddr, USDsMintAmt, 0);
	}

	function mintWithSPAView(address collaAddr, uint SPAAmt)
		public returns (uint SPABurnAmt, uint CollaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(SPAAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, CollaDepAmt, USDsAmt, swapFeeAmount)  = mintView(collaAddr, SPAAmt, 1);
	}

	function mintWithCollaView(address collaAddr, uint CollaAmt)
		public returns (uint SPABurnAmt, uint CollaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, CollaDepAmt, USDsAmt, swapFeeAmount) = mintView(collaAddr, CollaAmt, 2);
	}

	// SPABurnAmt precision: 10^18
	// CollaDepAmt precision: 10^collaAddrDecimal
	// USDsAmt precision: 10^18
	// swapFeeAmount precision: swapFeePresion
	function mintWithEthView(uint CollaAmt)
		public returns (uint SPABurnAmt, uint CollaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, CollaDepAmt, USDsAmt, swapFeeAmount) = mintView(address(0), CollaAmt, 2);
	}

	function mintView(
		address collaAddr,
		uint valueAmt,
		uint8 valueType
	) public returns (uint SPABurnAmt, uint CollaDepAmt, uint USDsAmt, uint swapFeeAmount) {
		uint priceColla = 0;
		uint precisionColla = 0;
		if (valueType == 3) {
			priceColla = IOracle(oracleAddr).getETHPrice();
			precisionColla = IOracle(oracleAddr).ETHPricePrecision();
		} else {
			priceColla = IOracle(oracleAddr).collatPrice(collaAddr);
			precisionColla = IOracle(oracleAddr).collatPricePrecision(collaAddr);
		}
		uint priceSPA = IOracle(oracleAddr).getSPAPrice();
		uint precisionSPA = IOracle(oracleAddr).SPAPricePrecision();
		uint swapFee = calculateSwapFeeIn();
		uint collaAddrDecimal = uint(ERC20Upgradeable(collaAddr).decimals());


		if (valueType == 0) {
			USDsAmt = valueAmt;
			SPABurnAmt = USDsAmt.mul(chiPrec - chiMint()).mul(precisionSPA).div(priceSPA.mul(chiPrec));
			if (swapFee > 0) {
				SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(swapFeePresion));
			}

			//Deposit collaeral
			uint CollaDepAmt_18 = USDsAmt.mul(chiMint()).mul(precisionColla).div(chiPrec.mul(priceColla));
			CollaDepAmt = CollaDepAmt_18.div(10**(uint(18).sub(collaAddrDecimal)));
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
			USDsAmt = USDsAmt.mul(chiPrec).mul(priceSPA).div(precisionSPA.mul(chiPrec - chiMint()));

			//Deposit collaeral
			uint CollaDepAmt_18 = USDsAmt.mul(chiMint()).mul(precisionColla).div(chiPrec.mul(priceColla));
			CollaDepAmt = CollaDepAmt_18.div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				CollaDepAmt = CollaDepAmt.add(CollaDepAmt.mul(swapFee).div(swapFeePresion));
			}

			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		} else if (valueType == 2 || valueType == 3) {
			CollaDepAmt = valueAmt;
			uint CollaDepAmt_18 = CollaDepAmt.mul(10**(uint(18).sub(collaAddrDecimal)));
			USDsAmt = CollaDepAmt_18.mul(chiPrec.mul(priceColla)).div(precisionColla).div(chiMint());

			SPABurnAmt = USDsAmt.mul(chiPrec - chiMint()).mul(precisionSPA).div(priceSPA.mul(chiPrec));
			if (swapFee > 0) {
				SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(swapFeePresion));
			}

			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		}
	}

	function _mint(
		address collaAddr,
		uint valueAmt,
		uint8 valueType
	) internal whenMintRedeemAllowed {
		(uint SPABurnAmt, uint CollaDepAmt, uint USDsAmt, uint swapFeeAmount) = mintView(collaAddr, valueAmt, valueType);
		ISperaxToken(SPATokenAddr).burnFrom(msg.sender, SPABurnAmt);
		if (valueType != 3) {
			ERC20Upgradeable(collaAddr).safeTransferFrom(msg.sender, collaValut, CollaDepAmt);
		}
		USDsInstance.mint(msg.sender, USDsAmt);
		USDsInstance.mint(USDsFeeValut, swapFeeAmount);

		emit USDSMinted(msg.sender, USDsAmt, SPABurnAmt, swapFeeAmount);
	}

	function redeem(address collaAddr, uint USDsAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_redeem(collaAddr, USDsAmt);
	}


	function redeemView(
		address collaAddr,
		uint USDsAmt
	) public returns (uint SPAMintAmt, uint CollaUnlockAmt, uint USDsBurntAmt, uint swapFeeAmount) {
		uint priceColla = IOracle(oracleAddr).collatPrice(collaAddr);
		uint precisionColla = IOracle(oracleAddr).collatPricePrecision(collaAddr);
		uint priceSPA = IOracle(oracleAddr).getSPAPrice();
		uint precisionSPA = IOracle(oracleAddr).SPAPricePrecision();
		uint swapFee = calculateSwapFeeOut();
		uint collaAddrDecimal = uint(ERC20Upgradeable(collaAddr).decimals());
		SPAMintAmt = USDsAmt.mul((chiPrec - chiRedeem()).mul(precisionSPA)).div(priceSPA.mul(chiPrec));
		if (swapFee > 0) {
			SPAMintAmt = SPAMintAmt.sub(SPAMintAmt.mul(swapFee).div(swapFeePresion));
		}

		//Unlock collaeral
		uint CollaUnlockAmt_18 = USDsAmt.mul(chiMint().mul(precisionColla)).div(chiPrec.mul(priceColla));
		CollaUnlockAmt = CollaUnlockAmt_18.div(10**(uint(18).sub(collaAddrDecimal)));
		if (swapFee > 0) {
			CollaUnlockAmt = CollaUnlockAmt.sub(CollaUnlockAmt.mul(swapFee).div(swapFeePresion));
		}


		//Burn USDs
		swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		USDsBurntAmt =  USDsAmt.sub(swapFeeAmount);
	}

	function _redeem(
		address collaAddr,
		uint USDsAmt
	) internal whenMintRedeemAllowed {
		(uint SPAMintAmt, uint CollaUnlockAmt, uint USDsBurntAmt, uint swapFeeAmount) = redeemView(collaAddr, USDsAmt);

		ISperaxToken(SPATokenAddr).mintForUSDs(msg.sender, SPAMintAmt);
		ERC20Upgradeable(collaAddr).safeTransfer(msg.sender, CollaUnlockAmt);
		USDsInstance.burn(msg.sender, USDsBurntAmt);
		USDsInstance.transferFrom(msg.sender, USDsFeeValut, swapFeeAmount);

		emit USDSRedeemed(msg.sender, USDsBurntAmt, SPAMintAmt, swapFeeAmount);
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

			emit TotalSupplyChanged(totalSupply, vaultValue);
		}
	}

	/**
	 * @dev  Precision: same as chi
	 */

	function collateralRatio() public view returns (uint256 ratio) {
        uint totalValue = _totalValue();
		uint USDsSupply =  USDsInstance.totalSupply();
		ratio = totalValue.mul(chiPrec).div(USDsSupply);
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
        //     ERC20Upgradeable asset = ERC20Upgradeable(allCollat[y]);
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
        ERC20Upgradeable asset = ERC20Upgradeable(_asset);
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

			emit SwapFeeInAllowed(newAllowance, block.timestamp);
    }

    function toggleSwapfeeOutAllowed(bool newAllowance) external onlyOwner {
      swapfeeOutAllowed = newAllowance;

			emit SwapFeeOutAllowed(newAllowance, block.timestamp);
    }

    function updateCollateralList(address collatAddress, bool allowance) external onlyOwner {
			if (allowance) {
				require(supportedCollat[collatAddress] == 0, "Collateral already allowed");
				allCollat.push(collatAddress);
				supportedCollat[collatAddress] = allCollat.length;
			} else {
				require(supportedCollat[collatAddress] > 0, "Collateral not allowed");
				allCollat[supportedCollat[collatAddress] - 1] = allCollat[allCollat.length - 1];
				allCollat.pop();
				delete supportedCollat[collatAddress];
			}

			emit CollateralUpdated(collatAddress, allowance);
    }
}
