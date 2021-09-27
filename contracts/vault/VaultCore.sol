//TO-DO: check source file of SafeMathUpgradeable regarding trySub() (and the usage of "unchecked")
//TO-DO: check ERC20Upgradeable vs ERC20Upgradeable
// Note: assuming when exponentWith_prec >= 2^32, toReturn >= swapFee_prec () (TO-DO: work out the number)
//TO-DO: deal with collateralStrategies
//TO-DO: what happen when we redeem aTokens
//TO-DO: whether _redeem needs "SafeTransferFrom" and how
//TO-DO: check all user inputs, especially mintView
//TO-DO: remove for testing purposes files
pragma solidity ^0.6.12;

//import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
//import "https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/v3.4.0/contracts/access/OwnableUpgradeable.sol";
import "../libraries/openzeppelin/OwnableUpgradeable.sol";
//import "@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";
//import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";

import "../libraries/Helpers.sol";
//import "../interfaces/IOracle.sol";
import "../interfaces/ISperaxToken.sol";
import "../interfaces/IStrategy.sol";
import "../libraries/VaultCoreLibrary.sol";
import "../token/USDs.sol";
//import "../libraries/BancorFormula.sol";
import "../interfaces/IBuyback.sol";
import "../interfaces/IVaultCore.sol";

