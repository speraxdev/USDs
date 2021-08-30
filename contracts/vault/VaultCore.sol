//TO-DO: check source file of SafeMathUpgradeable regarding trySub() (and the usage of "unchecked")
//TO-DO: check ERC20Upgradeable vs ERC20Upgradeable
// Note: assuming when exponentWith_prec >= 2^32, toReturn >= swapFeePresion () (TO-DO: work out the number)
//TO-DO: deal with collateralStrategies
//TO-DO: what happen when we redeem aTokens
//TO-DO: whether _redeem needs "SafeTransferFrom" and how
//TO-DO: check all user inputs, especially mintView
//TO-DO: style reorg
//TO-DO: vault and address(this)
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
import "../libraries/VaultCoreLibrary.sol";
import "../token/USDs.sol";
import "../libraries/BancorFormula.sol";
import "../interfaces/IBuyback.sol";

contract VaultCore is Initializable, OwnableUpgradeable {
	using SafeERC20Upgradeable for ERC20Upgradeable;
	using SafeMathUpgradeable for uint;
	using MyMath for uint;
	using StableMath for uint;

	bool public mintRedeemAllowed;	// if false, no USDs can be minted or burnt
	bool public allocationAllowed;		// if false, no collaterals can be reinvested
	bool public rebaseAllowed;
	bool public swapfeeInAllowed;
	bool public swapfeeOutAllowed;
	address public SPAaddr;
	address public oracleAddr;
	address public SPAvault;
	USDs USDsInstance;
	BancorFormula public BancorInstance;
	IBuyback BuybackInstance;
	uint public startBlockHeight;
	uint public constant chi_alpha = 513;
	uint public constant chi_alpha_prec = 10**12;
	uint public constant chi_prec = chi_alpha_prec;
	uint public constant chiInit = chi_prec * 100 / 95;
	uint public constant chi_beta = 9;
	uint public constant chi_beta_prec = 1;
	uint public constant chi_gamma = 1;
	uint public constant chi_gamma_prec = 1;
	uint public constant swapFeePresion = 1000000;
	uint public constant swapFee_p = 99;
	uint public constant swapFee_p_prec = 100;
	uint public constant swapFee_theta = 50;
	uint public constant swapFee_theta_prec = 1;
	uint32 public constant swapFee_a = 12;
	uint32 public constant swapFee_a_prec = 10;
	uint public constant swapFee_A = 20;
	uint public constant swapFee_A_prec = 1;
	uint public constant allocatePrecentage = 8;
	uint public constant allocatePrecentage_prec = 10;

	event USDsMinted(address indexed wallet, uint indexed USDsAmt, uint collateralAmt, uint SPAsAmt, uint feeAmt);
	event USDsRedeemed(address indexed wallet, uint indexed USDsAmt, uint collateralAmt, uint SPAsAmt, uint feeAmt);
	event Rebase(uint indexed oldSupply, uint indexed newSupply);
	event CollateralInfoChanged(address indexed collateralAddr, bool supported, address defaultStrategyAddr, bool allocationAllowed, uint8 rebaseMethod);
	event MintRedeemPermssionChanged(bool indexed permission);
	event AllocationPermssionChanged(bool indexed permission);
	event SwapFeeInPermissionChanged(bool indexed permission);
	event SwapFeeOutPermissionChanged(bool indexed permission);

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
	modifier whenAllocationAllowed {
		require(allocationAllowed, "Allocate paused");
		_;
	}
	/**
	 * @dev check if rebase is allowed
	 */
	modifier whenRebaseAllowed {
		require(rebaseAllowed, "Rebase paused");
		_;
	}

	struct collateralStruct {
		address collateralAddr;
		bool supported;
		address defaultStrategyAddr;
		bool allocationAllowed;
		uint8 rebaseMethod;
	}
	struct strategyStruct {
		address strategyAddr;
		bool enabled;
	}
	mapping(address => uint) public supportedCollateral;		// if it is 1, the collateral is supported; else it is 0, it is not supported
	mapping(address => collateralStruct) collateralsInfo;
	mapping(address => strategyStruct) strategiesInfo;
	collateralStruct[] allCollaterals;	// the list of all supported collaterals
	strategyStruct[] allStrategies;	// the list of all strategy addresses

	function initialize(address USDsToken_, address oracleAddr_, address BancorFormulaAddr_) public initializer {
		OwnableUpgradeable.__Ownable_init();
		mintRedeemAllowed = true;
		swapfeeInAllowed = true;
		swapfeeOutAllowed = true;
		allocationAllowed = true;
		SPAaddr = 0x2B607b664A1012aD658b430E03603be1DC83EeCc;	// SPA on Kovan
		SPAvault = address(this);
		USDsInstance = USDs(USDsToken_);
		oracleAddr = oracleAddr_;
		BancorInstance = BancorFormula(BancorFormulaAddr_);
		startBlockHeight = block.number;
	}

	/**
	 * @dev disable USDs mint & redeem
	 */
	function updateMintBurnPermission(bool _mintRedeemAllowed) external onlyOwner {
		mintRedeemAllowed = _mintRedeemAllowed;
		emit MintRedeemPermssionChanged(mintRedeemAllowed);
	}
	/**
	 * @dev disable collateral re-investment
	 */
	function updateAllocationPermission(bool _allocationAllowed) external onlyOwner {
		allocationAllowed = _allocationAllowed;
		emit AllocationPermssionChanged(allocationAllowed);
	}
	/**
	 * @dev disable swapInFee, i.e. mint becomes free
	 */
	function updateSwapInFee(bool _swapfeeInAllowed) external onlyOwner {
		swapfeeInAllowed = _swapfeeInAllowed;
		emit SwapFeeInPermissionChanged(swapfeeInAllowed);
	}
	/**
	 * @dev disable swapOutFee, i.e. redeem becomes free
	 */
	function updateSwapOutFee(bool _swapfeeOutAllowed) external onlyOwner {
		swapfeeOutAllowed = _swapfeeOutAllowed;
		emit SwapFeeOutPermissionChanged(swapfeeOutAllowed);
	}

	function updateCollateralInfo(address _collateralAddr, bool _supported, address _defaultStrategyAddr, bool _allocationAlloweduint8, uint8 _rebaseMethod) external onlyOwner {
		_updateCollateralInfo(_collateralAddr, _supported, _defaultStrategyAddr, _allocationAlloweduint8, _rebaseMethod);
	}

	function _updateCollateralInfo(address _collateralAddr, bool _supported, address _defaultStrategyAddr, bool _allocationAllowed, uint8 _rebaseMethod) internal {
		collateralStruct storage updatedCollateral = collateralsInfo[_collateralAddr];
		updatedCollateral.collateralAddr = _collateralAddr;
		updatedCollateral.supported = _supported;
		updatedCollateral.defaultStrategyAddr = _defaultStrategyAddr;
		updatedCollateral.allocationAllowed = _allocationAllowed;
		updatedCollateral.rebaseMethod = _rebaseMethod;
		emit CollateralInfoChanged(_collateralAddr, _supported, _defaultStrategyAddr, _allocationAllowed, _rebaseMethod);
	}

	/**
	 * @dev mint USDs by entering USDs amount
	 * @param collateralAddr the address of user's chosen collateral
	 * @param USDsMintAmt the amount of USDs to be minted
	 */
	function mintWithUSDs(address collateralAddr, uint USDsMintAmt)
		public
		whenMintRedeemAllowed
	{
		require(collateralsInfo[collateralAddr].supported, "Collateral not supported");
		require(USDsMintAmt > 0, "Amount needs to be greater than 0");
		_mint(collateralAddr, USDsMintAmt, 0);
	}

	/**
	 * @dev mint USDs by entering SPA amount
	 * @param collateralAddr the address of user's chosen collateral
	 * @param SPAAmt the amount of SPA to burn
	 */
	function mintWithSPA(address collateralAddr, uint SPAAmt)
		public
		whenMintRedeemAllowed
	{
		require(collateralsInfo[collateralAddr].supported, "Collateral not supported");
		require(SPAAmt > 0, "Amount needs to be greater than 0");
		_mint(collateralAddr, SPAAmt, 1);
	}

	/**
	 * @dev mint USDs by entering collateral amount (excluding ETH)
	 * @param collateralAddr the address of user's chosen collateral
	 * @param collateralAmt the amount of collateral to stake
	 */
	function mintWithColla(address collateralAddr, uint collateralAmt)
		public
		whenMintRedeemAllowed
	{
		require(collateralsInfo[collateralAddr].supported, "Collateral not supported");
		require(collateralAmt > 0, "Amount needs to be greater than 0");
		_mint(collateralAddr, collateralAmt, 2);
	}

	/**
	 * @dev mint USDs by ETH
	 * note: this function needs changes when USDs is deployed on other blockchain platform
	 */
	function mintWithEth() public payable whenMintRedeemAllowed {
    require(msg.value > 0, "Need to pay Ether");
		_mint(address(0), msg.value, 3);
	}


	/**
	 * @dev the generic, internal mint function
	 * @param collateralAddr the address of the collateral
	 * @param valueAmt the amount of tokens (the specific meaning depends on valueType)
	 * @param valueType the type of tokens (specific meanings are listed below)
	 *		valueType = 0: mintWithUSDs
	 *		valueType = 1: mintWithSPA
	 *		valueType = 2: mintWithColla
	 *		valueType = 3: mintWithETH
	 */
	function _mint(
		address collateralAddr,
		uint valueAmt,
		uint8 valueType
	) internal whenMintRedeemAllowed {
		// calculate all necessary related quantities based on user inputs
		(uint SPABurnAmt, uint collateralDepAmt, uint USDsAmt, uint swapFeeAmount) = VaultCoreLibrary.mintView(collateralAddr, valueAmt, valueType, address(this));
		// burn SPA tokens
		ISperaxToken(SPAaddr).burnFrom(msg.sender, SPABurnAmt);
		// if it it not mintWithETH, stake collaterals
		if (valueType != 3) {
			ERC20Upgradeable(collateralAddr).safeTransferFrom(msg.sender, address(this), collateralDepAmt);
		}
		// mint USDs and collect swapIn fees
		USDsInstance.mint(msg.sender, USDsAmt);
		USDsInstance.mint(address(this), swapFeeAmount);
		emit USDsMinted(msg.sender, USDsAmt, collateralDepAmt, SPABurnAmt, swapFeeAmount);
	}

	/**
	 *
	 */
	function redeem(address collateralAddr, uint USDsAmt)
		public
		whenMintRedeemAllowed
	{
		require(collateralsInfo[collateralAddr].supported, "Collateral not supported");
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_redeem(collateralAddr, USDsAmt);
	}

	function _redeem(
		address collateralAddr,
		uint USDsAmt
	) internal whenMintRedeemAllowed {
		(uint SPAMintAmt, uint collateralUnlockedAmt, uint USDsBurntAmt, uint swapFeeAmount) = VaultCoreLibrary.redeemView(collateralAddr, USDsAmt, address(this), oracleAddr);
		ISperaxToken(SPAaddr).mintForUSDs(msg.sender, SPAMintAmt);
		ERC20Upgradeable(collateralAddr).safeTransfer(msg.sender, collateralUnlockedAmt);
		USDsInstance.burn(msg.sender, USDsBurntAmt);
		USDsInstance.transferFrom(msg.sender, address(this), swapFeeAmount);

		emit USDsRedeemed(msg.sender, USDsBurntAmt, collateralUnlockedAmt,SPAMintAmt, swapFeeAmount);
	}

	/**
	 * @dev Calculate the total value of collaterals held by the Vault and all
	 *      strategies and update the supply of USDs.
	 */
	function rebase() external onlyOwner {
		_rebase();
	}

	/**
	 * @dev Calculate the total value of collaterals held by the Vault and all
	 *      strategies and update the supply of USDs, optionaly sending a
	 *      portion of the yield to the trustee.
	 */
	function _rebase() internal {
		IStrategy strategy;
		collateralStruct memory collateral;
		uint newTokensAmt;
		uint USDsSupply = USDsInstance._totalSupply();
		uint USDsSupplyIncrement;
		uint USDsSupplyIncrementTotal;
		for (uint y = 0; y < allCollaterals.length; y++) {
			collateral = allCollaterals[y];
			strategy = IStrategy(collateral.defaultStrategyAddr);
			newTokensAmt = strategy.checkInterestEarned(collateral.collateralAddr);
			if (newTokensAmt > 0) {
				if (collateral.rebaseMethod == 0) {
					(uint SPABurnAmt, , uint USDsAmt, uint swapFeeAmount) = VaultCoreLibrary.mintView(collateral.collateralAddr, newTokensAmt, 2, address(this));
					ISperaxToken(SPAaddr).burnFrom(SPAvault, SPABurnAmt);
					USDsSupplyIncrement = USDsSupply.add(USDsAmt).add(swapFeeAmount);
					USDsSupplyIncrementTotal = USDsSupplyIncrementTotal.add(USDsSupplyIncrement);
				}
				else if (collateral.rebaseMethod == 1) {
					strategy.withdraw(address(this), collateral.collateralAddr, newTokensAmt);
					//TODO: What if not 1 to 1 redeem
					BuybackInstance.swap(newTokensAmt);
				}
			}
			USDsInstance.changeSupply(USDsSupplyIncrementTotal);
			emit Rebase(USDsSupply, USDsSupplyIncrementTotal);
		}
	}
	//
	// /**
	//  * @dev  _precision: same as chi (chi_prec)
	//  */
	//
	function collateralRatio() public view returns (uint ratio) {
    uint totalValueLocked = _totalValueLocked();
		uint USDsSupply =  USDsInstance.totalSupply();
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).getUSDsPrice_prec();
		uint USDsValue = USDsSupply.mul(priceUSDs).div(precisionUSDs);
		ratio = totalValueLocked.mul(chi_prec).div(USDsValue);
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
		//address collateralAddr;
		collateralStruct memory collateral;
		uint priceColla = 0;
		uint precisionColla = 0;
		uint collateralAddrDecimal = 0;
		uint collaTotalValueInVault = 0;
		uint collaTotalValueInVault_18 = 0;
		for (uint y = 0; y < allCollaterals.length; y++) {
			collateral = allCollaterals[y];
			priceColla = IOracle(oracleAddr).getCollateralPrice(collateral.collateralAddr);
			precisionColla = IOracle(oracleAddr).getCollateralPrice_prec(collateral.collateralAddr);
			collateralAddrDecimal = uint(ERC20Upgradeable(collateral.collateralAddr).decimals());
			collaTotalValueInVault = ERC20Upgradeable(collateral.collateralAddr).balanceOf(address(this)).mul(priceColla).div(precisionColla);
			collaTotalValueInVault_18 = collaTotalValueInVault.mul(10**(uint(18).sub(collateralAddrDecimal)));
			value = value.add(collaTotalValueInVault_18);
		}
	}

	function totalValueInStrategies() external view returns (uint value) {
		value = _totalValueInStrategies();
	}

	function _totalValueInStrategies() internal view returns (uint value) {
		for (uint i = 0; i < allStrategies.length; i++) {
			if (allStrategies[i].enabled) {
				value = value.add(_totalValueInStrategy(allStrategies[i].strategyAddr));
			}
		}
	}

	function _totalValueInStrategy(address _strategyAddr) internal view returns (uint value) {
		IStrategy strategy = IStrategy(_strategyAddr);
		collateralStruct memory collateral;
		uint priceColla = 0;
		uint precisionColla = 0;
		uint collateralAddrDecimal = 0;
		uint collaTotalValueInStrategy = 0;
		uint collaTotalValueInStrategy_18 = 0;
		for (uint y = 0; y < allCollaterals.length; y++) {
			collateral = allCollaterals[y];
			if (strategy.supportsCollateral(collateral.collateralAddr)) {
				priceColla = IOracle(oracleAddr).getCollateralPrice(collateral.collateralAddr);
				precisionColla = IOracle(oracleAddr).getCollateralPrice_prec(collateral.collateralAddr);
				collateralAddrDecimal = uint(ERC20Upgradeable(collateral.collateralAddr).decimals());
				collaTotalValueInStrategy = strategy.checkBalance(collateral.collateralAddr).mul(priceColla).div(precisionColla);
				collaTotalValueInStrategy_18 = collaTotalValueInStrategy.mul(10**(uint(18).sub(collateralAddrDecimal)));
				value = value.add(collaTotalValueInStrategy_18);
			}
		}
	}

	/**
		* @notice Allocate unallocated funds on Vault to strategies.
		* @dev Allocate unallocated funds on Vault to strategies.
		**/
	function allocateAll() external whenAllocationAllowed onlyOwner {
		for (uint i = 0; i < allCollaterals.length; i++) {
			collateralStruct memory collateral = allCollaterals[i];
			if (collateral.supported && collateral.allocationAllowed) {
				_allocate(collateral.collateralAddr);
			}
		}
	}

	function allocate(address _collateralAddr) external whenAllocationAllowed onlyOwner {
		collateralStruct memory collateral = collateralsInfo[_collateralAddr];
		if (collateral.supported && collateral.allocationAllowed) {
			_allocate(collateral.collateralAddr);
		}
	}

	function allocate(address _collateralAddr, uint amtToAllocate) external whenAllocationAllowed onlyOwner {
		collateralStruct memory collateral = collateralsInfo[_collateralAddr];
		if (collateral.supported && collateral.allocationAllowed) {
			_allocate(collateral.collateralAddr, amtToAllocate);
		}

	}

	/**
	* @notice Allocate unallocated funds on Vault to strategies.
	* @dev Allocate unallocated funds on Vault to strategies.
	**/
	function _allocate(address _collateralAddr) internal {
		collateralStruct memory collateral = collateralsInfo[_collateralAddr];
		require(collateral.supported, "_allocate: Collateral not supported. ");
		require(collateral.defaultStrategyAddr != address(0), "_allocate: Strategy not set. ");
		require(collateral.allocationAllowed, "_allocate: Allocation not allowed. ");
		IStrategy strategyInstance = IStrategy(collateralsInfo[_collateralAddr].defaultStrategyAddr);
		strategyStruct memory strategy = strategiesInfo[collateralsInfo[_collateralAddr].defaultStrategyAddr];
		require(strategy.strategyAddr != address(0), "_allocate: Strategy not set. ");
		require(strategy.enabled, "_allocate: Strategy not enabled. ");
		uint amtInVault = ERC20Upgradeable(_collateralAddr).balanceOf(address(this));
		uint amtInStrategy = strategyInstance.checkBalance(_collateralAddr);
		uint amtTotal = amtInVault.add(amtInStrategy);
		(, uint amtToAllocate) = amtTotal.mul(allocatePrecentage).div(allocatePrecentage_prec).trySub(amtInStrategy);
		if (amtToAllocate > 0) {
			ERC20Upgradeable(_collateralAddr).safeTransfer(collateral.defaultStrategyAddr, amtToAllocate);
			strategyInstance.deposit(_collateralAddr, amtToAllocate);
		}
	}

	/**
	* @notice Allocate unallocated funds on Vault to strategies.
	* @dev Allocate unallocated funds on Vault to strategies.
	**/
	function _allocate(address _collateralAddr, uint amtToAllocate) internal {
		collateralStruct memory collateral = collateralsInfo[_collateralAddr];
		require(collateral.supported, "_allocate: Collateral not supported. ");
		require(collateral.defaultStrategyAddr != address(0), "_allocate: Strategy not set. ");
		require(collateral.allocationAllowed, "_allocate: Allocation not allowed. ");
		IStrategy strategyInstance = IStrategy(collateralsInfo[_collateralAddr].defaultStrategyAddr);
		strategyStruct memory strategy = strategiesInfo[collateralsInfo[_collateralAddr].defaultStrategyAddr];
		require(strategy.strategyAddr != address(0), "_allocate: Strategy not set. ");
		require(strategy.enabled, "_allocate: Strategy not enabled. ");
		require(amtToAllocate > 0, "_allocate: amtToAllocate should be positive. ");
		ERC20Upgradeable(_collateralAddr).safeTransfer(collateral.defaultStrategyAddr, amtToAllocate);
		strategyInstance.deposit(_collateralAddr, amtToAllocate);
	}

}
