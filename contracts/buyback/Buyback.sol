//pragma solidity =0.7.6;
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import '../libraries/TransferHelper.sol';
import '../interfaces/ISwapRouter.sol';
import '../interfaces/IBuyback.sol';

contract Buyback is IBuyback {
    ISwapRouter public immutable swapRouter;
    address public immutable USDsAddr;
    address public constant USDCaddr = 0x2F375e94FC336Cdec2Dc0cCB5277FE59CBf1cAe5;
    address public immutable vaultAddr;
    // For this example, we will set the pool fee to 0.05%.
    uint24 public constant poolFee = 500;

    /**
     * @dev Verifies that the caller is the Vault.
     */
    modifier onlyVault() {
        require(msg.sender == vaultAddr, "Caller is not the Vault");
        _;
    }

    constructor(ISwapRouter _swapRouter, address _USDsAddr, address _vaultAddr) public {
        swapRouter = _swapRouter;
        USDsAddr = _USDsAddr;
        vaultAddr = _vaultAddr;
    }

    /// @notice swapExactInputSingle swaps a fixed amount of USDC for a maximum possible amount of USDs
    /// using the USDC/USDs 0.3% pool by calling `exactInputSingle` in the swap router.
    /// @dev The calling address must approve this contract to spend at least `amountIn` worth of its USDC for this function to succeed.
    /// @param amountIn The exact amount of USDC that will be swapped for USDs.
    /// @return amountOut The amount of USDs received.
    function swapExactInputSingle(uint256 amountIn) external onlyVault override returns (uint256 amountOut) {
        // msg.sender must approve this contract
        // Transfer the specified amount of USDC to this contract.
        TransferHelper.safeTransferFrom(USDCaddr, msg.sender, address(this), amountIn);
        // Approve the router to spend USDC.
        TransferHelper.safeApprove(USDCaddr, address(swapRouter), amountIn);
        // Naively set amountOutMinimum to 0. In production, use an oracle or other data source to choose a safer value for amountOutMinimum.
        // We also set the sqrtPriceLimitx96 to be 0 to ensure we swap our exact input amount.
        ISwapRouter.ExactInputSingleParams memory params =
            ISwapRouter.ExactInputSingleParams({
                tokenIn: USDCaddr,
                tokenOut: USDsAddr,
                fee: poolFee,
                recipient: msg.sender,
                deadline: block.timestamp,
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            });
        // The call to `exactInputSingle` executes the swap.
        amountOut = swapRouter.exactInputSingle(params);
    }
}