contract VaultCore is Initializable, OwnableUpgradeable, IVaultCore {
	using SafeERC20Upgradeable for ERC20Upgradeable;
	using SafeMathUpgradeable for uint;
	using StableMath for uint;

	bool public override mintRedeemAllowed;
	bool public override allocationAllowed;
	bool public override rebaseAllowed;
	bool public override swapfeeInAllowed;
	bool public override swapfeeOutAllowed;
	address public SPAaddr;
	address public override oracleAddr;
	address public SPAvault;
	USDs USDsInstance;
	BancorFormula public override BancorInstance;
	uint public override startBlockHeight;
	uint public SPAminted;
	uint public SPAburnt;
	uint32 public override chi_alpha;
	uint64 public override constant chi_alpha_prec = 10**12;
	uint64 public override constant chi_prec = 10**12;
	uint64 public override chiInit;
	uint32 public override chi_beta;
	uint16 public override constant chi_beta_prec = 10**4;
	uint32 public override chi_gamma;
	uint16 public override constant chi_gamma_prec = 10**4;
	uint64 public override constant swapFee_prec = 10**12;
	uint32 public override swapFee_p;
	uint16 public override constant swapFee_p_prec = 10**4;
	uint32 public override swapFee_theta;
	uint16 public override constant swapFee_theta_prec = 10**4;
	uint32 public override swapFee_a;
	uint16 public override constant swapFee_a_prec = 10**4;
	uint32 public override swapFee_A;
	uint16 public override constant swapFee_A_prec = 10**4;
	uint32 public override allocatePrecentage;
	uint16 public override constant allocatePrecentage_prec = 10**4;

	event parametersUpdated(uint64 _chiInit, uint32 _chi_beta, uint32 _chi_gamma, uint32 _swapFee_p, uint32 _swapFee_theta, uint32 _swapFee_a, uint32 _swapFee_A, uint32 _allocatePrecentage);
	event USDsMinted(address indexed wallet, uint indexed USDsAmt, uint collateralAmt, uint SPAsAmt, uint feeAmt);
	event USDsRedeemed(address indexed wallet, uint indexed USDsAmt, uint collateralAmt, uint SPAsAmt, uint feeAmt);
	event Rebase(uint indexed oldSupply, uint indexed newSupply);
	event CollateralInfoChanged(address indexed collateralAddr, bool supported, address defaultStrategyAddr, bool allocationAllowed, address buyBackAddr, bool rebaseAllowed);
	event StrategyInfoChanged(address strategyAddr, bool enabled);
	event MintRedeemPermssionChanged(bool indexed permission);
	event AllocationPermssionChanged(bool indexed permission);
	event SwapFeeInOutPermissionChanged(bool indexed swapfeeInAllowed, bool indexed swapfeeOutAllowed);

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
		address buyBackAddr;
		bool rebaseAllowed;
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

	function initialize() public initializer {
		OwnableUpgradeable.__Ownable_init();
		mintRedeemAllowed = true;
		swapfeeInAllowed = false;
		swapfeeOutAllowed = false;
		allocationAllowed = false;
		SPAaddr = 0xbb5E27Ae27A6a7D092b181FbDdAc1A1004e9adff;	// SPA on Kovan
		SPAvault = address(this);
		startBlockHeight = block.number;
		BancorInstance = BancorFormula(0x0f27662A7e4033eB4549a4E6Bd42a35a96979BdC);
		chi_alpha = uint32(chi_alpha_prec * 513 / 10**10);
		chiInit = chi_prec * 95 / 100;
		chi_beta = chi_beta_prec * 9;
		chi_gamma = chi_gamma_prec;
		swapFee_p = swapFee_p_prec * 99 / 100;
		swapFee_theta = swapFee_theta_prec * 50;
		swapFee_a = swapFee_a_prec * 12 / 10;
		swapFee_A = swapFee_A_prec * 20;
		allocatePrecentage = allocatePrecentage_prec * 8 / 10;
	}

	//For testing purposes:
	function updateUSDsAddress(address _USDsAddr) external onlyOwner {
		USDsInstance = USDs(_USDsAddr);
	}

	function updateOracleAddress(address _oracleAddr) external onlyOwner {
		oracleAddr =  _oracleAddr;
	}

	function updateParameters(uint64 _chiInit, uint32 _chi_beta, uint32 _chi_gamma, uint32 _swapFee_p, uint32 _swapFee_theta, uint32 _swapFee_a, uint32 _swapFee_A, uint32 _allocatePrecentage) external onlyOwner {
		chiInit = _chiInit;
		chi_beta = _chi_beta;
		chi_gamma = _chi_gamma;
		swapFee_p = _swapFee_p;
		swapFee_theta = _swapFee_theta;
		swapFee_a = _swapFee_a;
		swapFee_A = _swapFee_A;
		allocatePrecentage = _allocatePrecentage;
		emit parametersUpdated(chiInit, chi_beta, chi_gamma, swapFee_p, swapFee_theta, swapFee_a, swapFee_A, allocatePrecentage);
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
	function updateSwapInOutFeePermission(bool _swapfeeInAllowed, bool _swapfeeOutAllowed) external onlyOwner {
		swapfeeInAllowed = _swapfeeInAllowed;
		swapfeeOutAllowed = _swapfeeOutAllowed;
		emit SwapFeeInOutPermissionChanged(swapfeeInAllowed, swapfeeOutAllowed);
	}

	function updateCollateralInfo(address _collateralAddr, bool _supported, address _defaultStrategyAddr, bool _allocationAllowed, address _buyBackAddr, bool _rebaseAllowed) external onlyOwner {
		_updateCollateralInfo(_collateralAddr, _supported, _defaultStrategyAddr, _allocationAllowed, _buyBackAddr, _rebaseAllowed);
	}

	function _updateCollateralInfo(address _collateralAddr, bool _supported, address _defaultStrategyAddr, bool _allocationAllowed, address _buyBackAddr, bool _rebaseAllowed) internal {
		collateralStruct storage updatedCollateral = collateralsInfo[_collateralAddr];
		updatedCollateral.collateralAddr = _collateralAddr;
		updatedCollateral.supported = _supported;
		updatedCollateral.defaultStrategyAddr = _defaultStrategyAddr;
		updatedCollateral.allocationAllowed = _allocationAllowed;
		updatedCollateral.buyBackAddr = _buyBackAddr;
		emit CollateralInfoChanged(_collateralAddr, _supported, _defaultStrategyAddr, _allocationAllowed, _buyBackAddr, _rebaseAllowed);
	}

	function updateStrategyInfo(address _strategyAddr, bool _enabled) external onlyOwner {
		_updateStrategyInfo(_strategyAddr, _enabled);
	}

	function _updateStrategyInfo(address _strategyAddr, bool _enabled) internal {
		strategyStruct storage updatedStrategy = strategiesInfo[_strategyAddr];
		updatedStrategy.strategyAddr = _strategyAddr;
		updatedStrategy.enabled = _enabled;
		emit StrategyInfoChanged(_strategyAddr, _enabled);
	}

	/**
	 * @dev mint USDs by entering USDs amount
	 * @param collateralAddr the address of user's chosen collateral
	 * @param USDsMintAmt the amount of USDs to be minted
	 */
	function mintWithUSDs(address collateralAddr, uint USDsMintAmt, uint slippageCollateral, uint slippageSPA, uint deadline)
		public
		whenMintRedeemAllowed
	{
		require(collateralsInfo[collateralAddr].supported, "Collateral not supported");
		require(USDsMintAmt > 0, "Amount needs to be greater than 0");
		_mint(collateralAddr, USDsMintAmt, 0, USDsMintAmt, slippageCollateral, slippageSPA, deadline);
	}

	/**
	 * @dev mint USDs by entering SPA amount
	 * @param collateralAddr the address of user's chosen collateral
	 * @param SPAamt the amount of SPA to burn
	 */

	function mintWithSPA(address collateralAddr, uint SPAamt, uint slippageUSDs, uint slippageCollateral, uint deadline)
		public
		whenMintRedeemAllowed
	{
		require(collateralsInfo[collateralAddr].supported, "Collateral not supported");
		require(SPAamt > 0, "Amount needs to be greater than 0");
		_mint(collateralAddr, SPAamt, 1, slippageUSDs, slippageCollateral, SPAamt, deadline);
	}

	/**
	 * @dev mint USDs by entering collateral amount (excluding ETH)
	 * @param collateralAddr the address of user's chosen collateral
	 * @param collateralAmt the amount of collateral to stake
	 */
	function mintWithColla(address collateralAddr, uint collateralAmt, uint slippageUSDs, uint slippageSPA, uint deadline)
		public
		whenMintRedeemAllowed
	{
		require(collateralsInfo[collateralAddr].supported, "Collateral not supported");
		require(collateralAmt > 0, "Amount needs to be greater than 0");
		_mint(collateralAddr, collateralAmt, 2, slippageUSDs, collateralAmt, slippageSPA, deadline);
	}

	/**
	 * @dev mint USDs by ETH
	 * note: this function needs changes when USDs is deployed on other blockchain platform
	 */
	function mintWithEth(uint slippageUSDs, uint slippageSPA, uint deadline) public payable whenMintRedeemAllowed {
		require(msg.value > 0, "Need to pay Ether");
		_mint(address(0), msg.value, 3, slippageUSDs, msg.value, slippageSPA, deadline);
	}


	/**
	 * @dev the generic, internal mint function
	 * @param collateralAddr the address of the collateral
	 * @param valueAmt the amount of tokens (the specific meaning depends on valueType)
	 * @param valueType the type of tokens (specific meanings are listed lower)
	 *		valueType = 0: mintWithUSDs
	 *		valueType = 1: mintWithSPA
	 *		valueType = 2: mintWithColla
	 *		valueType = 3: mintWithETH
	 */
	function _mint(
		address collateralAddr,
		uint valueAmt,
		uint8 valueType,
		uint slippageUSDs,
		uint slippageCollat,
		uint slippageSPA,
		uint deadline
	) internal whenMintRedeemAllowed {
		// calculate all necessary related quantities based on user inputs
		(uint SPABurnAmt, uint collateralDepAmt, uint USDsAmt, uint swapFeeAmount) = VaultCoreLibrary.mintView(collateralAddr, valueAmt, valueType, address(this));

		// slippageUSDs is the minimum value of the minted USDs
		// slippageCollat is the maximum value of the required collateral
		// slippageSPA is the maximum value of the required spa
		require(USDsAmt >= slippageUSDs, "USDs amount is lower than the maximum slippage");
		require(collateralDepAmt <= slippageCollat, "Collateral amount is more than the maximum slippage");
		require(SPABurnAmt >= slippageSPA, "SPA amount is more than the maximum slippage");
		require(block.timestamp <= deadline, "Deadline expired");

		// burn SPA tokens
		ISperaxToken(SPAaddr).burnFrom(msg.sender, SPABurnAmt);
		SPAburnt = SPAburnt.add(SPABurnAmt);
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
	function redeem(address collateralAddr, uint USDsAmt, uint slippageCollat, uint slippageSPA, uint deadline)
		public
		whenMintRedeemAllowed
	{
		require(collateralsInfo[collateralAddr].supported, "Collateral not supported");
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_redeem(collateralAddr, USDsAmt, slippageCollat, slippageSPA, deadline);
	}

	/**
	 *
	 */
	function redeemWithEth(uint USDsAmt, uint slippageEth, uint slippageSPA, uint deadline)
		public
		whenMintRedeemAllowed
	{
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_redeem(address(0), USDsAmt, slippageEth, slippageSPA, deadline);
	}

	function _redeem(
		address collateralAddr,
		uint USDsAmt,
		uint slippageCollat,
		uint slippageSPA,
		uint deadline
	) internal whenMintRedeemAllowed {
		(uint SPAMintAmt, uint collateralUnlockedAmt, uint USDsBurntAmt, uint swapFeeAmount) = VaultCoreLibrary.redeemView(collateralAddr, USDsAmt, address(this), oracleAddr);

		// slippageCollat is the minimum value of the unlocked collateral
		// slippageSPA is the minimum value of the minted spa
		require(collateralUnlockedAmt >= slippageCollat, "Collateral amount is lower than the maximum slippage");
		require(SPAMintAmt >= slippageSPA, "SPA amount is lower than the maximum slippage");
		require(block.timestamp <= deadline, "Deadline expired");

		ISperaxToken(SPAaddr).mintForUSDs(msg.sender, SPAMintAmt);
		SPAminted = SPAminted.add(SPAMintAmt);

		if (collateralAddr == address(0)) {
			(bool sent, ) = msg.sender.call{value: collateralUnlockedAmt}("");
			require(sent, "Failed to send Ether");
		} else {
			ERC20Upgradeable(collateralAddr).safeTransfer(msg.sender, collateralUnlockedAmt);
		}
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
		uint USDsSupplyIncrementTotal;
		uint USDsReceived;
		for (uint y = 0; y < allCollaterals.length; y++) {
			collateral = allCollaterals[y];
			strategy = IStrategy(collateral.defaultStrategyAddr);
			newTokensAmt = strategy.checkInterestEarned(collateral.collateralAddr);
			if (newTokensAmt > 0 && collateral.rebaseAllowed) {
				strategy.withdraw(address(this), collateral.collateralAddr, newTokensAmt);
				USDsReceived = IBuyback(collateral.buyBackAddr).swapExactInputSingle(newTokensAmt);
				USDsInstance.burn(address(this), USDsReceived);
				USDsSupplyIncrementTotal = USDsSupplyIncrementTotal.add(USDsReceived);
			}
		}
		uint USDsNewSupply = USDsSupply.add(USDsSupplyIncrementTotal);
		USDsInstance.changeSupply(USDsNewSupply);
		emit Rebase(USDsSupply, USDsNewSupply);
	}
	//
	// /**
	//  * @dev  _precision: same as chi (chi_prec)
	//  */
	//
	function collateralRatio() public view override returns (uint ratio) {
		uint totalValueLocked = _totalValueLocked();
		uint USDsSupply = USDsInstance.totalSupply();
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
		for (uint y = 0; y < allCollaterals.length; y++) {
			collateralStruct memory collateral = allCollaterals[y];
			uint priceColla = IOracle(oracleAddr).getCollateralPrice(collateral.collateralAddr);
			uint precisionColla = IOracle(oracleAddr).getCollateralPrice_prec(collateral.collateralAddr);
			uint collateralAddrDecimal = uint(ERC20Upgradeable(collateral.collateralAddr).decimals());
			uint collaTotalValueInVault = ERC20Upgradeable(collateral.collateralAddr).balanceOf(address(this)).mul(priceColla).div(precisionColla);
			uint collaTotalValueInVault_18 = collaTotalValueInVault.mul(10**(uint(18).sub(collateralAddrDecimal)));
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
		for (uint y = 0; y < allCollaterals.length; y++) {
			collateralStruct memory collateral = allCollaterals[y];
			if (strategy.supportsCollateral(collateral.collateralAddr)) {
				uint priceColla = IOracle(oracleAddr).getCollateralPrice(collateral.collateralAddr);
				uint precisionColla = IOracle(oracleAddr).getCollateralPrice_prec(collateral.collateralAddr);
				uint collateralAddrDecimal = uint(ERC20Upgradeable(collateral.collateralAddr).decimals());
				uint collaTotalValueInStrategy = strategy.checkBalance(collateral.collateralAddr).mul(priceColla).div(precisionColla);
				uint collaTotalValueInStrategy_18 = collaTotalValueInStrategy.mul(10**(uint(18).sub(collateralAddrDecimal)));
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
				IStrategy strategyInstance = IStrategy(collateral.defaultStrategyAddr);
				uint amtInVault = ERC20Upgradeable(collateral.collateralAddr).balanceOf(address(this));
				uint amtInStrategy = strategyInstance.checkBalance(collateral.collateralAddr);
				uint amtTotal = amtInVault.add(amtInStrategy);
				(, uint amtToAllocate) = amtTotal.mul(allocatePrecentage).div(allocatePrecentage_prec).trySub(amtInStrategy);
				if (amtToAllocate > 0) {
					_allocate(collateral.collateralAddr, amtToAllocate);
				}
			}
		}
	}

	function allocate(address _collateralAddr, uint amtToAllocate) external whenAllocationAllowed onlyOwner {
		_allocate(_collateralAddr, amtToAllocate);
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
