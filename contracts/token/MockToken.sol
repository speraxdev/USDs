// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "../token/ERC20WithDecimals.sol";
contract MockToken is ERC20WithDecimals {
    constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_
    ) 
    
     public ERC20(name_, symbol_)
            ERC20WithDecimals(decimals_)
    
     {
        uint256 amount = 10000000000 * (10 ** uint(decimals_));
         _mint(_msgSender(), amount);
    }
}
