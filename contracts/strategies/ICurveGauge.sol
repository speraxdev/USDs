// SPDX-License-Identifier: agpl-3.0
//pragma solidity ^0.8.0;
pragma solidity ^0.8.7;

interface ICurveGauge {
    function balanceOf(address account) external view returns (uint256);

    function deposit(uint256 _value) external;

    function withdraw(uint256 value) external;

    function claim_rewards(address _addr, address _receiver) external;
}
