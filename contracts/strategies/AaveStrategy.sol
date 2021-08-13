pragma solidity ^0.6.12;

/**
 * @title OUSD Aave Strategy
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

    /**
     * @dev Deposit asset into Aave
     * @param _asset Address of asset to deposit
     * @param _amount Amount of asset to deposit
     */
    function deposit(address _asset, uint256 _amount)
        external
        onlyVault
        nonReentrant
    {
        _deposit(_asset, _amount);
    }

    /**
     * @dev Deposit asset into Aave
     * @param _asset Address of asset to deposit
     * @param _amount Amount of asset to deposit
     */
    function _deposit(address _asset, uint256 _amount) internal {
        require(_amount > 0, "Must deposit something");
        IAaveAToken aToken = _getATokenFor(_asset);
        emit Deposit(_asset, address(aToken), _amount);
        _getLendingPool().deposit(_asset, _amount, referralCode);
    }

    /**
     * @dev Deposit the entire balance of any supported asset into Aave
     */
    function depositAll() external onlyVault nonReentrant {
        for (uint256 i = 0; i < assetsMapped.length; i++) {
            uint256 balance = ERC20Upgradeable(assetsMapped[i]).balanceOf(address(this));
            if (balance > 0) {
                _deposit(assetsMapped[i], balance);
            }
        }
    }

    /**
     * @dev Withdraw asset from Aave
     * @param _recipient Address to receive withdrawn asset
     * @param _asset Address of asset to withdraw
     * @param _amount Amount of asset to withdraw
     */
    function withdraw(
        address _recipient,
        address _asset,
        uint256 _amount
    ) external onlyVault nonReentrant {
        require(_amount > 0, "Must withdraw something");
        require(_recipient != address(0), "Must specify recipient");

        IAaveAToken aToken = _getATokenFor(_asset);
        emit Withdrawal(_asset, address(aToken), _amount);
        aToken.redeem(_amount);
        ERC20Upgradeable(_asset).safeTransfer(_recipient, _amount);
    }

    /**
     * @dev Remove all assets from platform and send them to Vault contract.
     */
    function withdrawAll() external onlyVaultOrGovernor nonReentrant {
        for (uint256 i = 0; i < assetsMapped.length; i++) {
            // Redeem entire balance of aToken
            IAaveAToken aToken = _getATokenFor(assetsMapped[i]);
            uint256 balance = aToken.balanceOf(address(this));
            if (balance > 0) {
                aToken.redeem(balance);
                // Transfer entire balance to Vault
                ERC20Upgradeable asset = ERC20Upgradeable(assetsMapped[i]);
                asset.safeTransfer(
                    vaultAddress,
                    asset.balanceOf(address(this))
                );
            }
        }
    }

    /**
     * @dev Get the total asset value held in the platform
     * @param _asset      Address of the asset
     * @return balance    Total value of the asset in the platform
     */
    function checkBalance(address _asset)
        external
        view
        returns (uint256 balance)
    {
        // Balance is always with token aToken decimals
        IAaveAToken aToken = _getATokenFor(_asset);
        balance = aToken.balanceOf(address(this));
    }

    /**
     * @dev Retuns bool indicating whether asset is supported by strategy
     * @param _asset Address of the asset
     */
    function supportsAsset(address _asset) external view returns (bool) {
        return assetToPToken[_asset] != address(0);
    }

    /**
     * @dev Approve the spending of all assets by their corresponding aToken,
     *      if for some reason is it necessary.
     */
    function safeApproveAllTokens() external onlyGovernor nonReentrant {
        uint256 assetCount = assetsMapped.length;
        address lendingPoolVault = _getLendingPoolCore();
        // approve the pool to spend the bAsset
        for (uint256 i = 0; i < assetCount; i++) {
            address asset = assetsMapped[i];
            // Safe approval
            ERC20Upgradeable(asset).safeApprove(lendingPoolVault, 0);
            ERC20Upgradeable(asset).safeApprove(lendingPoolVault, uint256(-1));
        }
    }



    /**
     * @dev Get the aToken wrapped in the ICERC20 interface for this asset.
     *      Fails if the pToken doesn't exist in our mappings.
     * @param _asset Address of the asset
     * @return Corresponding aToken to this asset
     */
    function _getATokenFor(address _asset) internal view returns (IAaveAToken) {
        address aToken = assetToPToken[_asset];
        require(aToken != address(0), "aToken does not exist");
        return IAaveAToken(aToken);
    }


}
