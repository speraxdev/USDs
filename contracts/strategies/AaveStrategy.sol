// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

/**
 * @title USDs Aave Strategy
 * @notice Investment strategy for investing stablecoins via Aave
 * @author Origin Protocol Inc
 */
import "./IAave.sol";
import {
    ERC20Upgradeable,
    InitializableAbstractStrategy
} from "./InitializableAbstractStrategy.sol";

contract AaveStrategy is InitializableAbstractStrategy {
    uint16 constant referralCode = 0;
    mapping(address => uint) public principalAmt;

    /**
     * @dev Deposit collateral into Aave
     * @param _collateral Address of collateral to deposit
     * @param _amount Amount of collateral to deposit
     */
    function deposit(address _collateral, uint256 _amount)
        external
        onlyVault
        override
    {
        _deposit(_collateral, _amount);
    }

    /**
     * @dev Deposit collateral into Aave
     * @param _collateral Address of collateral to deposit
     * @param _amount Amount of collateral to deposit
     */
    function _deposit(address _collateral, uint256 _amount) internal {
        require(_amount > 0, "Must deposit something");
        IAaveAToken aToken = _getATokenFor(_collateral);
        emit Deposit(_collateral, address(aToken), _amount);
        _getLendingPool().deposit(_collateral, _amount, referralCode);
        principalAmt[_collateral] = principalAmt[_collateral].add(_amount);
    }

    /**
     * @dev Deposit the entire balance of any supported collateral into Aave
     */
    function depositAll() external onlyVault override {
        for (uint256 i = 0; i < collateralsMapped.length; i++) {
            uint256 balance = ERC20Upgradeable(collateralsMapped[i]).balanceOf(address(this));
            if (balance > 0) {
                _deposit(collateralsMapped[i], balance);
            }
        }
    }

    /**
     * @dev Withdraw collateral from Aave
     * @param _recipient Address to receive withdrawn collateral
     * @param _collateral Address of collateral to withdraw
     * @param _amount Amount of collateral to withdraw
     */
    function withdraw(
        address _recipient,
        address _collateral,
        uint256 _amount
    ) external onlyVault   override {
        require(_amount > 0, "Must withdraw something");
        require(_recipient != address(0), "Must specify recipient");

        IAaveAToken aToken = _getATokenFor(_collateral);
        emit Withdrawal(_collateral, address(aToken), _amount);
        aToken.redeem(_amount);
        ERC20Upgradeable(_collateral).safeTransfer(_recipient, _amount);
        uint balance = aToken.balanceOf(address(this));
        if (balance < principalAmt[_collateral]) {
            principalAmt[_collateral] = balance;
        }
    }

    /**
     * @dev Remove all collaterals from platform and send them to Vault contract.
     */
    function withdrawAll() external onlyVaultOrOwner override {
        for (uint256 i = 0; i < collateralsMapped.length; i++) {
            // Redeem entire balance of aToken
            IAaveAToken aToken = _getATokenFor(collateralsMapped[i]);
            uint256 balance = aToken.balanceOf(address(this));
            if (balance > 0) {
                aToken.redeem(balance);
                // Transfer entire balance to Vault
                ERC20Upgradeable collateral = ERC20Upgradeable(collateralsMapped[i]);
                collateral.safeTransfer(
                    vaultAddress,
                    collateral.balanceOf(address(this))
                );
            }
        }
    }

    /**
     * @dev Get the total collateral value held in the platform
     * @param _collateral      Address of the collateral
     * @return balance    Total value of the collateral in the platform
     */
    function checkBalance(address _collateral)
        external
        view
        override
        returns (uint256 balance)
    {
        // Balance is always with token aToken decimals
        IAaveAToken aToken = _getATokenFor(_collateral);
        balance = aToken.balanceOf(address(this));
    }

    function checkInterestEarned(address _collateral)
        external
        view
        override
        returns (uint256 interestEarned)
    {
        // Balance is always with token aToken decimals
        IAaveAToken aToken = _getATokenFor(_collateral);
        interestEarned = aToken.balanceOf(address(this)).sub(principalAmt[_collateral]);

    }

    /**
     * @dev Retuns bool indicating whether collateral is supported by strategy
     * @param _collateral Address of the collateral
     */
    function supportsCollateral(address _collateral) external view override returns (bool) {
        return collateralToPToken[_collateral] != address(0);
    }

    /**
     * @dev Approve the spending of all collaterals by their corresponding aToken,
     *      if for some reason is it necessary.
     */
    function safeApproveAllTokens() external onlyOwner   override {
        uint256 collateralCount = collateralsMapped.length;
        address lendingPoolVault = _getLendingPoolCore();
        // approve the pool to spend the bCollateral
        for (uint256 i = 0; i < collateralCount; i++) {
            address collateral = collateralsMapped[i];
            // Safe approval
            ERC20Upgradeable(collateral).safeApprove(lendingPoolVault, 0);
            ERC20Upgradeable(collateral).safeApprove(lendingPoolVault, uint256(-1));
        }
    }

    /**
     * @dev Internal method to respond to the addition of new collateral / aTokens
     *      We need to approve the aToken and give it permission to spend the collateral
     * @param _collateral Address of the collateral to approve
     * @param _aToken This aToken has the approval approval
     */
    function _abstractSetPToken(address _collateral, address _aToken) internal override {
        address lendingPoolVault = _getLendingPoolCore();
        ERC20Upgradeable(_collateral).safeApprove(lendingPoolVault, 0);
        ERC20Upgradeable(_collateral).safeApprove(lendingPoolVault, uint256(-1));
    }

    /**
     * @dev Get the aToken wrapped in the ICERC20 interface for this collateral.
     *      Fails if the pToken doesn't exist in our mappings.
     * @param _collateral Address of the collateral
     * @return Corresponding aToken to this collateral
     */
    function _getATokenFor(address _collateral) internal view returns (IAaveAToken) {
        address aToken = collateralToPToken[_collateral];
        require(aToken != address(0), "aToken does not exist");
        return IAaveAToken(aToken);
    }

    /**
     * @dev Get the current address of the Aave lending pool, which is the gateway to
     *      depositing.
     * @return Current lending pool implementation
     */
    function _getLendingPool() internal view returns (IAaveLendingPool) {
        address lendingPool = ILendingPoolAddressesProvider(platformAddress)
            .getLendingPool();
        require(lendingPool != address(0), "Lending pool does not exist");
        return IAaveLendingPool(lendingPool);
    }

    /**
     * @dev Get the current address of the Aave lending pool core, which stores all the
     *      reserve tokens in its vault.
     * @return Current lending pool core address
     */
    function _getLendingPoolCore() internal view returns (address payable) {
        address payable lendingPoolCore = ILendingPoolAddressesProvider(
            platformAddress
        )
            .getLendingPoolCore();
        require(
            lendingPoolCore != address(uint160(address(0))),
            "Lending pool core does not exist"
        );
        return lendingPoolCore;
    }
}
