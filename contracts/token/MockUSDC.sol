// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockUSDC is ERC20 {
    constructor() public ERC20("Mock USDC", "MockUSDC") {
        uint256 amount = 10000 * 10 ** 18;
        _mint(msg.sender, amount );
        ERC20.transfer(msg.sender, amount);
    }
}