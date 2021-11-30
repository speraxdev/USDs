// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockToken is ERC20 {
    constructor() public ERC20("Mock Token", "MockT") {
        uint256 amount = 100000 * 10 ** 18;
        _mint(msg.sender, amount );
        ERC20.transfer(msg.sender, amount);
    }
}