// https://docs.uniswap.org/protocol/guides/swaps/single-swaps
//pragma solidity =0.7.6;
//pragma abicoder v2;
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import '../libraries/TransferHelper.sol';
import '../interfaces/ISwapRouter.sol';
import '../interfaces/IBuyback.sol';

contract BuybackSingle is IBuyback {
    using SafeERC20 for IERC20;

    ISwapRouter public immutable swapRouter;
    address public immutable USDs;
    address public immutable inputToken;
    uint24 public immutable poolFee;
    address public immutable vaultAddr;

    /**
     * @dev Verifies that the caller is the Vault.
     */
    modifier onlyVault() {
        require(msg.sender == vaultAddr, "Caller is not the Vault");
        _;
    }

    constructor(ISwapRouter _swapRouter, address _USDs, address _inputToken, address _vaultAddr, uint24 _poolFee) public {
        swapRouter = _swapRouter;
        USDs = _USDs;
        inputToken = _inputToken;
        poolFee = _poolFee;
        vaultAddr = _vaultAddr;
    }

    /// @notice swapExactInputSingle swaps a fixed amount of USDC for a maximum possible amount of USDs
    /// using the USDC/USDs 0.3% pool by calling `exactInputSingle` in the swap router.
    /// @dev The calling address must approve this contract to spend at least `amountIn` worth of its USDC for this function to succeed.
    /// @param amountIn The exact amount of USDC that will be swapped for USDs.
    /// @return amountOut The amount of USDs received.
    function swap(uint256 amountIn) external onlyVault override returns (uint256 amountOut) {
        // msg.sender must approve this contract
        // Transfer the specified amount of USDC to this contract.
        TransferHelper.safeTransferFrom(inputToken, msg.sender, address(this), amountIn);
        // Approve the router to spend USDC.
        TransferHelper.safeApprove(inputToken, address(swapRouter), amountIn);
        // Naively set amountOutMinimum to 0. In production, use an oracle or other data source to choose a safer value for amountOutMinimum.
        // We also set the sqrtPriceLimitx96 to be 0 to ensure we swap our exact input amount.
        ISwapRouter.ExactInputSingleParams memory params =
            ISwapRouter.ExactInputSingleParams({
                tokenIn: inputToken,
                tokenOut: USDs,
                fee: poolFee,
                recipient: msg.sender,
                deadline: block.timestamp,
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            });
        // The call to `exactInputSingle` executes the swap.
        amountOut = swapRouter.exactInputSingle(params);
        IERC20(USDs).safeTransfer(vaultAddr, amountOut);
    }
}
