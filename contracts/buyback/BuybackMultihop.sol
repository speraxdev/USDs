// SPDX-License-Identifier: UNLICENSED
//pragma solidity =0.7.6;
//pragma abicoder v2;
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import '@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol';
import '@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol';
import '../libraries/TransferHelper.sol';
import '../libraries/OracleLibrary.sol';
import '../interfaces/ISwapRouter.sol';
import '../interfaces/IBuyback.sol';
import '../interfaces/IOracle.sol';

/**
 * @title buyback contract of USDs protocol
 * @dev unfinished
 * @dev ERC20 compatible contract for USDs
 * @dev reference: https://docs.uniswap.org/protocol/guides/swaps/multihop-swaps
 * @author Sperax Foundation
 */
contract BuybackMultihop is IBuyback {
    using SafeERC20 for IERC20;

    ISwapRouter public immutable swapRouter;
    address public immutable USDs;
    address public immutable inputToken;
    address public immutable intermediateToken;
    uint24 public immutable poolFee1;
    uint24 public immutable poolFee2;
    address public immutable vaultAddr;
    address public constant UniswapV3Factory= 0x1F98431c8aD98523631AE4a59f267346ea31F984;
    uint32 public constant movingAvgShortPeriod = 600;

    /**
     * @dev Verifies that the caller is the Vault.
     */
    modifier onlyVault() {
        require(msg.sender == vaultAddr, "Caller is not the Vault");
        _;
    }

    constructor(ISwapRouter _swapRouter, address _USDs, address _inputToken, address _intermediateToken, address _vaultAddr, uint24 _poolFee1, uint24 _poolFee2) public {
        swapRouter = _swapRouter;
        USDs = _USDs;
        inputToken = _inputToken;
        intermediateToken = _intermediateToken;
        poolFee1 = _poolFee1;
        poolFee2 = _poolFee2;
        vaultAddr = _vaultAddr;
    }


    function _getAmountOutExpected(uint256 amountIn) internal view returns (uint) {
        require(amountIn < uint128(-1), "amountIn too large");
        address poolAddr1 = IUniswapV3Factory(UniswapV3Factory).getPool(intermediateToken, inputToken, poolFee1);
        address poolAddr2 = IUniswapV3Factory(UniswapV3Factory).getPool(USDs, intermediateToken, poolFee2);
        uint32 longestSec1 = OracleLibrary.getOldestObservationSecondsAgo(poolAddr1);
        uint32 longestSec2 = OracleLibrary.getOldestObservationSecondsAgo(poolAddr2);
        uint32 period1 = movingAvgShortPeriod < longestSec1 ? movingAvgShortPeriod : longestSec1;
        uint32 period2 = movingAvgShortPeriod < longestSec2 ? movingAvgShortPeriod : longestSec2;
        int24 timeWeightedAverageTick1 = OracleLibrary.consult(poolAddr1, period1);
        int24 timeWeightedAverageTick2 = OracleLibrary.consult(poolAddr2, period2);
        uint quoteAmount1 = OracleLibrary.getQuoteAtTick(timeWeightedAverageTick1, uint128(amountIn), intermediateToken, inputToken);
        require(quoteAmount1 < uint128(-1), "quoteAmount1 too large");
        uint quoteAmount2 = OracleLibrary.getQuoteAtTick(timeWeightedAverageTick2, uint128(quoteAmount1), USDs, intermediateToken);
        return quoteAmount2;
    }

    /// @notice swapInputMultiplePools swaps a fixed amount of inputToken for a maximum possible amount of USDs through an intermediary pool.
    /// For this example, we will swap inputToken to intermediateToken, then intermediateToken to USDs to achieve our desired output.
    /// @dev The calling address must approve this contract to spend at least `amountIn` worth of its inputToken for this function to succeed.
    /// @param amountIn The amount of inputToken to be swapped.
    /// @return amountOut The amount of USDs received after the swap.
    function swap(uint256 amountIn) external onlyVault override returns (uint256 amountOut) {
        // Transfer `amountIn` of inputToken to this contract.
        TransferHelper.safeTransferFrom(inputToken, msg.sender, address(this), amountIn);

        // Approve the router to spend inputToken.
        TransferHelper.safeApprove(inputToken, address(swapRouter), amountIn);

        uint256 _amountOutMinimum = _getAmountOutExpected(amountIn) * 8 / 10;

        // Multiple pool swaps are encoded through bytes called a `path`. A path is a sequence of token addresses and poolFees that define the pools used in the swaps.
        // The format for pool encoding is (tokenIn, fee, tokenOut/tokenIn, fee, tokenOut) where tokenIn/tokenOut parameter is the shared token across the pools.
        // Since we are swapping inputToken to intermediateToken and then intermediateToken to USDs the path encoding is (inputToken, 0.3%, intermediateToken, 0.3%, USDs).
        ISwapRouter.ExactInputParams memory params =
            ISwapRouter.ExactInputParams({
                path: abi.encodePacked(inputToken, poolFee1, intermediateToken, poolFee2, USDs),
                recipient: msg.sender,
                deadline: block.timestamp,
                amountIn: amountIn,
                amountOutMinimum: _amountOutMinimum
            });

        // Executes the swap.
        amountOut = swapRouter.exactInput(params);
    }
}
