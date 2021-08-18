//TO-DO: check source file of SafeMathUpgradeable regarding trySub() (and the usage of "unchecked")
//TO-DO: check ERC20Upgradeable vs ERC20Upgradeable
// Note: assuming when exponentWithPrec >= 2^32, toReturn >= swapFeePresion () (TO-DO: work out the number)
//TO-DO: AAVE in progress
//TO-DO: deal with assetDefaultStrategies
pragma solidity ^0.6.12;

import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/AddressUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";

import "../libraries/MyMath.sol";
import "../libraries/Helpers.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/ISperaxToken.sol";
import "../interfaces/IStrategy.sol";
import "../interfaces/IVault.sol";
import "../libraries/StableMath.sol";
import { USDs } from "../token/USDs.sol";
import { BancorFormula } from "../libraries/BancorFormula.sol";

contract VaultCore is Initializable, OwnableUpgradeable {
	using SafeERC20Upgradeable for ERC20Upgradeable;
	using SafeMathUpgradeable for uint;
	using MyMath for uint;
	using StableMath for uint;

	bool public mintRedeemAllowed;
	bool public capitalAllowed;

	bool public swapfeeInAllowed;
	bool public swapfeeOutAllowed;

	mapping(address => uint) public supportedCollatAmount;
	mapping(address => uint) public supportedCollat;
	mapping(address => address) public assetDefaultStrategies;
	address[] allCollat;
	address[] allStrategies;
	mapping (address => mapping (address => uint)) public strategiesAllocatedAmt;

	address public SPATokenAddr;
	address public oracleAddr;
	address public collaValut;
	address public SPAValut;
	address public USDsFeeValut;
	address public USDsYieldValut;

	uint public startBlockHeight;


	uint public constant chi_alpha = 513;
	uint public constant chi_alpha_Prec = 10**12;
	uint public constant chiPrec = chi_alpha_Prec;
	uint public chiInit = chiPrec * 100 / 95;
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

	uint public allocatePrecentage = 8;
	uint public allocatePrecentage_Prec = 10;


	USDs USDsInstance;
	BancorFormula BancorInstance;

	// event USDSMinted(
	// 	address indexed wallet,
	// 	uint indexed USDsAmt,
	// 	uint indexed SPAsAmt,
	// 	uint feeAmt
	// );
	//
	// event USDSRedeemed(
	// 	address indexed wallet,
	// 	uint indexed USDsAmt,
	// 	uint indexed SPAsAmt,
	// 	uint feeAmt
	// );
	//
	// event TotalSupplyChanged(
	// 	uint indexed oldSupply,
	// 	uint indexed newSupply
	// );
	//
	// event SwapFeeInAllowed(
	// 	bool indexed allowance,
	// 	uint time
	// );
	//
	// event SwapFeeOutAllowed(
	// 	bool indexed allowance,
	// 	uint time
	// );
	//
	// event CollateralUpdated(
	// 	address indexed token,
	// 	bool indexed allowance
	// );


	// ADMIN

	modifier whenMintRedeemAllowed {
		require(mintRedeemAllowed, "Mint & redeem paused");
		_;
	}

	modifier whenNotCapitalPaused {
		require(capitalAllowed, "Allocate paused");
		_;
	}

	function pauseMintBurn() external onlyOwner {
		mintRedeemAllowed = false;
	}
	function unpauseMintBurn() external onlyOwner {
		mintRedeemAllowed = true;
	}
	function pauseAllocate() external onlyOwner {
		capitalAllowed = false;
	}
	function unpauseAllocate() external onlyOwner {
		capitalAllowed = true;
	}
	function pauseSwapInFee() external onlyOwner {
		swapfeeInAllowed = false;
	}
	function unpauseSwapInFee() external onlyOwner {
		swapfeeInAllowed = true;
	}
	function pauseSwapOutFee() external onlyOwner {
		swapfeeOutAllowed = false;
	}
	function unpauseSwapOutFee() external onlyOwner {
		swapfeeOutAllowed = true;
	}

    function supportAsset(address _asset) external onlyOwner {
        require(supportedCollat[_asset] == 0, "Asset already supported");
		supportedCollat[_asset] = 1;
		allCollat.push(_asset);
		// TO-DO: add Oracle support here;
    }

	//INITIALIZER

	function initialize(address USDsToken_, address oracleAddr_, address BancorFormulaAddr_) public initializer {
		OwnableUpgradeable.__Ownable_init();
		// Initialize variables
		mintRedeemAllowed = true;
		swapfeeInAllowed = true;
		swapfeeOutAllowed = true;
		capitalAllowed = true;
		SPATokenAddr = 0x2B607b664A1012aD658b430E03603be1DC83EeCc;

		collaValut = address(this);
		SPAValut = address(this);
		USDsFeeValut = address(this);
		USDsYieldValut = address(this);
		supportedCollat[0xb7a4F3E9097C08dA09517b5aB877F7a917224ede] = 1;
		allCollat.push(0xb7a4F3E9097C08dA09517b5aB877F7a917224ede);
		supportedCollat[0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa] = 1;
		allCollat.push(0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa);
		supportedCollat[0x07de306FF27a2B630B1141956844eB1552B956B5] = 1;
		allCollat.push(0x07de306FF27a2B630B1141956844eB1552B956B5);
		USDsInstance = USDs(USDsToken_);
		oracleAddr = oracleAddr_;
		BancorInstance = BancorFormula(BancorFormulaAddr_);
		startBlockHeight = block.number;
	}


	function calculateSwapFeeIn() public returns (uint) {
		if (!swapfeeInAllowed) {
			return 0;
		}

		uint priceUSDs_Average = IOracle(oracleAddr).getUSDsPrice_Average(); //TODO: change to 3 days average
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint smallPwithPrecision = swapFee_p.mul(precisionUSDs).div(swapFee_p_Prec);
		if (smallPwithPrecision < priceUSDs_Average) {
			return swapFeePresion / 1000; // 0.1%
		} else {
			uint temp = (smallPwithPrecision - priceUSDs_Average).mul(swapFee_theta).div(swapFee_theta_Prec); //precision: precisionUSDs
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

	// Note: need to be less than (2^32 - 1)
	// Note: assuming when exponentWithPrec >= 2^32, toReturn >= swapFeePresion () (TO-DO: work out the number)
	function calculateSwapFeeOut() public view returns (uint) {
		if (!swapfeeOutAllowed) {
			return 0;
		}
		uint USDsInOutRatio = IOracle(oracleAddr).USDsInOutRatio();
		uint USDsInOutRatioPrecision = IOracle(oracleAddr).USDsInOutRatioPrecision();
		if (USDsInOutRatio <= uint(12).mul(USDsInOutRatioPrecision).div(10)) {
			return swapFeePresion / 1000; //0.1%
		} else {
			uint exponentWithPrec = USDsInOutRatio - uint(12).mul(USDsInOutRatioPrecision).div(10);
			if (exponentWithPrec >= 2^32) {
				return swapFeePresion;
			}
			(uint powResWithPrec, uint8 powResPrec) = BancorInstance.power(swapFee_A, swapFee_A_Prec, uint32(exponentWithPrec), uint32(USDsInOutRatioPrecision));
			uint toReturn = uint(powResWithPrec >> powResPrec).mul(swapFeePresion).div(100);
			if (toReturn >= swapFeePresion) {
				return swapFeePresion;
			} else {
				return toReturn;
			}
		}
	}
	// chi_alpha_Prec = chiPrec
	function chiTarget(uint chiInit_, uint blockPassed, uint priceUSDs, uint precisionUSDs) public pure returns (uint chiTarget_) {
		uint chiAdjustmentA = blockPassed.mul(chiPrec).mul(chi_alpha).div(chi_alpha_Prec);
		uint chiAdjustmentB;
		uint afterB;
		if (priceUSDs >= precisionUSDs) {
			chiAdjustmentB = chi_beta.mul(chiPrec).mul(priceUSDs - precisionUSDs).mul(priceUSDs - precisionUSDs).div(chi_beta_Prec);
			afterB = chiInit_.add(chiAdjustmentB);
		} else {
			chiAdjustmentB = chi_beta.mul(chiPrec).mul(precisionUSDs - priceUSDs).mul(precisionUSDs - priceUSDs).div(chi_beta_Prec);
			(, afterB) = chiInit_.trySub(chiAdjustmentB);
		}
		(, chiTarget_) = afterB.trySub(chiAdjustmentA);
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
		uint collateralRatio_ = collateralRatio();
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
		public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(USDsMintAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, collaDepAmt, USDsAmt, swapFeeAmount) = mintView(collaAddr, USDsMintAmt, 0);
	}

	function mintWithSPAView(address collaAddr, uint SPAAmt)
		public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(SPAAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, collaDepAmt, USDsAmt, swapFeeAmount)  = mintView(collaAddr, SPAAmt, 1);
	}

	function mintWithCollaView(address collaAddr, uint CollaAmt)
		public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, collaDepAmt, USDsAmt, swapFeeAmount) = mintView(collaAddr, CollaAmt, 2);
	}

	// SPABurnAmt precision: 10^18
	// collaDepAmt precision: 10^collaAddrDecimal
	// USDsAmt precision: 10^18
	// swapFeeAmount precision: swapFeePresion
	function mintWithEthView(uint CollaAmt)
		public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, collaDepAmt, USDsAmt, swapFeeAmount) = mintView(address(0), CollaAmt, 3);
	}

	function mintView(
		address collaAddr,
		uint valueAmt,
		uint8 valueType
	) public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount) {
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
			uint collaDepAmt_18 = USDsAmt.mul(chiMint()).mul(precisionColla).div(chiPrec.mul(priceColla));
			collaDepAmt = collaDepAmt_18.div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				collaDepAmt = collaDepAmt.add(collaDepAmt.mul(swapFee).div(swapFeePresion));
			}

			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		} else if (valueType == 1) {
			SPABurnAmt = valueAmt;

			USDsAmt = SPABurnAmt;
			if (swapFee > 0) {
				USDsAmt = USDsAmt.mul(swapFeePresion).div(swapFeePresion.add(swapFee));
			}
			USDsAmt = USDsAmt.mul(chiPrec).mul(priceSPA).div(precisionSPA.mul(chiPrec - chiMint()));

			//Deposit collaeral
			uint collaDepAmt_18 = USDsAmt.mul(chiMint()).mul(precisionColla).div(chiPrec.mul(priceColla));
			collaDepAmt = collaDepAmt_18.div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				collaDepAmt = collaDepAmt.add(collaDepAmt.mul(swapFee).div(swapFeePresion));
			}

			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		} else if (valueType == 2 || valueType == 3) {
			collaDepAmt = valueAmt;
			USDsAmt = collaDepAmt;

			if (swapFee > 0) {
				USDsAmt = USDsAmt.mul(swapFeePresion).div(swapFeePresion.add(swapFee));
			}
			uint CollaDepAmt_18 = USDsAmt.mul(10**(uint(18).sub(collaAddrDecimal)));
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
		(uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount) = mintView(collaAddr, valueAmt, valueType);
		ISperaxToken(SPATokenAddr).burnFrom(msg.sender, SPABurnAmt);
		if (valueType != 3) {
			ERC20Upgradeable(collaAddr).safeTransferFrom(msg.sender, collaValut, collaDepAmt);
		}
		USDsInstance.mint(msg.sender, USDsAmt);
		USDsInstance.mint(USDsFeeValut, swapFeeAmount);

		supportedCollatAmount[collaAddr] = supportedCollatAmount[collaAddr].add(collaDepAmt);
		//emit USDSMinted(msg.sender, USDsAmt, SPABurnAmt, swapFeeAmount);
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
	) public returns (uint SPAMintAmt, uint collaUnlockAmt, uint USDsBurntAmt, uint swapFeeAmount) {
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
		uint collaUnlockAmt_18 = USDsAmt.mul(chiMint().mul(precisionColla)).div(chiPrec.mul(priceColla));
		collaUnlockAmt = collaUnlockAmt_18.div(10**(uint(18).sub(collaAddrDecimal)));
		if (swapFee > 0) {
			collaUnlockAmt = collaUnlockAmt.sub(collaUnlockAmt.mul(swapFee).div(swapFeePresion));
		}


		//Burn USDs
		swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		USDsBurntAmt =  USDsAmt.sub(swapFeeAmount);
	}

	function _redeem(
		address collaAddr,
		uint USDsAmt
	) internal whenMintRedeemAllowed {
		(uint SPAMintAmt, uint collaUnlockAmt, uint USDsBurntAmt, uint swapFeeAmount) = redeemView(collaAddr, USDsAmt);

		ISperaxToken(SPATokenAddr).mintForUSDs(msg.sender, SPAMintAmt);
		ERC20Upgradeable(collaAddr).safeTransfer(msg.sender, collaUnlockAmt);
		supportedCollatAmount[collaAddr] = supportedCollatAmount[collaAddr].sub(collaUnlockAmt);
		USDsInstance.burn(msg.sender, USDsBurntAmt);
		USDsInstance.transferFrom(msg.sender, USDsFeeValut, swapFeeAmount);

		//emit USDSRedeemed(msg.sender, USDsBurntAmt, SPAMintAmt, swapFeeAmount);
	}

	/**
	 * @dev Calculate the total value of assets held by the Vault and all
	 *      strategies and update the supply of USDs.
	 */
	function rebase() external onlyOwner {
		_rebase();
	}

	/**
	 * @dev Calculate the total value of assets held by the Vault and all
	 *      strategies and update the supply of USDs, optionaly sending a
	 *      portion of the yield to the trustee.
	 */
	function _rebase() internal {
		address _strategyAddr;
		IStrategy strategy;
		address collaAddr;
		uint allocatedAmt;
		uint newTokensAmt;
		uint USDsSupplyIncrement;
		uint USDsSupplyIncrementTotal;
		for (uint y = 0; y < allCollat.length; y++) {
			collaAddr = allCollat[y];
			for (uint i = 0; i < allStrategies.length; i++) {
				_strategyAddr = allStrategies[i];
				strategy = IStrategy(_strategyAddr);
				allocatedAmt = strategiesAllocatedAmt[collaAddr][_strategyAddr] ;
				(, newTokensAmt) = strategy.checkBalance(collaAddr).trySub(allocatedAmt);
				if (newTokensAmt > 0) {
					strategy.withdraw(address(this), collaAddr, newTokensAmt);
					(uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount) = mintView(collaAddr, newTokensAmt, 2);
					//strategy.withdraw(address(this), collaAddr, collaDepAmt);
					ISperaxToken(SPATokenAddr).burnFrom(SPAValut, SPABurnAmt);
					USDsSupplyIncrement = USDsInstance._totalSupply().add(USDsAmt).add(swapFeeAmount);
					USDsSupplyIncrementTotal = USDsSupplyIncrementTotal.add(USDsSupplyIncrement);
				}
				USDsInstance.changeSupply(USDsSupplyIncrementTotal);
		   }
		}



	}
	//
	// /**
	//  * @dev  Precision: same as chi (chiPrec)
	//  */
	//
	function collateralRatio() public returns (uint ratio) {
        uint totalValueLocked = _totalValueLocked();
		uint USDsSupply =  USDsInstance.totalSupply();
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint USDsValue = USDsSupply.mul(priceUSDs).div(precisionUSDs);
		ratio = totalValueLocked.mul(chiPrec).div(USDsValue);
    }

    function totalValueLocked() external view returns (uint value) {
        value = _totalValueLocked();
    }

    function _totalValueLocked() internal view returns (uint value) {
		value = _totalValueInVault().add(_totalValueInStrategies());
    }

	function totalValueInVault() external view returns (uint value) {
		value = _totalValueInVault();
	}

	function _totalValueInVault() internal view returns (uint value) {
		address collaAddr;
		uint priceColla = 0;
		uint precisionColla = 0;
		uint collaAddrDecimal = 0;
		uint collaTotalValueInVault = 0;
		uint collaTotalValueInVault_18 = 0;
		for (uint y = 0; y < allCollat.length; y++) {
			collaAddr = allCollat[y];
			priceColla = IOracle(oracleAddr).collatPrice(collaAddr);
			precisionColla = IOracle(oracleAddr).collatPricePrecision(collaAddr);
			collaAddrDecimal = uint(ERC20Upgradeable(collaAddr).decimals());
			collaTotalValueInVault = ERC20Upgradeable(collaAddr).balanceOf(address(this)).mul(priceColla).div(precisionColla);
			collaTotalValueInVault_18 = collaTotalValueInVault.mul(10**(uint(18).sub(collaAddrDecimal)));
			value = value.add(collaTotalValueInVault_18);
		}
	}

	function totalValueInStrategies() external view returns (uint value) {
		value = _totalValueInStrategies();
	}

	function _totalValueInStrategies() internal view returns (uint value) {
		for (uint i = 0; i < allStrategies.length; i++) {
		   value = value.add(_totalValueInStrategy(allStrategies[i]));
	   }
	}


	function _totalValueInStrategy(address _strategyAddr) internal view returns (uint value) {
		IStrategy strategy = IStrategy(_strategyAddr);
		address collaAddr;
		uint priceColla = 0;
		uint precisionColla = 0;
		uint collaAddrDecimal = 0;
		uint collaTotalValueInStrategy = 0;
		uint collaTotalValueInStrategy_18 = 0;
		for (uint y = 0; y < allCollat.length; y++) {
			collaAddr = allCollat[y];
			if (strategy.supportsAsset(collaAddr)) {
				priceColla = IOracle(oracleAddr).collatPrice(collaAddr);
				precisionColla = IOracle(oracleAddr).collatPricePrecision(collaAddr);
				collaAddrDecimal = uint(ERC20Upgradeable(collaAddr).decimals());
				collaTotalValueInStrategy = strategy.checkBalance(allCollat[y]).mul(priceColla).div(precisionColla);
				collaTotalValueInStrategy_18 = collaTotalValueInStrategy.mul(10**(uint(18).sub(collaAddrDecimal)));
				value = value.add(collaTotalValueInStrategy_18);
			}
		}
	}



	/**
     * @notice Allocate unallocated funds on Vault to strategies.
     * @dev Allocate unallocated funds on Vault to strategies.
     **/
    function allocate() external whenNotCapitalPaused {
        _allocate();
    }

    /**
     * @notice Allocate unallocated funds on Vault to strategies.
     * @dev Allocate unallocated funds on Vault to strategies.
     **/
    function _allocate() internal {
        // Iterate over all assets in the Vault and allocate the the appropriate
        // strategy
        for (uint i = 0; i < allCollat.length; i++) {
			address collateralAddr = allCollat[i];
            ERC20Upgradeable collateralERC20 = ERC20Upgradeable(collateralAddr);
            uint collatInVault = collateralERC20.balanceOf(address(this));
			uint collatInVaultTotal = supportedCollatAmount[allCollat[i]];
			(,uint allocateAmount) = collatInVaultTotal.mul(allocatePrecentage).div(allocatePrecentage_Prec).trySub(collatInVault);

            address depositStrategyAddr = assetDefaultStrategies[collateralAddr];

            if (depositStrategyAddr != address(0) && allocateAmount > 0) {
                IStrategy strategy = IStrategy(depositStrategyAddr);
                collateralERC20.safeTransfer(address(strategy), allocateAmount);
                strategy.deposit(collateralAddr, allocateAmount);
				strategiesAllocatedAmt[collateralAddr][depositStrategyAddr] = strategiesAllocatedAmt[collateralAddr][depositStrategyAddr].add(allocateAmount);
            }
        }
    }




}
