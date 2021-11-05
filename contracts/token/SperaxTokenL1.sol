
// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import "@openzeppelin/contracts/access/Ownable.sol";
import "arb-bridge-peripherals/contracts/tokenbridge/ethereum/gateway/L1CustomGateway.sol";
import "arb-bridge-peripherals/contracts/tokenbridge/ethereum/gateway/L1GatewayRouter.sol";
import "arb-bridge-peripherals/contracts/tokenbridge/ethereum/ICustomToken.sol";
import { SperaxToken } from "./SperaxToken.sol";

contract SperaxTokenL1 is Ownable, ICustomToken {
    address public spaAddress;
    address public bridge;
    address public router;
    bool private shouldRegisterGateway;

    constructor(address _spaAddress) public {
        spaAddress = _spaAddress;
    }

    /**
     * @dev mint SPA when USDs is burnt
     */
    function mintForUSDs(address account, uint256 amount) external {
        SperaxToken(spaAddress).mintForUSDs(account, amount);
    }

    /**
     * @dev Destroys `amount` tokens from the caller.
     *
     * See {ERC20-_burn}.
     */
    function burn(uint256 amount) public {
        SperaxToken(spaAddress).burnFrom(_msgSender(), amount);
    }

    /**
     * @dev Destroys `amount` tokens from `account`, deducting from the caller's
     * allowance.
     *
     * See {ERC20-_burn} and {ERC20-allowance}.
     *
     * Requirements:
     *
     * - the caller must have allowance for ``accounts``'s tokens of at least
     * `amount`.
     */
    function burnFrom(address account, uint256 amount) public {
        SperaxToken(spaAddress).burnFrom(_msgSender(), amount);
    }


    /**
     * @dev View `account` locked information
     */
    function timelockOf(address account) public view returns(uint256 releaseTime, uint256 amount) {
        return SperaxToken(spaAddress).timelockOf(account);
    }

    /**
     * @dev Transfer to the "recipient" some specified 'amount' that is locked until "releaseTime"
     * @notice only Owner call
     */
    function transferWithLock(address recipient, uint256 amount, uint256 releaseTime) public onlyOwner returns (bool) {
        return SperaxToken(spaAddress).transferWithLock(recipient, amount, releaseTime);
    }

    /**
     * @dev Release the specified `amount` of locked amount
     * @notice only Owner call
     */
    function release(address account, uint256 releaseAmount) public onlyOwner {
        SperaxToken(spaAddress).release(account, releaseAmount);
    }

    /**
     * @dev Triggers stopped state.
     * @notice only Owner call
     */
    function pause() public onlyOwner {
        SperaxToken(spaAddress).pause();
    }

    /**
     * @dev Returns to normal state.
     * @notice only Owner call
     */
    function unpause() public onlyOwner {
        SperaxToken(spaAddress).unpause();
    }

    /**
     * @dev Triggers stopped state of mint.
     * @notice only Owner call
     */
    function mintPause() public onlyOwner {
        SperaxToken(spaAddress).mintPause();
    }

    /**
     * @dev Returns to normal state of mint.
     * @notice only Owner call
     */
    function mintUnpause() public onlyOwner {
        SperaxToken(spaAddress).mintUnpause();
    }

    /**
     * @dev Batch transfer amount to recipient
     * @notice that excessive gas consumption causes transaction revert
     */
    function batchTransfer(address[] memory recipients, uint256[] memory amounts) public {
        SperaxToken(spaAddress).batchTransfer(recipients, amounts);
    }

    // Arbitrum


    function balanceOf(address account)
        public
        view
        override(ICustomToken)
        returns (uint256)
    {
        return SperaxToken(spaAddress).balanceOf(account);
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) public override(ICustomToken) returns (bool) {
        return SperaxToken(spaAddress).transferFrom(sender, recipient, amount);
    }

    /// @dev we only set shouldRegisterGateway to true when in `registerTokenOnL2`
    function isArbitrumEnabled() external view override returns (uint8) {
        require(shouldRegisterGateway, "NOT_EXPECTED_CALL");
        return uint8(0xa4b1);
    }

    /**
     * @dev change the arbitrum bridge address
     * @param newBridge the new bridge address
     * @param newRouter the new router address
     */
    function changeArbToken(address newBridge, address newRouter) external onlyOwner {
        bridge = newBridge;
        router = newRouter;
    }

    function changeSpaAddress(address newSPA) external onlyOwner {
        spaAddress = newSPA;
    }
  
    function registerTokenOnL2(
        address l2CustomTokenAddress,
        uint256 maxSubmissionCostForCustomBridge,
        uint256 maxSubmissionCostForRouter,
        uint256 maxGas,
        uint256 gasPriceBid,
        address creditBackAddress
    ) public override {
        // we temporarily set `shouldRegisterGateway` to true for the callback in registerTokenToL2 to succeed
        bool prev = shouldRegisterGateway;
        shouldRegisterGateway = true;

        L1CustomGateway(bridge).registerTokenToL2(
            l2CustomTokenAddress,
            maxGas,
            gasPriceBid,
            maxSubmissionCostForCustomBridge,
            creditBackAddress
        );

        L1GatewayRouter(router).setGateway(
            bridge,
            maxGas,
            gasPriceBid,
            maxSubmissionCostForRouter,
            creditBackAddress
        );

        shouldRegisterGateway = prev;
    }
}