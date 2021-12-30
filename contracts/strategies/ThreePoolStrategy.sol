// SPDX-License-Identifier: MIT
/**
 * @title Curve 3Pool Strategy
 * @notice Investment strategy for investing stablecoins via Curve 3Pool
 * @author Sperax Inc
 */
 pragma solidity ^0.6.12;

import '@openzeppelin/contracts/token/ERC20/ERC20.sol';
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import '../interfaces/IOracle.sol';
import { ICurve3Pool } from "./ICurve3Pool.sol";
import { ICurveGauge } from "./ICurveGauge.sol";
import { InitializableAbstractStrategy } from "./InitializableAbstractStrategy.sol";
import { StableMath } from "../libraries/StableMath.sol";

contract ThreePoolStrategy is InitializableAbstractStrategy {
    using StableMath for uint256;
    using SafeERC20 for IERC20;

    event RewardTokenCollected(address recipient, uint256 amount);
    event SlippageChanged(uint256 newSlippage);
    event ThresholdChanged(uint256 newThreshold);

    uint256 public lpAssetThreshold = 3000;
    uint256 public lpAssetSlippage = 10*1e16; // TODO: change to a reasonable number
    uint256 internal supportedAssetIndex;

    ICurveGauge internal curveGauge;
    ICurve3Pool internal curvePool;
    IOracle internal oracle;

    receive() external payable {}
    fallback() external payable {}

    /**
     * Initializer for setting up strategy internal state. This overrides the
     * InitializableAbstractStrategy initializer as Curve strategies don't fit
     * well within that abstraction.
     * @param _platformAddress Address of the Curve 3pool
     * @param _vaultAddress Address of the vault
     * @param _rewardTokenAddress Address of CRV
     * @param _assets Addresses of supported assets. MUST be passed in the same
     *                order as returned by coins on the pool contract, i.e.
     *                DAI, USDC, USDT
     * @param _pTokens Platform Token corresponding addresses
     * @param _crvGaugeAddress Address of the Curve DAO gauge for this pool
     */
    function initialize(
        address _platformAddress, // 3Pool address
        address _vaultAddress,
        address _rewardTokenAddress, // CRV
        address[] calldata _assets,
        address[] calldata _pTokens,
        address _crvGaugeAddress,
        uint256 _supportedAssetIndex,
        address _oracleAddr
    ) external initializer {
        require(_assets.length == 3, "Must have exactly three assets");
        require(_supportedAssetIndex < 3, "_supportedAssetIndex exceeds 2");
        // Should be set prior to abstract initialize call otherwise
        // abstractSetPToken calls will fail
        InitializableAbstractStrategy._initialize(
            _platformAddress,
            _vaultAddress,
            _rewardTokenAddress,
            _assets,
            _pTokens
        );
        curveGauge = ICurveGauge(_crvGaugeAddress);
        curvePool = ICurve3Pool(platformAddress);
        supportedAssetIndex = _supportedAssetIndex;
        oracle = IOracle(_oracleAddr);
        _abstractSetPToken(
            assetsMapped[_supportedAssetIndex],
            assetToPToken[assetsMapped[_supportedAssetIndex]]
        );
    }

    /**
     * @dev change to a new lpAssetSlippage
     * @dev lpAssetSlippage set to 1e16 means the slippage is 1% (overall precision
            is 1e18); it is the slippage on the conversion between LP token
            and underlying collateral/asset
     * @param _lpAssetSlippage new slippage setting
     */
    function changeSlippage(uint256 _lpAssetSlippage) external onlyOwner {
        lpAssetSlippage = _lpAssetSlippage;
        emit SlippageChanged(lpAssetSlippage);
    }

    /**
     * @dev change to a new lpAssetThreshold
     * @dev lpAssetThreshold should be set to the minimum number
            of totalPTokens such that curvePool.calc_withdraw_one_coin does not
            revert
     * @param _lpAssetThreshold new lpAssetThreshold
     */
    function changeThreshold(uint256 _lpAssetThreshold) external onlyOwner {
        lpAssetThreshold = _lpAssetThreshold;
        emit ThresholdChanged(lpAssetThreshold);
    }


    /**
     * @dev Check if an asset/collateral is supported.
     * @param _asset    Address of the asset
     * @return bool     Whether asset is supported
     */
    function supportsCollateral(
        address _asset
    ) public view override returns (bool) {
        if (assetToPToken[_asset] != address(0) &&
            _getPoolCoinIndex(_asset) == supportedAssetIndex) {
                return true;
            }
        else {
            return false;
        }
    }

    /**
     * @dev Deposit asset into the Curve 3Pool
     * @param _asset Address of asset to deposit
     * @param _amount Amount of asset to deposit
     */
    function deposit(address _asset, uint256 _amount)
        external
        override
        onlyVault
        nonReentrant
    {
        require(supportsCollateral(_asset), "Unsupported collateral");
        require(_amount > 0, "Must deposit something");
        // 3Pool requires passing deposit amounts for all 3 assets, set to 0 for
        // all
        uint256[3] memory _amounts;
        uint256 poolCoinIndex = _getPoolCoinIndex(_asset);
        // Set the amount on the asset we want to deposit
        _amounts[poolCoinIndex] = _amount;
        uint256 assetDecimals = ERC20(_asset).decimals();
        uint256 assetPrice =  oracle.getCollateralPrice(_asset);
        uint256 assetPrice_prec = oracle.getCollateralPrice_prec(_asset);
        uint256 depositValue = _amount
            .scaleBy(int8(18 - assetDecimals))
            .mul(assetPrice)
            .divPrecisely(curvePool.get_virtual_price())
            .div(assetPrice_prec);
        uint256 minMintAmount = depositValue.mulTruncate(
            uint256(1e18).sub(lpAssetSlippage)
        );
        // Do the deposit to 3pool
        // triger to deposit LP tokens
        curvePool.add_liquidity(_amounts, 0); //TODO: change to minMintAmount
        allocatedAmt[_asset] = allocatedAmt[_asset].add(_amount);
        // Deposit into Gauge
        IERC20 pToken = IERC20(assetToPToken[_asset]);
        curveGauge.deposit(
            pToken.balanceOf(address(this))
        );
        emit Deposit(_asset, address(assetToPToken[_asset]), _amount);
    }

    function withdraw(
        address _recipient,
        address _asset,
        uint256 _amount
    ) external override onlyVault nonReentrant {
        _withdraw(_recipient, _asset, _amount);
    }

    /**
     * @dev Withdraw asset from Curve 3Pool
     * @param _asset Address of asset to withdraw
     * @param _amount Amount of asset to withdraw
     */
    function withdrawToVault(
        address _asset,
        uint256 _amount
    ) external override onlyOwner nonReentrant {
        _withdraw(vaultAddress, _asset, _amount);
    }

    /**
     * @dev Collect interest earned from 3Pool
     * @param _recipient Address to receive withdrawn asset
     * @param _asset Address of asset to withdraw
     */
    function collectInterest(
        address _recipient,
        address _asset
    ) external override onlyVault nonReentrant {
        require(_recipient != address(0), "Invalid recipient");
        require(supportsCollateral(_asset), "Unsupported collateral");
        (uint256 contractPTokens, , uint256 totalPTokens) = _getTotalPTokens();
        uint256 poolCoinIndex = _getPoolCoinIndex(_asset);
        uint256 assetInterest = checkInterestEarned(_asset);
        require(assetInterest > 0, "No interest earned");
        uint256 maxAmount = curvePool.calc_withdraw_one_coin(
            totalPTokens,
            poolCoinIndex
        );
        uint256 maxBurnedPTokens = totalPTokens
            .mul(assetInterest)
            .div(maxAmount);
        // Not enough in this contract or in the Gauge, can't proceed
        require(totalPTokens >= maxBurnedPTokens, "Insufficient 3CRV balance");
        // We have enough LP tokens, make sure they are all on this contract
        if (contractPTokens < maxBurnedPTokens) {
            // Not enough of pool token exists on this contract, some must be
            // staked in Gauge, unstake difference
            curveGauge.withdraw(
                maxBurnedPTokens.sub(contractPTokens)
            );
        }
        (contractPTokens, , ) = _getTotalPTokens();
        maxBurnedPTokens = maxBurnedPTokens < contractPTokens ?
                           maxBurnedPTokens : contractPTokens;
        uint256 minRedeemAmount = _getMinRedeemAmt(maxBurnedPTokens, _asset);
        uint256 balance_before = IERC20(_asset).balanceOf(address(this));
        curvePool.remove_liquidity_one_coin(
            maxBurnedPTokens,
            _getPoolCoinIndex(_asset),
            minRedeemAmount
        );
        uint256 _amount_received = IERC20(_asset).balanceOf(address(this))
            .sub(balance_before);
        IERC20(_asset).safeTransfer(_recipient, _amount_received);
        emit InterestCollected(
            _asset,
            address(assetToPToken[_asset]),
            _amount_received
        );
    }

    /**
     * @dev Collect accumulated CRV and send to Vault.
     */
    function collectRewardToken() external override onlyVault nonReentrant {
        IERC20 crvToken = IERC20(rewardTokenAddress);
        uint256 balance_before = crvToken.balanceOf(vaultAddress);
        curveGauge.claim_rewards(address(this), vaultAddress);
        uint256 balance_after = crvToken.balanceOf(vaultAddress);
        emit RewardTokenCollected(vaultAddress, balance_after.sub(balance_before));
    }

    /**
     * @dev Approve the spending of all assets by their corresponding pool tokens,
     *      if for some reason is it necessary.
     */
    function safeApproveAllTokens() override onlyOwner external {
        // This strategy is a special case since it only supports one asset
        _abstractSetPToken(
            assetsMapped[supportedAssetIndex],
            assetToPToken[assetsMapped[supportedAssetIndex]]
        );
    }

    /**
     * @dev Get the total asset value held in the platform
     * @param _asset      Address of the asset
     * @return balance    Total value of the asset in the platform
     */
    function checkBalance(address _asset)
        public
        override
        view
        returns (uint256 balance)
    {
        require(supportsCollateral(_asset), "Unsupported collateral");
        // Calculate how many asset we get in return after withdrawing
        // all LP tokens
        (, , uint256 totalPTokens) = _getTotalPTokens();
        uint256 poolCoinIndex = _getPoolCoinIndex(_asset);
        if (totalPTokens > lpAssetThreshold) {
            balance = curvePool.calc_withdraw_one_coin(
                totalPTokens,
                poolCoinIndex
            );
        }
    }

    /**
     * @dev Get the amount of asset/collateral earned as interest
     * @param _asset  Address of the asset
     * @return interestEarned
               The amount of asset/collateral earned as interest
     */
    function checkInterestEarned(address _asset)
        public
        view
        override
        returns (uint256)
    {
        require(supportsCollateral(_asset), "Unsupported collateral");
        // Calculate how many platform tokens we need to withdraw the asset
        // amount in the worst case (i.e withdrawing all LP tokens)
        (uint256 contractPTokens, , uint256 totalPTokens) = _getTotalPTokens();
        uint256 poolCoinIndex = _getPoolCoinIndex(_asset);
        uint256 maxAmount;
        if (totalPTokens > lpAssetThreshold) {
            maxAmount = curvePool.calc_withdraw_one_coin(
                totalPTokens,
                poolCoinIndex
            );
        }
        uint256 assetInterest;
        if (maxAmount > allocatedAmt[_asset]) {
            return assetInterest = maxAmount.sub(allocatedAmt[_asset]);
        } else {
            return 0;
        }
    }

    /**
     * @dev Withdraw asset from Curve 3Pool
     * @param _recipient Address to receive withdrawn asset
     * @param _asset Address of asset to withdraw
     * @param _amount Amount of asset to withdraw
     */
    function _withdraw(
        address _recipient,
        address _asset,
        uint256 _amount
    ) internal {
        require(_recipient != address(0), "Invalid recipient");
        require(supportsCollateral(_asset), "Unsupported collateral");
        require(_amount > 0, "Invalid amount");
        (uint256 contractPTokens, , uint256 totalPTokens) = _getTotalPTokens();
        // Calculate how many platform tokens we need to withdraw the asset
        // amount in the worst case (i.e withdrawing all LP tokens)
        require(totalPTokens > 0, "Insufficient 3CRV balance");
        uint256 maxAmount;
        if (totalPTokens > lpAssetThreshold) {
            maxAmount = curvePool.calc_withdraw_one_coin(
                totalPTokens,
                _getPoolCoinIndex(_asset)
            );
        }
        uint256 maxBurnedPTokens = totalPTokens.mul(_amount).div(maxAmount);
        // Not enough in this contract or in the Gauge, can't proceed
        require(totalPTokens >= maxBurnedPTokens, "Insufficient 3CRV balance");
        // We have enough LP tokens, make sure they are all on this contract
        if (contractPTokens < maxBurnedPTokens) {
            // Not enough of pool token exists on this contract, some must be
            // staked in Gauge, unstake difference
            curveGauge.withdraw(
                maxBurnedPTokens.sub(contractPTokens)
            );
        }
        (contractPTokens, , ) = _getTotalPTokens();
        maxBurnedPTokens = maxBurnedPTokens < contractPTokens ?
                           maxBurnedPTokens : contractPTokens;
        uint256 minRedeemAmount = _getMinRedeemAmt(maxBurnedPTokens, _asset);
        uint256 balance_before = IERC20(_asset).balanceOf(address(this));
        curvePool.remove_liquidity_one_coin(
            maxBurnedPTokens,
            _getPoolCoinIndex(_asset),
            minRedeemAmount
        );
        uint256 _amount_received = IERC20(_asset).balanceOf(address(this))
            .sub(balance_before);
        if (_amount_received >= allocatedAmt[_asset]) {
            allocatedAmt[_asset] = 0;
        } else {
            allocatedAmt[_asset] = allocatedAmt[_asset].sub(_amount_received);
        }
        IERC20(_asset).safeTransfer(_recipient, _amount_received);
        emit Withdrawal(_asset, address(assetToPToken[_asset]), _amount_received);
    }

    /**
     * @dev Call the necessary approvals for the Curve pool and gauge
     * @param _asset Address of the asset
     * @param _pToken Address of the corresponding platform token (i.e. 3CRV)
     */
    function _abstractSetPToken(address _asset, address _pToken) override internal {
        IERC20 asset = IERC20(_asset);
        IERC20 pToken = IERC20(_pToken);
        // 3Pool for asset (required for adding liquidity)
        asset.safeApprove(platformAddress, 0);
        asset.safeApprove(platformAddress, uint256(-1));
        // 3Pool for LP token (required for removing liquidity)
        pToken.safeApprove(platformAddress, 0);
        pToken.safeApprove(platformAddress, uint256(-1));
        // Gauge for LP token
        pToken.safeApprove(address(curveGauge), 0);
        pToken.safeApprove(address(curveGauge), uint256(-1));
    }

    /**
     * @dev Calculate the total platform token balance (i.e. 3CRV) that exist in
     * this contract or is staked in the Gauge (or in other words, the total
     * amount platform tokens we own).
     */
    function _getTotalPTokens()
        internal
        view
        returns (
            uint256 contractPTokens,
            uint256 gaugePTokens,
            uint256 totalPTokens
        )
    {
        contractPTokens = IERC20(assetToPToken[assetsMapped[0]]).balanceOf(
            address(this)
        );
        gaugePTokens = curveGauge.balanceOf(address(this));
        totalPTokens = contractPTokens.add(gaugePTokens);
    }

    /**
     * @dev Get the index of the coin in 3pool
     */
    function _getPoolCoinIndex(address _asset) internal view returns (uint256) {
        for (uint256 i = 0; i < 3; i++) {
            if (assetsMapped[i] == _asset) return i;
        }
        revert("Unsupported collateral");
    }

    /**
     * @dev Get the expected amount of asset/collateral when redeeming LP tokens
     * @param lpTokenAmt  Amount of LP token to redeem
     * @param _asset  Address of the asset
     * @return interestEarned
               The amount of asset/collateral earned as interest
     */
    function _getMinRedeemAmt(
        uint256 lpTokenAmt,
        address _asset
    ) internal returns (uint256) {
        uint256 assetPrice_prec = oracle.getCollateralPrice_prec(_asset);
        uint256 assetPrice = oracle.getCollateralPrice(_asset);
        uint256 minRedeemAmount = lpTokenAmt
            .mul(curvePool.get_virtual_price())
            .mul(assetPrice_prec)
            .div(assetPrice)
            .div(1e18) //get_virtual_price()'s precsion
            .scaleBy(int8(ERC20(_asset).decimals() - 18));
    }
}
