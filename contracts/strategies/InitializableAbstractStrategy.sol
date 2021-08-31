pragma solidity ^0.6.12;


import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";

import "./IAave.sol";


abstract contract InitializableAbstractStrategy is Initializable, OwnableUpgradeable {
    using SafeERC20Upgradeable for ERC20Upgradeable;
    using SafeMathUpgradeable for uint;

    event PTokenAdded(address indexed _collateral, address _pToken);
    event PTokenRemoved(address indexed _collateral, address _pToken);
    event Deposit(address indexed _collateral, address _pToken, uint256 _amount);
    event Withdrawal(address indexed _collateral, address _pToken, uint256 _amount);
    event RewardTokenCollected(address recipient, uint256 amount);

    // Core address for the given platform
    address public platformAddress;

    address public vaultAddress;

    // collateral => pToken (Platform Specific Token Address)
    mapping(address => address) public collateralToPToken;

    // Full list of all collaterals supported here
    address[] internal collateralsMapped;

    // Reward token address
    address public rewardTokenAddress;
    uint256 public rewardLiquidationThreshold;

    /**
     * @dev Internal initialize function, to set up initial internal state
     * @param _platformAddress jGeneric platform address
     * @param _vaultAddress Address of the Vault
     * @param _rewardTokenAddress Address of reward token for platform
     * @param _collaterals Addresses of initial supported collaterals
     * @param _pTokens Platform Token corresponding addresses
     */
    function initialize(
        address _platformAddress,
        address _vaultAddress,
        address _rewardTokenAddress,
        address[] calldata _collaterals,
        address[] calldata _pTokens
    ) external initializer {
        InitializableAbstractStrategy._initialize(
            _platformAddress,
            _vaultAddress,
            _rewardTokenAddress,
            _collaterals,
            _pTokens
        );
    }

    function _initialize(
        address _platformAddress,
        address _vaultAddress,
        address _rewardTokenAddress,
        address[] memory _collaterals,
        address[] memory _pTokens
    ) internal {
        platformAddress = _platformAddress;
        vaultAddress = _vaultAddress;
        rewardTokenAddress = _rewardTokenAddress;
        uint256 collateralCount = _collaterals.length;
        require(collateralCount == _pTokens.length, "Invalid input arrays");
        for (uint256 i = 0; i < collateralCount; i++) {
            _setPTokenAddress(_collaterals[i], _pTokens[i]);
        }
    }

    /**
     * @dev Collect accumulated reward token and send to Vault.
     */
    function collectRewardToken() external onlyVault   {
        ERC20Upgradeable rewardToken = ERC20Upgradeable(rewardTokenAddress);
        uint256 balance = rewardToken.balanceOf(address(this));
        emit RewardTokenCollected(vaultAddress, balance);
        rewardToken.safeTransfer(vaultAddress, balance);
    }

    /**
     * @dev Verifies that the caller is the Vault.
     */
    modifier onlyVault() {
        require(msg.sender == vaultAddress, "Caller is not the Vault");
        _;
    }

    /**
     * @dev Verifies that the caller is the Vault or Governor.
     */
    modifier  onlyVaultOrOwner() {
        require(
            msg.sender == vaultAddress || msg.sender == owner(),
            "Caller is not the Vault or Governor"
        );
        _;
    }

    /**
     * @dev Set the reward token address.
     * @param _rewardTokenAddress Address of the reward token
     */
    function setRewardTokenAddress(address _rewardTokenAddress)
        external

    {
        rewardTokenAddress = _rewardTokenAddress;
    }

    /**
     * @dev Set the reward token liquidation threshold.
     * @param _threshold Threshold amount in decimals of reward token that will
     * cause the Vault to claim and withdrawAll on allocate() calls.
     */
    function setRewardLiquidationThreshold(uint256 _threshold)
        external

    {
        rewardLiquidationThreshold = _threshold;
    }

    /**
     * @dev Provide support for collateral by passing its pToken address.
     *      This method can only be called by the system Governor
     * @param _collateral    Address for the collateral
     * @param _pToken   Address for the corresponding platform token
     */
    function setPTokenAddress(address _collateral, address _pToken)
        external

    {
        _setPTokenAddress(_collateral, _pToken);
    }

    /**
     * @dev Remove a supported collateral by passing its index.
     *      This method can only be called by the system Governor
     * @param _collateralIndex Index of the collateral to be removed
     */
    function removePToken(uint256 _collateralIndex) external   {
        require(_collateralIndex < collateralsMapped.length, "Invalid index");
        address collateral = collateralsMapped[_collateralIndex];
        address pToken = collateralToPToken[collateral];

        if (_collateralIndex < collateralsMapped.length - 1) {
            collateralsMapped[_collateralIndex] = collateralsMapped[collateralsMapped.length - 1];
        }
        collateralsMapped.pop();
        collateralToPToken[collateral] = address(0);

        emit PTokenRemoved(collateral, pToken);
    }

    /**
     * @dev Provide support for collateral by passing its pToken address.
     *      Add to internal mappings and execute the platform specific,
     * abstract method `_abstractSetPToken`
     * @param _collateral    Address for the collateral
     * @param _pToken   Address for the corresponding platform token
     */
    function _setPTokenAddress(address _collateral, address _pToken) internal {
        require(collateralToPToken[_collateral] == address(0), "pToken already set");
        require(
            _collateral != address(0) && _pToken != address(0),
            "Invalid addresses"
        );

        collateralToPToken[_collateral] = _pToken;
        collateralsMapped.push(_collateral);

        emit PTokenAdded(_collateral, _pToken);

        _abstractSetPToken(_collateral, _pToken);
    }

    /**
     * @dev Transfer token to owner. Intended for recovering tokens stuck in
     *      strategy contracts, i.e. mistaken sends.
     * @param _collateral Address for the collateral
     * @param _amount Amount of the collateral to transfer
     */
    function transferToken(address _collateral, uint256 _amount)
        public

    {
        ERC20Upgradeable(_collateral).safeTransfer(owner(), _amount);
    }

    /***************************************
                 Abstract
    ****************************************/

    function _abstractSetPToken(address _collateral, address _pToken) internal virtual;

    function safeApproveAllTokens() external virtual;

    /**
     * @dev Deposit a amount of collateral into the platform
     * @param _collateral               Address for the collateral
     * @param _amount              Units of collateral to deposit
     */
    function deposit(address _collateral, uint256 _amount) external virtual;

    /**
     * @dev Deposit balance of all supported collaterals into the platform
     */
    function depositAll() external virtual;

    /**
     * @dev Withdraw an amount of collateral from the platform.
     * @param _recipient         Address to which the collateral should be sent
     * @param _collateral             Address of the collateral
     * @param _amount            Units of collateral to withdraw
     */
    function withdraw(
        address _recipient,
        address _collateral,
        uint256 _amount
    ) external virtual;

    /**
     * @dev Withdraw all collaterals from strategy sending collaterals to Vault.
     */
    function withdrawAll() external virtual;

    /**
     * @dev Get the total collateral value held in the platform.
     *      This includes any interest that was generated since depositing.
     * @param _collateral      Address of the collateral
     * @return balance    Total value of the collateral in the platform
     */
    function checkBalance(address _collateral)
        external
        view
        virtual
        returns (uint256 balance);

    function checkInterestEarned(address _collateral)
        external
        view
        virtual
        returns (uint256 interestEarned);

    /**
     * @dev Check if an collateral is supported.
     * @param _collateral    Address of the collateral
     * @return bool     Whether collateral is supported
     */
    function supportsCollateral(address _collateral) external view virtual returns (bool);
}
