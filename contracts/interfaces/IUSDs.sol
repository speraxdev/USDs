pragma solidity ^0.6.12;

interface IUSDs {
    function mint(address _account, uint256 _amount) external;
    function burn(address _account, uint256 _amount) external;
    function changeSupply(uint256 _newTotalSupply) external;
    function totalMinted() external returns (uint256);
    function totalBurnt() external returns (uint256);
}
