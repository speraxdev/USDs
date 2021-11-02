// SPDX-License-Identifier: MIT
pragma solidity >=0.6.12;
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "../interfaces/ISperaxToken.sol";
import "../interfaces/IStrategy.sol";
import "../interfaces/IVaultCore.sol";
import "../interfaces/IUSDs.sol";
import "../interfaces/IBuyback.sol";
import "./VaultCoreTools.sol";

contract VaultCore is Initializable, OwnableUpgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable, IVaultCore {
	using SafeERC20Upgradeable for IERC20Upgradeable;
	using SafeMathUpgradeable for uint;
	using StableMath for uint;

	bytes32 public constant REBASER_ROLE = keccak256("REBASER_ROLE");

	bool public override mintRedeemAllowed;
	bool public override allocationAllowed;
	bool public override rebaseAllowed;
	bool public override swapfeeInAllowed;
	bool public override swapfeeOutAllowed;
	address public SPAaddr;
	address public USDsAddr;
	address public override oracleAddr;
	address public SPAvault;
	address public feeVault;
	address public vaultCoreToolsAddr;
	uint public override startBlockHeight;
	uint public SPAminted;
	uint public SPAburnt;
	uint32 public override chi_alpha;
	uint64 public override constant chi_alpha_prec = 10**12;
	uint64 public override constant chi_prec = chi_alpha_prec;
	uint public override chiInit;
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
	uint8 public override constant allocatePercentage_prec = 10**2;

	event parametersUpdated(uint _chiInit, uint32 _chi_beta, uint32 _chi_gamma, uint32 _swapFee_p, uint32 _swapFee_theta, uint32 _swapFee_a, uint32 _swapFee_A);
	event USDsMinted(address indexed wallet, uint indexed USDsAmt, uint collateralAmt, uint SPAsAmt, uint feeAmt);
	event USDsRedeemed(address indexed wallet, uint indexed USDsAmt, uint collateralAmt, uint SPAsAmt, uint feeAmt);
	event Rebase(uint indexed oldSupply, uint indexed newSupply);
	event CollateralAdded(address indexed collateralAddr, bool addded, address defaultStrategyAddr, bool allocationAllowed, uint8 allocatePercentage, address buyBackAddr, bool rebaseAllowed);
	event CollateralChanged(address indexed collateralAddr, bool addded, address defaultStrategyAddr, bool allocationAllowed, uint8 allocatePercentage, address buyBackAddr, bool rebaseAllowed);
	event StrategyAdded(address strategyAddr, bool added);
	event MintRedeemPermssionChanged(bool indexed permission);
	event AllocationPermssionChanged(bool indexed permission);
	event SwapFeeInOutPermissionChanged(bool indexed swapfeeInAllowed, bool indexed swapfeeOutAllowed);
	event CollateralAllocated(address indexed collateralAddr, address indexed depositStrategyAddr, uint allocateAmount);

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
		bool added;
		address defaultStrategyAddr;
		bool allocationAllowed;
		uint8 allocatePercentage;
		address buyBackAddr;
		bool rebaseAllowed;
	}
	struct strategyStruct {
		address strategyAddr;
		bool added;
	}
	mapping(address => collateralStruct) collateralsInfo;
	mapping(address => strategyStruct) strategiesInfo;
	collateralStruct[] allCollaterals;	// the list of all added collaterals
	strategyStruct[] allStrategies;	// the list of all strategy addresses

	function initialize(address _SPAaddr, address _vaultCoreToolsAddr, address _feeVault) public initializer {
		OwnableUpgradeable.__Ownable_init();
		AccessControlUpgradeable.__AccessControl_init();
		ReentrancyGuardUpgradeable.__ReentrancyGuard_init();
		mintRedeemAllowed = true;
		swapfeeInAllowed = false;
		swapfeeOutAllowed = false;
		allocationAllowed = false;
		SPAaddr = _SPAaddr;
		vaultCoreToolsAddr = _vaultCoreToolsAddr;
		SPAvault = address(this);
		startBlockHeight = block.number;
		chi_alpha = uint32(chi_alpha_prec * 158 / 10**10);
		chiInit = uint(chi_prec * 95 / 100);
		chi_beta = chi_beta_prec * 9;
		chi_gamma = chi_gamma_prec;
		swapFee_p = swapFee_p_prec * 99 / 100;
		swapFee_theta = swapFee_theta_prec * 50;
		swapFee_a = swapFee_a_prec * 12 / 10;
		swapFee_A = swapFee_A_prec * 20;
		feeVault = _feeVault;
		_setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
	}

	//for testing purpose
	function updateUSDsAddress(address _USDsAddr) external onlyOwner {
		USDsAddr = _USDsAddr;
	}

	function updateOracleAddress(address _oracleAddr) external onlyOwner {
		oracleAddr =  _oracleAddr;
	}

	function updateParameters(uint _chiInit, uint32 _chi_beta, uint32 _chi_gamma, uint32 _swapFee_p, uint32 _swapFee_theta, uint32 _swapFee_a, uint32 _swapFee_A) external onlyOwner {
		chiInit = _chiInit;
		chi_beta = _chi_beta;
		chi_gamma = _chi_gamma;
		swapFee_p = _swapFee_p;
		swapFee_theta = _swapFee_theta;
		swapFee_a = _swapFee_a;
		swapFee_A = _swapFee_A;
		emit parametersUpdated(chiInit, chi_beta, chi_gamma, swapFee_p, swapFee_theta, swapFee_a, swapFee_A);
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

	function addCollateral(address _collateralAddr, address _defaultStrategyAddr, bool _allocationAllowed, uint8 _allocatePercentage, address _buyBackAddr, bool _rebaseAllowed) external onlyOwner {
		require(!collateralsInfo[_collateralAddr].added, "Collateral added");
		require(ERC20Upgradeable(_collateralAddr).decimals() <= 18, "Collaterals decimals need to be less than 18");
		collateralStruct storage addingCollateral = collateralsInfo[_collateralAddr];
		addingCollateral.collateralAddr = _collateralAddr;
		addingCollateral.added = true;
		addingCollateral.defaultStrategyAddr = _defaultStrategyAddr;
		addingCollateral.allocationAllowed = _allocationAllowed;
		addingCollateral.allocatePercentage = _allocatePercentage;
		addingCollateral.buyBackAddr = _buyBackAddr;
		addingCollateral.rebaseAllowed = _rebaseAllowed;
		allCollaterals.push(addingCollateral);
		emit CollateralAdded(_collateralAddr, addingCollateral.added, _defaultStrategyAddr, _allocationAllowed, _allocatePercentage, _buyBackAddr, _rebaseAllowed);
	}

	function updateCollateralInfo(address _collateralAddr, address _defaultStrategyAddr, bool _allocationAllowed, uint8 _allocatePercentage, address _buyBackAddr, bool _rebaseAllowed) external onlyOwner {
		require(collateralsInfo[_collateralAddr].added, "Collateral not added");
		collateralStruct storage updatedCollateral = collateralsInfo[_collateralAddr];
		updatedCollateral.collateralAddr = _collateralAddr;
		updatedCollateral.defaultStrategyAddr = _defaultStrategyAddr;
		updatedCollateral.allocationAllowed = _allocationAllowed;
		updatedCollateral.buyBackAddr = _buyBackAddr;
		emit CollateralChanged(_collateralAddr, updatedCollateral.added, _defaultStrategyAddr, _allocationAllowed, _allocatePercentage, _buyBackAddr, _rebaseAllowed);
	}

	function addStrategy(address _strategyAddr) external onlyOwner {
		require(!strategiesInfo[_strategyAddr].added, "Strategy added");
		strategyStruct storage addingStrategy = strategiesInfo[_strategyAddr];
		addingStrategy.strategyAddr = _strategyAddr;
		addingStrategy.added = true;
		allStrategies.push(addingStrategy);
		emit StrategyAdded(_strategyAddr, true);
	}

	/**
	 * @dev mint USDs by entering USDs amount
	 * @param collateralAddr the address of user's chosen collateral
	 * @param USDsMintAmt the amount of USDs to be minted
	 */
	function mintWithUSDs(address collateralAddr, uint USDsMintAmt, uint slippageCollateral, uint slippageSPA, uint deadline)
		public
		whenMintRedeemAllowed
		nonReentrant
	{
		require(collateralsInfo[collateralAddr].added, "Collateral not added");
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
		nonReentrant
	{
		require(collateralsInfo[collateralAddr].added, "Collateral not added");
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
		nonReentrant
	{
		require(collateralsInfo[collateralAddr].added, "Collateral not added");
		require(collateralAmt > 0, "Amount needs to be greater than 0");
		_mint(collateralAddr, collateralAmt, 2, slippageUSDs, collateralAmt, slippageSPA, deadline);
	}

	/**
	 * @dev mint USDs by ETH
	 * note: this function needs changes when USDs is deployed on other blockchain platform
	 */
	function mintWithEth(uint slippageUSDs, uint slippageSPA, uint deadline) public payable whenMintRedeemAllowed nonReentrant {
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
		(uint SPABurnAmt, uint collateralDepAmt, uint USDsAmt, uint swapFeeAmount) = VaultCoreTools(vaultCoreToolsAddr).mintView(collateralAddr, valueAmt, valueType, address(this));

		// slippageUSDs is the minimum value of the minted USDs
		// slippageCollat is the maximum value of the required collateral
		// slippageSPA is the maximum value of the required spa
		require(USDsAmt >= slippageUSDs, "USDs amount is lower than the maximum slippage");
		require(collateralDepAmt <= slippageCollat, "Collateral amount is more than the maximum slippage");
		require(SPABurnAmt <= slippageSPA, "SPA amount is more than the maximum slippage");
		require(block.timestamp <= deadline, "Deadline expired");

		// burn SPA tokens
		ISperaxToken(SPAaddr).burnFrom(msg.sender, SPABurnAmt);
		SPAburnt = SPAburnt.add(SPABurnAmt);
		// if it it not mintWithETH, stake collaterals
		if (valueType != 3) {
			IERC20Upgradeable(collateralAddr).safeTransferFrom(msg.sender, address(this), collateralDepAmt);
		}
		// mint USDs and collect swapIn fees
		IUSDs(USDsAddr).mint(msg.sender, USDsAmt);
		IUSDs(USDsAddr).mint(feeVault, swapFeeAmount);
		emit USDsMinted(msg.sender, USDsAmt, collateralDepAmt, SPABurnAmt, swapFeeAmount);
	}

	/**
	 *
	 */
	function redeem(address collateralAddr, uint USDsAmt, uint slippageCollat, uint slippageSPA, uint deadline)
		public
		whenMintRedeemAllowed
		nonReentrant
	{
		require(collateralsInfo[collateralAddr].added, "Collateral not added");
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_redeem(collateralAddr, USDsAmt, slippageCollat, slippageSPA, deadline);
	}

	/**
	 *
	 */
	function redeemWithEth(uint USDsAmt, uint slippageEth, uint slippageSPA, uint deadline)
		public
		whenMintRedeemAllowed
		nonReentrant
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
		(uint SPAMintAmt, uint collateralUnlockedAmt, uint USDsBurntAmt, uint swapFeeAmount) = VaultCoreTools(vaultCoreToolsAddr).redeemView(collateralAddr, USDsAmt, address(this), oracleAddr);
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
			IERC20Upgradeable(collateralAddr).safeTransfer(msg.sender, collateralUnlockedAmt);
		}
		IUSDs(USDsAddr).burn(msg.sender, USDsBurntAmt);
		IERC20Upgradeable(USDsAddr).safeTransferFrom(msg.sender, feeVault, swapFeeAmount);

		emit USDsRedeemed(msg.sender, USDsBurntAmt, collateralUnlockedAmt,SPAMintAmt, swapFeeAmount);
	}

	function collateralRatio() public view override returns (uint ratio) {
		uint totalValueLocked = totalValueLocked();
		uint USDsSupply = IERC20Upgradeable(USDsAddr).totalSupply();
		uint priceUSDs = uint(IOracle(oracleAddr).getUSDsPrice());
		uint precisionUSDs = IOracle(oracleAddr).getUSDsPrice_prec();
		uint USDsValue = USDsSupply.mul(priceUSDs).div(precisionUSDs);
		ratio = totalValueLocked.mul(chi_prec).div(USDsValue);
	}

	function totalValueLocked() public view returns (uint value) {
		//value = totalValueInVault().add(totalValueInStrategies());
		value = totalValueInVault();
	}

	function totalValueInVault() public view returns (uint value) {
		for (uint y = 0; y < allCollaterals.length; y++) {
			collateralStruct memory collateral = allCollaterals[y];
			value = value.add(_valueInVault(collateral.collateralAddr));
		}
	}

	function _valueInVault(address _collateralAddr) internal view returns (uint value) {
		collateralStruct memory collateral = collateralsInfo[_collateralAddr];
		uint priceColla = IOracle(oracleAddr).getCollateralPrice(collateral.collateralAddr);
		uint precisionColla = IOracle(oracleAddr).getCollateralPrice_prec(collateral.collateralAddr);
		uint collateralAddrDecimal = uint(ERC20Upgradeable(collateral.collateralAddr).decimals());
		uint collateralTotalValueInVault = IERC20Upgradeable(collateral.collateralAddr).balanceOf(address(this)).mul(priceColla).div(precisionColla);
		uint collateralTotalValueInVault_18 = collateralTotalValueInVault.mul(10**(uint(18).sub(collateralAddrDecimal)));
		value = collateralTotalValueInVault_18;
	}
}
