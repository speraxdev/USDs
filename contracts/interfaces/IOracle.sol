pragma solidity ^0.6.12;

interface IOracle {
    event Update(uint currPriceMA7, uint currPricetime);

    function lastUpdateTime() external view returns (uint32);
    function period() external view returns (uint32);
    function token0PriceMA() external view returns (uint);
    function update() external;
    function collatPrice(address tokenAddr) external view returns (int);
    function getSPAPrice() external view returns (int);
    function getUSDsPrice() external view returns (int);
    function ETHPricePrecision() external view returns (uint);
    function collatPricePrecision(address tokenAddr) external view returns (uint);
    function SPAPricePrecision() external view returns (uint);
    function USDsPricePrecision() external view returns (uint);
}
