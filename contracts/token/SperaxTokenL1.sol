// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "arb-bridge-peripherals/contracts/tokenbridge/ethereum/gateway/L1CustomGateway.sol";
import "arb-bridge-peripherals/contracts/tokenbridge/ethereum/gateway/L1GatewayRouter.sol";
import "arb-bridge-peripherals/contracts/tokenbridge/ethereum/ICustomToken.sol";

interface OrinigalSPA {
    function mintForUSDs(address account, uint256 amount) external;
}

contract SperaxTokenL1 is ERC20, Ownable, ICustomToken {
    address public spaAddress;
    address public bridge;
    address public router;
    bool private shouldRegisterGateway;

    constructor(string memory name_, string memory symbol_, address _spaAddress) ERC20(name_, symbol_) public {
        spaAddress = _spaAddress;
    }

    /**
     * @dev See {IERC20-totalSupply}.
     */
    function totalSupply() public view override returns (uint256) {
        return IERC20(spaAddress).totalSupply();
    }

    function balanceOf(address account)
        public
        view
        override(ERC20, ICustomToken)
        returns (uint256)
    {
        return IERC20(spaAddress).balanceOf(account);
    }

    function transfer(address recipient, uint256 amount) public override returns (bool) {
        (bool success, bytes memory result) = spaAddress.delegatecall(abi.encodeWithSignature("increaseAllowance(address,uint256)", recipient, amount));
        return abi.decode(result, (bool));
    }

    /**
     * @dev See {IERC20-allowance}.
     */
    function allowance(address owner, address spender) public view override returns (uint256) {
        return IERC20(spaAddress).allowance(owner, spender);
    }

    function approve(address spender, uint256 amount) public override returns (bool) {
        (bool success, bytes memory result) = spaAddress.delegatecall(abi.encodeWithSignature("approve(address,uint256)", spender, amount));
        return abi.decode(result, (bool));
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) public override(ERC20, ICustomToken) returns (bool) {
        (bool success, bytes memory result) = spaAddress.delegatecall(abi.encodeWithSignature("transferFrom(address,address,uint256)", sender, recipient, amount));
        return abi.decode(result, (bool));
    }

    function increaseAllowance(address spender, uint256 addedValue) public override returns (bool) {
        (bool success, bytes memory result) = spaAddress.delegatecall(abi.encodeWithSignature("increaseAllowance(address,uint256)", spender, addedValue));
        return abi.decode(result, (bool));
    }

    function decreaseAllowance(address spender, uint256 subtractedValue) public override returns (bool) {
        (bool success, bytes memory result) = spaAddress.delegatecall(abi.encodeWithSignature("increaseAllowance(address,uint256)", spender, subtractedValue));
        return abi.decode(result, (bool));
    }

    modifier onlyGateway() {
        require(msg.sender == bridge, "ONLY_GATEWAY");
        _;
    }

    /**
     * @dev mint SPA
     */
    function bridgeMint(address account, uint256 amount) onlyGateway external {
        OrinigalSPA(spaAddress).mintForUSDs(account, amount);
    }

    // Arbitrum
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
