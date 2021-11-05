//pragma solidity =0.7.6;
//pragma abicoder v2;
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import '../libraries/TransferHelper.sol';
import '../interfaces/ISwapRouter.sol';
import '../interfaces/IBuyback.sol';

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

        // Multiple pool swaps are encoded through bytes called a `path`. A path is a sequence of token addresses and poolFees that define the pools used in the swaps.
        // The format for pool encoding is (tokenIn, fee, tokenOut/tokenIn, fee, tokenOut) where tokenIn/tokenOut parameter is the shared token across the pools.
        // Since we are swapping inputToken to intermediateToken and then intermediateToken to USDs the path encoding is (inputToken, 0.3%, intermediateToken, 0.3%, USDs).
        ISwapRouter.ExactInputParams memory params =
            ISwapRouter.ExactInputParams({
                path: abi.encodePacked(inputToken, poolFee1, intermediateToken, poolFee2, USDs),
                recipient: msg.sender,
                deadline: block.timestamp,
                amountIn: amountIn,
                amountOutMinimum: 0
            });

        // Executes the swap.
        amountOut = swapRouter.exactInput(params);
        IERC20(USDs).safeTransfer(vaultAddr, amountOut);
    }
}
