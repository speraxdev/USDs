// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

interface IBuyback {
    function swap(address inputToken, uint amountIn) external returns (uint);
}
