//TO-DO: check source file of SafeMathUpgradeable regarding trySub() (and the usage of "unchecked")
//TO-DO: check ERC20Upgradeable vs ERC20Upgradeable
// Note: assuming when exponentWithPrec >= 2^32, toReturn >= swapFeePresion () (TO-DO: work out the number)
//TO-DO: AAVE in progress
//TO-DO: deal with assetDefaultStrategies
//TO-DO: what happen when we redeem aTokens
//TO-DO: whether _redeem needs "SafeTransferFrom" and how
//TO-DO: check all user inputs, especially mintView
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

	bool public mintRedeemAllowed;	// if false, no USDs can be minted or burnt
	bool public capitalAllowed;		// if false, no collaterals can be reinvested

	bool public swapfeeInAllowed;
	bool public swapfeeOutAllowed;

	mapping(address => uint) public supportedCollatAmount;	// the total amount of some supported collateral users have staked 	
	mapping(address => uint) public supportedCollat;		// if it is 1, the collateral is supported; else it is 0, it is not supported
	mapping(address => address) public assetDefaultStrategies;	// the corresponding strategy contract address to a supported collateral token (currently, they are all AAVE)
	address[] allCollat;	// the list of all supported collaterals
	address[] allStrategies;	// the list of all strategy addresses
	mapping (address => mapping (address => uint)) public strategiesAllocatedAmt; // the amount of a specific collateral re-invested by a chosen strategy

	address public SPATokenAddr;
	address public oracleAddr;
	address public collaValut;	// the contract address that stores all collaterals
								// WARNING: currently, this address is the same as the address of VaultCore.sol
	address public SPAValut;	
	address public USDsFeeValut;	// the account that stores all swapping fees
	address public USDsYieldValut;	// TO DELETE

	uint public startBlockHeight;

	// the following constant economic parameters are subject to changes
	uint public constant chi_alpha = 513;
	uint public constant chi_alpha_Prec = 10**12;
	uint public constant chiPrec = chi_alpha_Prec;
	uint public constant chiInit = chiPrec * 100 / 95;
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

	uint public constant allocatePrecentage = 8;
	uint public constant allocatePrecentage_Prec = 10;


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
	/**
	 * @dev check if USDs mint & redeem are both allowed
	 */
	modifier whenMintRedeemAllowed {
		require(mintRedeemAllowed, "Mint & redeem paused");
		_;
	}
	/**
	 * @dev check if re-investment of collaterals is allowed
	 */
	modifier whenNotCapitalPaused {
		require(capitalAllowed, "Allocate paused");
		_;
	}
	/**
	 * @dev disable USDs mint & redeem
	 */
	function updateMintBurn(bool _mintRedeemAllowed) external onlyOwner {
		mintRedeemAllowed = _mintRedeemAllowed;
	}
	/**
	 * @dev disable collateral re-investment
	 */
	function updateCapitalAllowance(bool _capitalAllowed) external onlyOwner {
		capitalAllowed = _capitalAllowed;
	}
	/**
	 * @dev disable swapInFee, i.e. mint becomes free
	 */
	function updateSwapInFee(bool _swapfeeInAllowed) external onlyOwner {
		swapfeeInAllowed = _swapfeeInAllowed;
	}
	/**
	 * @dev disable swapOutFee, i.e. redeem becomes free
	 */
	function updateSwapOutFee(bool _swapfeeOutAllowed) external onlyOwner {
		swapfeeOutAllowed = _swapfeeOutAllowed;
	}

	/**
	 * @dev add a new supported collateral
	 * @param _asset the address of the new supported collateral
	 */
	function supportAsset(address _asset, bool _flag) external onlyOwner {
		if (_flag) {
			require(supportedCollat[_asset] == 0, "Asset already supported");
			allCollat.push(_asset);
			supportedCollat[_asset] = allCollat.length;
		} else {
			require(supportedCollat[_asset] > 0, "Asset already removed");
			allCollat[supportedCollat[_asset] - 1] = allCollat[allCollat.length - 1];
			allCollat.pop();
			supportedCollat[_asset] = 0;
		}
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
		SPATokenAddr = 0x2B607b664A1012aD658b430E03603be1DC83EeCc;	// SPA on Kovan

		collaValut = address(this);
		SPAValut = address(this);
		USDsFeeValut = address(this);
		USDsYieldValut = address(this);	// TO DELETE
		supportedCollat[0xb7a4F3E9097C08dA09517b5aB877F7a917224ede] = 1;	// USDC on Kovan
		allCollat.push(0xb7a4F3E9097C08dA09517b5aB877F7a917224ede);
		supportedCollat[0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa] = 2;	// Dai on Kovan
		allCollat.push(0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa);
		supportedCollat[0x07de306FF27a2B630B1141956844eB1552B956B5] = 3;	// USDT on Kovan
		allCollat.push(0x07de306FF27a2B630B1141956844eB1552B956B5);
		USDsInstance = USDs(USDsToken_);
		oracleAddr = oracleAddr_;
		BancorInstance = BancorFormula(BancorFormulaAddr_);
		startBlockHeight = block.number;
	}

	/**
	 * @dev calculate the InSwap fee, i.e. fees for minting USDs
	 * @return the InSwap fee
	 */
	function calculateSwapFeeIn() public returns (uint) {
		// if InSwap fee is disabled, return 0
		if (!swapfeeInAllowed) {
			return 0;
		}

		// implement the formula in Section 4.3.1 of whitepaper 
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
	/**
	 * @dev calculate the OutSwap fee, i.e. fees for redeeming USDs
	 * @return the OutSwap fee 
	 */
	function calculateSwapFeeOut() public view returns (uint) {
		// if the OutSwap fee is diabled, return 0
		if (!swapfeeOutAllowed) {
			return 0;
		}

		// implement the formula in Section 4.3.2 of whitepaper
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


	// note: chi_alpha_Prec = chiPrec
	/**
	 * @dev calculate chiTarget by the formula in section 2.2 of the whitepaper
	 * @param chiInit_ the initial value of chi
	 * @param blockPassed the number of blocks that have passed since USDs is launched, i.e. "Block Height"
	 * @param priceUSDs the price of USDs, i.e. "USDs Price"
	 * @param precisionUSDs the precision used in the variable "priceUSDs"
	 * @return chiTarget_ the value of chiTarget
	 */
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

	/**
	 * @dev calculate chiMint
	 * @return chiMint, i.e. chiTarget, since they share the same value 
	 */
	function chiMint() public returns (uint)  {
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint blockPassed = uint(block.number).sub(startBlockHeight);
		return chiTarget(chiInit, blockPassed, priceUSDs, precisionUSDs);
	}

	/**
	 * @dev calculate chiRedeem based on the formula at the end of section 2.2
	 * @return chiRedeem_
	 */
	function chiRedeem() public returns (uint chiRedeem_) {
		// calculate chiTarget
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).USDsPricePrecision();
		uint blockPassed = uint(block.number).sub(startBlockHeight);
		uint chiTarget_ = chiTarget(chiInit, blockPassed, priceUSDs, precisionUSDs);
		// calculate chiRedeem
		uint collateralRatio_ = collateralRatio();
		if (chiTarget_ > collateralRatio_) {
			chiRedeem_ = chiTarget_.add(chi_gamma.mul(chiTarget_ - collateralRatio_).div(chi_gamma_Prec));
		} else {
			chiRedeem_ = chiTarget_;
		}

	}

	/**
	 * @dev mint USDs by entering USDs amount
	 * @param collaAddr the address of user's chosen collateral
	 * @param USDsMintAmt the amount of USDs to be minted
	 */
	function mintWithUSDs(address collaAddr, uint USDsMintAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(USDsMintAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, USDsMintAmt, 0);
	}

	/**
	 * @dev mint USDs by entering SPA amount
	 * @param collaAddr the address of user's chosen collateral
	 * @param SPAAmt the amount of SPA to burn
	 */
	function mintWithSPA(address collaAddr, uint SPAAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(SPAAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, SPAAmt, 1);
	}

	/**
	 * @dev mint USDs by entering collateral amount (excluding ETH)
	 * @param collaAddr the address of user's chosen collateral
	 * @param CollaAmt the amount of collateral to stake
	 */
	function mintWithColla(address collaAddr, uint CollaAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, CollaAmt, 2);
	}

	/**
	 * @dev mint USDs by ETH
	 * note: this function needs changes when USDs is deployed on other blockchain platform
	 */
	function mintWithEth() public payable whenMintRedeemAllowed {
    require(msg.value > 0, "Need to pay Ether");
		_mint(address(0), msg.value, 3);
	}

	//View functions

	/**
	 * @dev view related quantities for minting USDs with USDs amount
	 * @param collaAddr the address of user's chosen collateral
	 * @param USDsMintAmt the amount of USDs to mint
	 * @return SPABurnAmt the amount of SPA to burn
	 *			collaDepAmt the amount of collateral to stake
	 *			USDsAmt the amount of USDs to mint
	 *			swapFeeAmount the amount of Inswapfee to pay
	 */
	function mintWithUSDsView(address collaAddr, uint USDsMintAmt)
		public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(USDsMintAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, collaDepAmt, USDsAmt, swapFeeAmount) = mintView(collaAddr, USDsMintAmt, 0);
	}
	/**
	 * @dev view related quantities for minting USDs with SPA amount to burn
	 * @param collaAddr the address of user's chosen collateral
	 * @param SPAAmt the amount of SPAs to burn
	 * @return SPABurnAmt the amount of SPA to burn
	 *			collaDepAmt the amount of collateral to stake
	 *			USDsAmt the amount of USDs to mint
	 *			swapFeeAmount the amount of Inswapfee to pay
	 */
	function mintWithSPAView(address collaAddr, uint SPAAmt)
		public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(SPAAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, collaDepAmt, USDsAmt, swapFeeAmount)  = mintView(collaAddr, SPAAmt, 1);
	}
	/**
	 * @dev view related quantities for minting USDs with collateral amount to stake (excluding ETH)
	 * @param collaAddr the address of user's chosen collateral
	 * @param CollaAmt the amount of collateral to stake
	 * @return SPABurnAmt the amount of SPA to burn
	 *			collaDepAmt the amount of collateral to stake
	 *			USDsAmt the amount of USDs to mint
	 *			swapFeeAmount the amount of Inswapfee to pay
	 */
	function mintWithCollaView(address collaAddr, uint CollaAmt)
		public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(supportedCollat[collaAddr] > 0, "Collateral not supported");
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, collaDepAmt, USDsAmt, swapFeeAmount) = mintView(collaAddr, CollaAmt, 2);
	}

	/**
	 * @dev view related quantities for minting USDs with ETH
	 * @param CollaAmt the amount of ETH that the user stakes for minting USDs
	 * @return SPABurnAmt the amount of SPA to burn
	 *			collaDepAmt the amount of collateral to stake
	 *			USDsAmt the amount of USDs to mint
	 *			swapFeeAmount the amount of Inswapfee to pay
	 *
	 * SPABurnAmt precision: 10^18
	 * collaDepAmt precision: 10^collaAddrDecimal
	 * USDsAmt precision: 10^18
	 * swapFeeAmount precision: swapFeePresion
	 */
	function mintWithEthView(uint CollaAmt)
		public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount)
	{
		require(CollaAmt > 0, "Amount needs to be greater than 0");
		(SPABurnAmt, collaDepAmt, USDsAmt, swapFeeAmount) = mintView(address(0), CollaAmt, 3);
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
	 *			collaDepAmt the amount of collateral to stake
	 *			USDsAmt the amount of USDs to mint
	 *			swapFeeAmount the amount of Inswapfee to pay
	 */
	function mintView(
		address collaAddr,
		uint valueAmt,
		uint8 valueType
	) public returns (uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount) {
		// obtain the price and pecision of the collateral
		uint priceColla = 0;
		uint precisionColla = 0;
		if (valueType == 3) {
			priceColla = IOracle(oracleAddr).getETHPrice();
			precisionColla = IOracle(oracleAddr).ETHPricePrecision();
		} else {
			priceColla = IOracle(oracleAddr).collatPrice(collaAddr);
			precisionColla = IOracle(oracleAddr).collatPricePrecision(collaAddr);
		}
		// obtain other necessary data
		uint priceSPA = IOracle(oracleAddr).getSPAPrice();
		uint precisionSPA = IOracle(oracleAddr).SPAPricePrecision();
		uint swapFee = calculateSwapFeeIn();
		uint collaAddrDecimal = uint(ERC20Upgradeable(collaAddr).decimals());

		if (valueType == 0) { // when mintWithUSDs
			// calculate USDsAmt
			USDsAmt = valueAmt;
			// calculate SPABurnAmt
			SPABurnAmt = USDsAmt.mul(chiPrec - chiMint()).mul(precisionSPA).div(priceSPA.mul(chiPrec));
			if (swapFee > 0) {
				SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(swapFeePresion));
			}
			// calculate collaDepAmt
			uint collaDepAmt_18 = USDsAmt.mul(chiMint()).mul(precisionColla).div(chiPrec.mul(priceColla));
			collaDepAmt = collaDepAmt_18.div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				collaDepAmt = collaDepAmt.add(collaDepAmt.mul(swapFee).div(swapFeePresion));
			}
			// calculate swapFeeAmount
			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);

		} else if (valueType == 1) { // when mintWithSPA
			// calculate SPABurnAmt
			SPABurnAmt = valueAmt;
			// calculate USDsAmt
			USDsAmt = SPABurnAmt;
			if (swapFee > 0) {
				USDsAmt = USDsAmt.mul(swapFeePresion).div(swapFeePresion.add(swapFee));
			}
			USDsAmt = USDsAmt.mul(chiPrec).mul(priceSPA).div(precisionSPA.mul(chiPrec - chiMint()));
			// calculate collaDepAmt
			uint collaDepAmt_18 = USDsAmt.mul(chiMint()).mul(precisionColla).div(chiPrec.mul(priceColla));
			collaDepAmt = collaDepAmt_18.div(10**(uint(18).sub(collaAddrDecimal)));
			if (swapFee > 0) {
				collaDepAmt = collaDepAmt.add(collaDepAmt.mul(swapFee).div(swapFeePresion));
			}
			// calculate swapFeeAmount
			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);

		} else if (valueType == 2 || valueType == 3) { // when mintWithColla or mintWithETH
			// calculate collaDepAmt
			collaDepAmt = valueAmt;
			// calculate USDsAmt
			USDsAmt = collaDepAmt;
			if (swapFee > 0) {
				USDsAmt = USDsAmt.mul(swapFeePresion).div(swapFeePresion.add(swapFee));
			}
			uint CollaDepAmt_18 = USDsAmt.mul(10**(uint(18).sub(collaAddrDecimal)));
			USDsAmt = CollaDepAmt_18.mul(chiPrec.mul(priceColla)).div(precisionColla).div(chiMint());
			// calculate SPABurnAmt
			SPABurnAmt = USDsAmt.mul(chiPrec - chiMint()).mul(precisionSPA).div(priceSPA.mul(chiPrec));
			if (swapFee > 0) {
				SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(swapFeePresion));
			}
			// calculate swapFeeAmount
			swapFeeAmount = USDsAmt.mul(swapFee).div(swapFeePresion);
		}
	}

	/**
	 * @dev the generic, internal mint function
	 * @param collaAddr the address of the collateral
	 * @param valueAmt the amount of tokens (the specific meaning depends on valueType)
	 * @param valueType the type of tokens (specific meanings are listed below)
	 *		valueType = 0: mintWithUSDs
	 *		valueType = 1: mintWithSPA
	 *		valueType = 2: mintWithColla
	 *		valueType = 3: mintWithETH
	 */
	function _mint(
		address collaAddr,
		uint valueAmt,
		uint8 valueType
	) internal whenMintRedeemAllowed {
		// calculate all necessary related quantities based on user inputs
		(uint SPABurnAmt, uint collaDepAmt, uint USDsAmt, uint swapFeeAmount) = mintView(collaAddr, valueAmt, valueType);
		// burn SPA tokens
		ISperaxToken(SPATokenAddr).burnFrom(msg.sender, SPABurnAmt);
		// if it it not mintWithETH, stake collaterals
		if (valueType != 3) {
			ERC20Upgradeable(collaAddr).safeTransferFrom(msg.sender, collaValut, collaDepAmt);
		}
		// mint USDs and collect swapIn fees
		USDsInstance.mint(msg.sender, USDsAmt);
		USDsInstance.mint(USDsFeeValut, swapFeeAmount);
		// update global stats
		supportedCollatAmount[collaAddr] = supportedCollatAmount[collaAddr].add(collaDepAmt);
		//TO DO
		//emit USDSMinted(msg.sender, USDsAmt, SPABurnAmt, swapFeeAmount);
	}

	/**
	 *
	 */
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
