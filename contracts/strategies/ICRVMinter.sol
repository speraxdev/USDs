// SPDX-License-Identifier: agpl-3.0
//pragma solidity ^0.8.0;
pragma solidity ^0.6.12;

interface ICRVMinter {
    function mint(address gaugeAddress) external;
}
