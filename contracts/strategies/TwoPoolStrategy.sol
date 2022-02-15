// Current version: 2
// This contract's version: 2
// Arbitrum-one proxy addresses: 1. USDC strategy: 0xbF82a3212e13b2d407D10f5107b5C8404dE7F403
//                               2. USDT strategy: 0xdc118F2F00812326Fe0De5c9c74c1c0c609d1eB4

// SPDX-License-Identifier: MIT
/**
 * @title Curve 2Pool Strategy
 * @notice Investment strategy for investing stablecoins via Curve 2Pool
 * @author Sperax Inc
 */
 pragma solidity ^0.6.12;

import '@openzeppelin/contracts/token/ERC20/ERC20.sol';
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import '../interfaces/IOracle.sol';
import { ICurve2Pool } from "../interfaces/ICurve2Pool.sol";
import { ICurveGauge } from "../interfaces/ICurveGauge.sol";
import { InitializableAbstractStrategy } from "./InitializableAbstractStrategy.sol";
import { StableMath } from "../libraries/StableMath.sol";

contract TwoPoolStrategy is InitializableAbstractStrategy {
    using StableMath for uint256;
    using SafeERC20 for IERC20;

    event SlippageChanged(uint256 newSlippage);
    event ThresholdChanged(uint256 newThreshold);

    // minimum LP needed when calculating LP to asset conversion
    uint256 public lpAssetThreshold = 3000;
    uint256 public lpAssetSlippage = 9800000;
    uint256 internal supportedAssetIndex;

    ICurveGauge public curveGauge;
    ICurve2Pool public curvePool;
    IOracle public oracle;

    /**
     * Initializer for setting up strategy internal state. This overrides the
     * InitializableAbstractStrategy initializer as Curve strategies don't fit
     * well within that abstraction.
     * @param _platformAddress Address of the Curve 2Pool
     * @param _vaultAddress Address of the vault
     * @param _rewardTokenAddress Address of CRV
     * @param _assets Addresses of supported assets. MUST be passed in the same
     *                order as returned by coins on the pool contract, i.e.
     *                DAI, USDC, USDT
     * @param _pTokens Platform Token corresponding addresses
     * @param _crvGaugeAddress Address of the Curve DAO gauge for this pool
     */
    function initialize(
        address _platformAddress, // 2Pool address
        address _vaultAddress,
        address _rewardTokenAddress, // CRV
        address[] calldata _assets,
        address[] calldata _pTokens,
        address _crvGaugeAddress,
        uint256 _supportedAssetIndex,
        address _oracleAddr
    ) external initializer {
        require(_assets.length == 2, "Must have exactly two assets");
        require(_supportedAssetIndex < 2, "_supportedAssetIndex exceeds 2");
        // Should be set prior to abstract initialize call otherwise
        // abstractSetPToken calls will fail
        curveGauge = ICurveGauge(_crvGaugeAddress);
        supportedAssetIndex = _supportedAssetIndex;
        oracle = IOracle(_oracleAddr);
        InitializableAbstractStrategy._initialize(
            _platformAddress,
            _vaultAddress,
            _rewardTokenAddress,
            _assets,
            _pTokens
        );
        curvePool = ICurve2Pool(platformAddress);
    }

    /**
     * @dev change to a new lpAssetSlippage
     * @dev lpAssetSlippage set to 9900000 means the slippage is 1%;
            overall precision is 10000000;
            it is the slippage on the conversion between LP token and underlying
            collateral/asset
     * @param _lpAssetSlippage new slippage setting
     */
    function changeSlippage(uint256 _lpAssetSlippage) external onlyOwner {
        require(_lpAssetSlippage <= 10000000, 'Slippage exceeds 100%');
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
     * @dev Deposit asset into the Curve 2Pool
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
        // 2Pool requires passing deposit amounts for both 2 assets, set to 0 for
        // all
        uint256[2] memory _amounts;
        uint256 poolCoinIndex = _getPoolCoinIndex(_asset);
        // Set the amount on the asset we want to deposit
        _amounts[poolCoinIndex] = _amount;
        uint256 expectedPtokenAmt = _getExpectedPtokenAmt(_amount, _asset);
        uint256 minMintAmount = expectedPtokenAmt
            .mul(lpAssetSlippage)
            .div(10000000);
        // Do the deposit to 2Pool
        // triger to deposit LP tokens
        curvePool.add_liquidity(_amounts, minMintAmount);
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
     * @dev Withdraw asset from Curve 2Pool
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
     * @dev Collect interest earned from 2Pool
     * @param _recipient Address to receive withdrawn asset
     * @param _asset Asset type deposited into this strategy contract
     */
    function collectInterest(
        address _recipient,
        address _asset
    ) external override onlyVault nonReentrant returns (
        address interestAsset,
        uint256 interestAmt
    ) {
        require(_recipient != address(0), "Invalid recipient");
        require(supportsCollateral(_asset), "Unsupported collateral");
        (uint256 contractPTokens, , uint256 totalPTokens) = _getTotalPTokens();
        uint256 assetInterest = checkInterestEarned(_asset);
        require(assetInterest > 0, "No interest earned");
        (uint256 maxReturn, address returnAsset) = _checkMaxReturn();
        interestAsset = returnAsset;
        if (returnAsset != _asset) {
            assetInterest = _convertBewteen(
                supportedAssetIndex,
                _getPoolCoinIndex(returnAsset),
                assetInterest
            );
        }
        uint256 maxBurnedPTokens = totalPTokens
            .mul(assetInterest)
            .div(maxReturn);
        // Not enough in this contract or in the Gauge, can't proceed
        require(totalPTokens >= maxBurnedPTokens, "Insufficient 2CRV balance");
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
        uint256 minRedeemAmount =
            _getExpectedAssetAmt(maxBurnedPTokens, returnAsset)
            .mul(lpAssetSlippage)
            .div(10000000);
        interestAmt = curvePool.remove_liquidity_one_coin(
            maxBurnedPTokens,
            int128(_getPoolCoinIndex(returnAsset)),
            minRedeemAmount,
            _recipient
        );
        emit InterestCollected(
            returnAsset,
            address(assetToPToken[_asset]),
            interestAmt
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
     * @return balance    Total amount of the asset in the platform
     */
    function checkBalance(address _asset)
        public
        override
        view
        returns (uint256 balance)
    {
        require(supportsCollateral(_asset), "Unsupported collateral");
        (uint256 maxReturn, address returnAsset) = _checkMaxReturn();
        if (_asset != returnAsset) {
            balance = _convertBewteen(
                _getPoolCoinIndex(returnAsset),
                supportedAssetIndex,
                maxReturn
            );
        } else {
            balance = maxReturn;
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
        uint256 balance = checkBalance(_asset);
        if (balance > allocatedAmt[_asset]) {
            return balance.sub(allocatedAmt[_asset]);
        } else {
            return 0;
        }
    }

    /**
     * @dev Withdraw asset from Curve 2Pool
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
        require(totalPTokens > 0, "Insufficient 2CRV balance");
        uint256 maxAmount = 0;
        if (totalPTokens > lpAssetThreshold) {
            maxAmount = curvePool.calc_withdraw_one_coin(
                totalPTokens,
                int128(_getPoolCoinIndex(_asset))
            );
        }
        uint256 maxBurnedPTokens = totalPTokens.mul(_amount).div(maxAmount);
        // Not enough in this contract or in the Gauge, can't proceed
        require(totalPTokens >= maxBurnedPTokens, "Insufficient 2CRV balance");
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
        uint256 expectedAssetAmt = _getExpectedAssetAmt(maxBurnedPTokens, _asset);
        uint256 minRedeemAmount = expectedAssetAmt
            .mul(lpAssetSlippage)
            .div(10000000);
        uint256 _amount_received = curvePool.remove_liquidity_one_coin(
            maxBurnedPTokens,
            int128(_getPoolCoinIndex(_asset)),
            minRedeemAmount,
            _recipient
        );
        if (_amount_received >= allocatedAmt[_asset]) {
            allocatedAmt[_asset] = 0;
        } else {
            allocatedAmt[_asset] = allocatedAmt[_asset].sub(_amount_received);
        }
        emit Withdrawal(_asset, address(assetToPToken[_asset]), _amount_received);
    }

    /**
     * @dev Call the necessary approvals for the Curve pool and gauge
     * @param _asset Address of the asset
     * @param _pToken Address of the corresponding platform token (i.e. 2CRV)
     */
    function _abstractSetPToken(address _asset, address _pToken) override internal {
        IERC20 asset = IERC20(_asset);
        IERC20 pToken = IERC20(_pToken);
        // 2Pool for asset (required for adding liquidity)
        asset.safeApprove(platformAddress, 0);
        asset.safeApprove(platformAddress, uint256(-1));
        // 2Pool for LP token (required for removing liquidity)
        pToken.safeApprove(platformAddress, 0);
        pToken.safeApprove(platformAddress, uint256(-1));
        // Gauge for LP token
        pToken.safeApprove(address(curveGauge), 0);
        pToken.safeApprove(address(curveGauge), uint256(-1));
    }

    /**
     * @dev Calculate the total platform token balance (i.e. 2CRV) that exist in
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
     * @dev Get the index of the coin in 2Pool
     */
    function _getPoolCoinIndex(address _asset) internal view returns (uint256) {
        for (uint256 i = 0; i < 2; i++) {
            if (assetsMapped[i] == _asset) return i;
        }
        revert("Unsupported collateral");
    }

    /**
     * @dev Get the expected amount of asset/collateral when redeeming LP tokens
     * @param lpTokenAmt  Amount of LP token to redeem
     * @param _asset  Address of the asset
     * @return expectedAssetAmt
                the expected amount of asset/collateral token received
     */
    function _getExpectedAssetAmt(
        uint256 lpTokenAmt,
        address _asset
    ) internal view returns (uint256 expectedAssetAmt) {
        uint256 assetPrice_prec = oracle.getCollateralPrice_prec(_asset);
        uint256 assetPrice = oracle.getCollateralPrice(_asset);
        expectedAssetAmt = lpTokenAmt
            .mul(curvePool.get_virtual_price())
            .mul(assetPrice_prec)
            .div(assetPrice)
            .div(1e18) //get_virtual_price()'s precsion
            .scaleBy(int8(ERC20(_asset).decimals() - 18));
    }

    /**
     * @dev Get the expected amount of lp when adding liquidity
     * @param assetAmt  Amount of asset/collateral
     * @param _asset  Address of the asset
     * @return expectedPtokenAmt the expected amount of lp token received
     */
    function _getExpectedPtokenAmt(
        uint256 assetAmt,
        address _asset
    ) internal view returns (uint256 expectedPtokenAmt) {
        uint256 assetPrice_prec = oracle.getCollateralPrice_prec(_asset);
        uint256 assetPrice = oracle.getCollateralPrice(_asset);
        expectedPtokenAmt = assetAmt
            .scaleBy(int8(18 - ERC20(_asset).decimals()))
            .mul(assetPrice)
            .mul(1e18)
            .div(curvePool.get_virtual_price())
            .div(assetPrice_prec);
    }

    /**
     * @notice Convert between USDC and USDT using Chainlink oracle
     * @dev The calculation here assume two tokens have the same decimals
     * @param index_from Index of the token to convert from
     * @param index_to Index of the token to convert to
     * @param amount_from amount of the token to convert from
     * @return amount_to amount of the token to convert to
     */
    function _convertBewteen(
        uint256 index_from,
        uint256 index_to,
        uint256 amount_from
    ) internal view returns (uint256 amount_to) {
        require(index_from != index_to, 'Conversion between the same asset');
        address token_from = assetsMapped[index_from];
        address token_to = assetsMapped[index_to];
        uint256 tokenPrice_from = oracle.getCollateralPrice(token_from);
        uint256 tokenPrice_to = oracle.getCollateralPrice(token_to);
        uint256 tokenPricePrecision_from = oracle
            .getCollateralPrice_prec(token_from);
        uint256 tokenPricePrecision_to = oracle
            .getCollateralPrice_prec(token_to);
        amount_to = amount_from
            .mul(tokenPrice_from)
            .mul(tokenPricePrecision_to)
            .div(tokenPrice_to)
            .div(tokenPricePrecision_from);
    }

    /**
     * @notice Get the total asset value held in the platform
     * @return maxReturn The amount of maximum returnAsset token redeemable
     * @return returnAsset The token that lp tokens are redeemed to
     */
    function _checkMaxReturn()
        internal
        view
        returns (uint256 maxReturn, address returnAsset)
    {
        (, , uint256 totalPTokens) = _getTotalPTokens();
        uint256 index_swappedToken =
            supportedAssetIndex == 1 ? 0 : 1;
        uint256 balanceNoSwap_originalToken = 0;
        uint256 balanceSwap_swappedToken = 0;
        uint256 balanceSwap_originalToken = 0;
        if (totalPTokens > lpAssetThreshold) {
            balanceNoSwap_originalToken = curvePool.calc_withdraw_one_coin(
                totalPTokens,
                int128(supportedAssetIndex)
            );
            balanceSwap_swappedToken = curvePool.calc_withdraw_one_coin(
                totalPTokens,
                int128(index_swappedToken)
            );
            balanceSwap_originalToken = _convertBewteen(
                supportedAssetIndex,
                index_swappedToken,
                balanceSwap_swappedToken
            );
        }
        maxReturn = balanceNoSwap_originalToken > balanceSwap_originalToken ?
            balanceNoSwap_originalToken : balanceSwap_swappedToken;
        returnAsset = balanceNoSwap_originalToken > balanceSwap_originalToken ?
            assetsMapped[supportedAssetIndex] : assetsMapped[index_swappedToken];
    }
}
