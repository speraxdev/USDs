// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
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
contract Buyback is IBuyback, Ownable {
    using SafeERC20 for IERC20;

    ISwapRouter public constant swapRouter = ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    address public immutable USDs;
    address public immutable vaultAddr;

    event Swap(address indexed inputToken, uint256 amountIn, uint256 amountOut);
    event InputTokenUpdated(
        address _inputTokenAddr,
        bool _supported,
        uint8 _hopNum,
        address _intermediateToken1,
        address _intermediateToken2,
        uint24 _poolFee1,
        uint24 _poolFee2,
        uint24 _poolFee3
     );

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
        uint8 hopNum;
        address intermediateToken1;
        address intermediateToken2;
		uint24 poolFee1;
        uint24 poolFee2;
        uint24 poolFee3;
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
     * @param _hopNum num of hops used to swap inputToken to USDs
     * @param _intermediateToken1 the first intermediateToken used for inputToken to USDs swapping
     * @param _intermediateToken2 the second intermediateToken used for inputToken to USDs swapping
     * @param _poolFee1 poolFee of inputToken-intermediateToken1
     * @param _poolFee2 poolFee of intermediateToken1-intermediateToken2
     * @param _poolFee3 poolFee of intermediateToken2-USDs
     */
    function updateInputTokenInfo(
        address _inputTokenAddr,
        bool _supported,
        uint8 _hopNum,
        address _intermediateToken1,
        address _intermediateToken2,
        uint24 _poolFee1,
        uint24 _poolFee2,
        uint24 _poolFee3
    ) external onlyOwner {
        _hopSettingCheck(
            _hopNum,
            _intermediateToken1,
            _intermediateToken2,
            _poolFee1,
            _poolFee2,
            _poolFee3
        );
        inputTokenStruct storage addinginputToken = inputTokensInfo[_inputTokenAddr];
        addinginputToken.inputTokenAddr = _inputTokenAddr;
        addinginputToken.supported = _supported;
        addinginputToken.hopNum = _hopNum;
        addinginputToken.intermediateToken1 = _intermediateToken1;
        addinginputToken.intermediateToken2 = _intermediateToken2;
        addinginputToken.poolFee1 = _poolFee1;
        addinginputToken.poolFee2 = _poolFee2;
        addinginputToken.poolFee3 = _poolFee3;
        emit InputTokenUpdated(
            _inputTokenAddr,
            _supported,
            _hopNum,
            _intermediateToken1,
            _intermediateToken2,
            _poolFee1,
            _poolFee2,
            _poolFee3
        );
    }

    /**
     * @notice swaps a fixed amount of inputToken for a maximum possible amount of USDs through an intermediary pool.
     * @param inputToken the ERC20 token used to swap back USDs
     * @param amountIn the amount of inputToken to be swapped.
     * @return amountOut the amount of USDs received after the swap.
     */
    function swap(address inputToken, uint256 amountIn) external onlyVault override returns (uint256 amountOut) {
        require(inputTokensInfo[inputToken].supported, "inputToken not supported");
        uint8 hopNum = inputTokensInfo[inputToken].hopNum;
        address intermediateToken1 = inputTokensInfo[inputToken].intermediateToken1;
        address intermediateToken2 = inputTokensInfo[inputToken].intermediateToken2;
        uint24 poolFee1 = inputTokensInfo[inputToken].poolFee1;
        uint24 poolFee2 = inputTokensInfo[inputToken].poolFee2;
        uint24 poolFee3 = inputTokensInfo[inputToken].poolFee3;
        TransferHelper.safeApprove(inputToken, address(swapRouter), amountIn);
        if (hopNum == 1) {
            ISwapRouter.ExactInputSingleParams memory params =
                ISwapRouter.ExactInputSingleParams({
                    tokenIn: inputToken,
                    tokenOut: USDs,
                    fee: poolFee1,
                    recipient: msg.sender,
                    deadline: block.timestamp,
                    amountIn: amountIn,
                    amountOutMinimum: 0,
                    sqrtPriceLimitX96: 0
                });
            amountOut = swapRouter.exactInputSingle(params);
        } else {
            bytes memory swapPath;
            if (hopNum == 2) {
                swapPath = abi.encodePacked(
                    inputToken,
                    poolFee1,
                    intermediateToken1,
                    poolFee2,
                    USDs
                );
            } else if (hopNum == 3) {
                swapPath = abi.encodePacked(
                    inputToken,
                    poolFee1,
                    intermediateToken1,
                    poolFee2,
                    intermediateToken2,
                    poolFee3,
                    USDs
                );
            } else {
                revert('Unsupported number of hops detected');
            }
            ISwapRouter.ExactInputParams memory params =
                ISwapRouter.ExactInputParams({
                    path: swapPath,
                    recipient: msg.sender,
                    deadline: block.timestamp,
                    amountIn: amountIn,
                    amountOutMinimum: 0
                });
            // Executes the swap.
            amountOut = swapRouter.exactInput(params);
        }
        TransferHelper.safeApprove(inputToken, address(swapRouter), amountOut);

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

    /**
     * @notice check if unnecessary intermediateToken address or pool fee has
               been defined (as non zero) based on the number of hops
     * @dev for hopNum 1 and 2, intermediateToken2 and poolFee3 should be 0
            for hopNum 1, intermediateToken1 and poolFee2 should be 0 as well
     * @param _hopNum num of hops used to swap inputToken to USDs
     * @param _intermediateToken1 the first intermediateToken used for inputToken to USDs swapping
     * @param _intermediateToken2 the second intermediateToken used for inputToken to USDs swapping
     * @param _poolFee1 poolFee of inputToken-intermediateToken1
     * @param _poolFee2 poolFee of intermediateToken1-intermediateToken2
     * @param _poolFee3 poolFee of intermediateToken2-USDs
     */
    function _hopSettingCheck(
        uint8 _hopNum,
        address _intermediateToken1,
        address _intermediateToken2,
        uint24 _poolFee1,
        uint24 _poolFee2,
        uint24 _poolFee3
    ) internal {
        require(_hopNum <= 3, "Supports at most 3 hops");
        require(_hopNum > 0, "hopNum has to be a positive number");
        require(_poolFee1 != 0, "_poolFee1 should be specified in all cases");
        if (_hopNum == 1) {
            require(
                _intermediateToken1 == address(0) &&
                _intermediateToken2 == address(0) &&
                _poolFee2 == 0 &&
                _poolFee3 == 0,
                "hopNum, intermediateToken, poolFee settings not matched"
            );
        } else if (_hopNum == 2) {
            require(
                _intermediateToken1 != address(0) &&
                _intermediateToken2 == address(0) &&
                _poolFee2 != 0 &&
                _poolFee3 == 0,
                "hopNum, intermediateToken, poolFee settings not matched"
            );
        } else if (_hopNum == 3) {
            require(
                _intermediateToken1 != address(0) &&
                _intermediateToken2 != address(0) &&
                _poolFee2 != 0 &&
                _poolFee3 != 0,
                "hopNum, intermediateToken, poolFee settings not matched"
            );
        }
    }
}
