// used by USDsL2V1-2, VaultCoreV1-4
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

interface IUSDsV1 {
    function mint(address _account, uint256 _amount) external;
    function burn(address _account, uint256 _amount) external;
    function changeSupply(uint256 _newTotalSupply) external;
    function mintedViaUsers() external view returns (uint256);
    function burntViaUsers() external view returns (uint256);
}
