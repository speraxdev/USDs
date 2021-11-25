// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import '@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol';
import "@openzeppelin/contracts/access/Ownable.sol";
import '../libraries/TransferHelper.sol';
import '../libraries/OracleLibrary.sol';
import '../interfaces/ISwapRouter.sol';
import '../interfaces/IBuyback.sol';
import '../interfaces/IOracle.sol';


/**
 * @title buyback contract of USDs protocol
 * @notice swap an ERC20 with USDs using one pool on Uniswap V3
 * @dev reference: https://docs.uniswap.org/protocol/guides/swaps/single-swaps
 * @author Sperax Foundation
 */
contract BuybackSingle is IBuyback, Ownable {
    using SafeERC20 for IERC20;

    ISwapRouter public constant swapRouter = ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    address public immutable USDs;
    address public immutable vaultAddr;

    event Swap(address indexed inputToken, uint256 amountIn, uint256 amountOut);
    event InputTokenUpdated(address _inputTokenAddr, bool _supported, uint24 _poolFee);

    /**
     * @dev Verifies that the caller is the Vault.
     */
    modifier onlyVault() {
        require(msg.sender == vaultAddr, "caller is not the vault");
        _;
    }

    struct inputTokenStruct {
		address inputTokenAddr;
		bool supported;
		uint24 poolFee;
	}

    mapping(address => inputTokenStruct) public inputTokensInfo;

    constructor(address _USDs, address _vaultAddr) public {
        USDs = _USDs;
        vaultAddr = _vaultAddr;
    }

    /**
     * @notice set up an ERC20 token (_inputTokenAddr) to swap back USDs
     * @dev call this function with _supported set to true when adding an inputToken for the first time
     * @param _inputTokenAddr inputToken used to swap back USDs
     * @param _supported if this contract supports using inputToken used to swap back USDs
     * @param _poolFee poolFee of intermediateToken-USDs
     */
    function updateInputTokenInfo(address _inputTokenAddr, bool _supported, uint24 _poolFee) external onlyOwner {
        inputTokenStruct storage addinginputToken = inputTokensInfo[_inputTokenAddr];
        addinginputToken.inputTokenAddr = _inputTokenAddr;
        addinginputToken.supported = _supported;
        addinginputToken.poolFee = _poolFee;
        emit InputTokenUpdated(_inputTokenAddr, _supported, _poolFee);
    }

    /**
	 * @notice swaps a fixed amount of inputToken for a maximum possible amount of USDs on Uniswap V3
     * @param inputToken the ERC20 token used to swap back USDs
     * @param amountIn the exact amount of inputToken that will be swapped for USDs
     * @return amountOut The amount of USDs received
     */
    function swap(address inputToken, uint256 amountIn) external onlyVault override returns (uint256 amountOut) {
        require(inputTokensInfo[inputToken].supported, "inputToken not supported");
        uint24 poolFee = inputTokensInfo[inputToken].poolFee;
        TransferHelper.safeApprove(inputToken, address(swapRouter), amountIn);
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
        // Executes the swap.
        amountOut = swapRouter.exactInputSingle(params);
        emit Swap(inputToken, amountIn, amountOut);
    }

    /**
     * @notice withdraw inputToken back to vault in case some inputToken were not spent
     * @param inputToken the ERC20 token used to swap back USDs
     * @param amount the exact amount of inputToken to withdraw back to vault
     */
    function withdrawToVault(address inputToken, uint256 amount) external onlyOwner {
        IERC20(inputToken).safeTransfer(vaultAddr, amount);
    }
}
