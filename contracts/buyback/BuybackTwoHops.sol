// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.7;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import '@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol';
import '../libraries/TransferHelper.sol';
import '../libraries/OracleLibrary.sol';
import '../interfaces/ISwapRouter.sol';
import '../interfaces/IBuyback.sol';
import '../interfaces/IOracle.sol';

/**
 * @title buyback contract of USDs protocol
 * @notice swap an ERC20 with USDs using two pools on Uniswap V3
 * @dev reference: https://docs.uniswap.org/protocol/guides/swaps/multihop-swaps
 * @author Sperax Foundation
 */
contract BuybackTwoHops is IBuyback, Ownable {
    using SafeERC20 for IERC20;

    ISwapRouter public constant swapRouter = ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    address public immutable USDs;
    address public immutable vaultAddr;

    event Swap(address indexed inputToken, uint256 amountIn, uint256 amountOut);
    event InputTokenUpdated(address _inputTokenAddr, bool _supported, address _intermediateToken, uint24 _poolFee1, uint24 _poolFee2);

    /**
     * @dev Verifies that the caller is the Vault.
     */
    modifier onlyVault() {
        require(msg.sender == vaultAddr, "Caller is not the Vault");
        _;
    }

    struct inputTokenStruct {
		address inputTokenAddr;
		bool supported;
        address intermediateToken;
		uint24 poolFee1;
        uint24 poolFee2;
	}

    mapping(address => inputTokenStruct) public inputTokensInfo;

    constructor(address _USDs, address _vaultAddr)  {
        USDs = _USDs;
        vaultAddr = _vaultAddr;
    }

    /**
     * @notice set up an ERC20 token (_inputTokenAddr) to swap back USDs
     * @dev call this function with _supported set to true when adding an inputToken for the first time
     * @param _inputTokenAddr inputToken used to swap back USDs
     * @param _supported if this contract supports using inputToken used to swap back USDs
     * @param _intermediateToken the intermediateToken used for inputToken to USDs swapping
     * @param _poolFee1 poolFee of inputToken-intermediateToken
     * @param _poolFee2 poolFee of intermediateToken-USDs
     */
    function updateInputTokenInfo(address _inputTokenAddr, bool _supported, address _intermediateToken, uint24 _poolFee1, uint24 _poolFee2) external onlyOwner {
        inputTokenStruct storage addinginputToken = inputTokensInfo[_inputTokenAddr];
        addinginputToken.inputTokenAddr = _inputTokenAddr;
        addinginputToken.supported = _supported;
        addinginputToken.intermediateToken = _intermediateToken;
        addinginputToken.poolFee1 = _poolFee1;
        addinginputToken.poolFee2 = _poolFee2;
        emit InputTokenUpdated(_inputTokenAddr, _supported, _intermediateToken, _poolFee1, _poolFee2);
    }

    /**
     * @notice swaps a fixed amount of inputToken for a maximum possible amount of USDs through an intermediary pool.
     * @param inputToken the ERC20 token used to swap back USDs
     * @param amountIn the amount of inputToken to be swapped.
     * @return amountOut the amount of USDs received after the swap.
     */
    function swap(address inputToken, uint256 amountIn) external onlyVault override returns (uint256 amountOut) {
        require(inputTokensInfo[inputToken].supported, "inputToken not supported");
        address intermediateToken = inputTokensInfo[inputToken].intermediateToken;
        uint24 poolFee1 = inputTokensInfo[inputToken].poolFee1;
        uint24 poolFee2 = inputTokensInfo[inputToken].poolFee2;
        TransferHelper.safeApprove(inputToken, address(swapRouter), amountIn);
        // Multiple pool swaps are encoded through bytes called a `path`. A path is a sequence of token addresses and poolFees that define the pools used in the swaps.
        // The format for pool encoding is (tokenIn, fee, tokenOut/tokenIn, fee, tokenOut) where tokenIn/tokenOut parameter is the shared token across the pools.
        // Since we are swapping inputToken to intermediateToken and then intermediateToken to USDs the path encoding is (inputToken, poolFee1, intermediateToken, poolFee2, USDs).
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
