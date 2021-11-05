// SPDX-License-Identifier: agpl-3.0
//pragma solidity ^0.8.0;
pragma solidity >=0.6.12;

import "@openzeppelin/contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";
import { ICERC20 } from "./ICompound.sol";
import { IComptroller } from "../interfaces/IComptroller.sol";
import { InitializableAbstractStrategy } from "./InitializableAbstractStrategy.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";

/**
 * @title USDs CREAM Strategy
 * @notice Investment strategy for investing ERC20 via CREAM
 * @author Sperax Foundation
 */
contract CompoundStrategy is InitializableAbstractStrategy {
    using SafeERC20Upgradeable for IERC20Upgradeable;

    event SkippedWithdrawal(address asset, uint256 amount);

    /**
     * @dev Collect accumulated COMP and send to Vault.
     */
    function collectRewardToken() external override onlyVault nonReentrant {
        // Claim COMP from Comptroller
        ICERC20 cToken = _getCTokenFor(assetsMapped[0]);
        IComptroller comptroller = IComptroller(cToken.comptroller());
        comptroller.claimComp(address(this));
        // Transfer COMP to Vault
        IERC20Upgradeable rewardToken = IERC20Upgradeable(rewardTokenAddress);
        uint256 balance = rewardToken.balanceOf(address(this));
        emit RewardTokenCollected(vaultAddress, balance);
        rewardToken.safeTransfer(vaultAddress, balance);
    }

    /**
     * @dev Deposit asset into Compound
     * @param _asset Address of asset to deposit
     * @param _amount Amount of asset to deposit
     */
    function deposit(address _asset, uint256 _amount)
        external
        override
        onlyVault
        nonReentrant
    {
        _deposit(_asset, _amount);
    }

    /**
     * @dev Deposit asset into Compound
     * @param _asset Address of asset to deposit
     * @param _amount Amount of asset to deposit
     */
    function _deposit(address _asset, uint256 _amount) internal {
        require(_amount > 0, "Must deposit something");
        ICERC20 cToken = _getCTokenFor(_asset);
        emit Deposit(_asset, address(cToken), _amount);
        require(cToken.mint(_amount) == 0, "cToken mint failed");
        allocatedAmt[_asset] = allocatedAmt[_asset].add(_amount);
    }

    /**
     * @dev Deposit the entire balance of any supported asset into Compound
     */
    function depositAll() external override onlyVault nonReentrant {
        for (uint256 i = 0; i < assetsMapped.length; i++) {
            uint256 balance = IERC20Upgradeable(assetsMapped[i]).balanceOf(address(this));
            if (balance > 0) {
                _deposit(assetsMapped[i], balance);
            }
        }
    }

    /**
     * @dev Withdraw asset from Compound
     * @param _recipient Address to receive withdrawn asset
     * @param _asset Address of asset to withdraw
     * @param _amount Amount of asset to withdraw
     */
    function withdraw(
        address _recipient,
        address _asset,
        uint256 _amount
    ) external override onlyVault nonReentrant {
        require(_amount > 0, "Must withdraw something");
        require(_recipient != address(0), "Must specify recipient");

        emit Withdrawal(_asset, address(assetToPToken[_asset]), _amount);

        ICERC20 cToken = _getCTokenFor(_asset);
        // If redeeming 0 cTokens, just skip, else COMP will revert
        uint256 cTokensToRedeem = _convertUnderlyingToCToken(cToken, _amount);
        if (cTokensToRedeem == 0) {
            emit SkippedWithdrawal(_asset, _amount);
            return;
        }

        emit Withdrawal(_asset, address(cToken), _amount);
        require(cToken.redeemUnderlying(_amount) == 0, "Redeem failed");
        IERC20Upgradeable(_asset).safeTransfer(_recipient, _amount);
        if (_amount >= allocatedAmt[_asset]) {
            allocatedAmt[_asset] = 0;
        } else {
            allocatedAmt[_asset] = allocatedAmt[_asset].sub(_amount);
        }
    }

    /**
     * @dev Withdraw asset from Compound
     * @param _asset Address of asset to withdraw
     * @param _amount Amount of asset to withdraw
     */
    function withdrawToVault(
        address _asset,
        uint256 _amount
    ) external override onlyOwner nonReentrant {
        require(_amount > 0, "Must withdraw something");
        require(vaultAddress != address(0), "Must specify recipient");

        emit Withdrawal(_asset, address(assetToPToken[_asset]), _amount);

        ICERC20 cToken = _getCTokenFor(_asset);
        // If redeeming 0 cTokens, just skip, else COMP will revert
        uint256 cTokensToRedeem = _convertUnderlyingToCToken(cToken, _amount);
        if (cTokensToRedeem == 0) {
            emit SkippedWithdrawal(_asset, _amount);
            return;
        }

        emit Withdrawal(_asset, address(cToken), _amount);
        require(cToken.redeemUnderlying(_amount) == 0, "Redeem failed");
        IERC20Upgradeable(_asset).safeTransfer(vaultAddress, _amount);
        if (_amount >= allocatedAmt[_asset]) {
            allocatedAmt[_asset] = 0;
        } else {
            allocatedAmt[_asset] = allocatedAmt[_asset].sub(_amount);
        }
    }

    /**
     * @dev Withdraw asset from Compound
     * @param _recipient Address to receive withdrawn asset
     * @param _asset Address of asset to withdraw
     */
    function withdrawInterest(
        address _recipient,
        address _asset
    ) external override onlyVault nonReentrant {
        uint256 _amount = _checkInterestEarned(_asset);
        require(_amount > 0, "Must withdraw something");
        require(_recipient != address(0), "Must specify recipient");

        emit Withdrawal(_asset, address(assetToPToken[_asset]), _amount);

        ICERC20 cToken = _getCTokenFor(_asset);
        // If redeeming 0 cTokens, just skip, else COMP will revert
        uint256 cTokensToRedeem = _convertUnderlyingToCToken(cToken, _amount);
        if (cTokensToRedeem == 0) {
            emit SkippedWithdrawal(_asset, _amount);
            return;
        }

        emit Withdrawal(_asset, address(cToken), _amount);
        require(cToken.redeemUnderlying(_amount) == 0, "Redeem failed");
        IERC20Upgradeable(_asset).safeTransfer(_recipient, _amount);
    }

    /**
     * @dev Remove all assets from platform and send them to Vault contract.
     */
    function withdrawAll() external override onlyVaultOrOwner nonReentrant {
        for (uint256 i = 0; i < assetsMapped.length; i++) {
            // Redeem entire balance of cToken
            ICERC20 cToken = _getCTokenFor(assetsMapped[i]);
            if (cToken.balanceOf(address(this)) > 0) {
                require(
                    cToken.redeem(cToken.balanceOf(address(this))) == 0,
                    "Redeem failed"
                );
                // Transfer entire balance to Vault
                IERC20Upgradeable asset = IERC20Upgradeable(assetsMapped[i]);
                asset.safeTransfer(
                    vaultAddress,
                    asset.balanceOf(address(this))
                );
            }
            allocatedAmt[assetsMapped[i]] = 0;
        }
    }

    /**
     * @dev Get the total asset value held in the platform
     *      This includes any interest that was generated since depositing
     *      Compound exchange rate between the cToken and asset gradually increases,
     *      causing the cToken to be worth more corresponding asset.
     * @param _asset      Address of the asset
     * @return balance    Total value of the asset in the platform
     */
    function checkBalance(address _asset)
        external
        view
        override
        returns (uint256 balance)
    {
        // Balance is always with token cToken decimals
        ICERC20 cToken = _getCTokenFor(_asset);
        balance = _checkBalance(cToken);
    }

    function checkInterestEarned(address _asset)
        external
        view
        override
        returns (uint256 interestEarned)
    {
        // Balance is always with token cToken decimals
        interestEarned = _checkInterestEarned(_asset);
    }


    /**
     * @dev Get the total asset value held in the platform
     *      underlying = (cTokenAmt * exchangeRate) / 1e18
     * @param _cToken     cToken for which to check balance
     * @return balance    Total value of the asset in the platform
     */
    function _checkBalance(ICERC20 _cToken)
        internal
        view
        returns (uint256 balance)
    {
        uint256 cTokenBalance = _cToken.balanceOf(address(this));
        uint256 exchangeRate = _cToken.exchangeRateStored();
        // e.g. 50e8*205316390724364402565641705 / 1e18 = 1.0265..e18
        balance = (cTokenBalance * exchangeRate) / 1e18;
    }

    function _checkInterestEarned(address _asset)
        internal
        view
        returns (uint256 interestEarned)
    {
        ICERC20 _cToken = _getCTokenFor(_asset);
        uint256 cTokenBalance = _cToken.balanceOf(address(this));
        uint256 exchangeRate = _cToken.exchangeRateStored();
        // e.g. 50e8*205316390724364402565641705 / 1e18 = 1.0265..e18
        uint256 balance = (cTokenBalance * exchangeRate) / 1e18;
        require(balance >= allocatedAmt[_asset], "Asset depreciated");
        interestEarned = balance - allocatedAmt[_asset];

    }

    /**
     * @dev Retuns bool indicating whether asset is supported by strategy
     * @param _asset Address of the asset
     */
    function supportsAsset(address _asset)
        external
        view
        override
        returns (bool)
    {
        return assetToPToken[_asset] != address(0);
    }

    /**
     * @dev Approve the spending of all assets by their corresponding cToken,
     *      if for some reason is it necessary.
     */
    function safeApproveAllTokens() external override {
        uint256 assetCount = assetsMapped.length;
        for (uint256 i = 0; i < assetCount; i++) {
            address asset = assetsMapped[i];
            address cToken = assetToPToken[asset];
            // Safe approval
            IERC20Upgradeable(asset).safeApprove(cToken, 0);
            IERC20Upgradeable(asset).safeApprove(cToken, type(uint256).max);
        }
    }

    /**
     * @dev Internal method to respond to the addition of new asset / cTokens
     *      We need to approve the cToken and give it permission to spend the asset
     * @param _asset Address of the asset to approve
     * @param _cToken The cToken for the approval
     */
    function _abstractSetPToken(address _asset, address _cToken)
        internal
        override
    {
        // Safe approval
        IERC20Upgradeable(_asset).safeApprove(_cToken, 0);
        IERC20Upgradeable(_asset).safeApprove(_cToken, type(uint256).max);
    }

    /**
     * @dev Get the cToken wrapped in the ICERC20 interface for this asset.
     *      Fails if the pToken doesn't exist in our mappings.
     * @param _asset Address of the asset
     * @return Corresponding cToken to this asset
     */
    function _getCTokenFor(address _asset) internal view returns (ICERC20) {
        address cToken = assetToPToken[_asset];
        require(cToken != address(0), "cToken does not exist");
        return ICERC20(cToken);
    }

    /**
     * @dev Converts an underlying amount into cToken amount
     *      cTokenAmt = (underlying * 1e18) / exchangeRate
     * @param _cToken     cToken for which to change
     * @param _underlying Amount of underlying to convert
     * @return amount     Equivalent amount of cTokens
     */
    function _convertUnderlyingToCToken(ICERC20 _cToken, uint256 _underlying)
        internal
        view
        returns (uint256 amount)
    {
        uint256 exchangeRate = _cToken.exchangeRateStored();
        // e.g. 1e18*1e18 / 205316390724364402565641705 = 50e8
        // e.g. 1e8*1e18 / 205316390724364402565641705 = 0.45 or 0
        amount = (_underlying * 1e18) / exchangeRate;
    }
}
