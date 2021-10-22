// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

interface IBuyback {
    function swapExactInputSingle(uint amountIn) external returns (uint);
}
