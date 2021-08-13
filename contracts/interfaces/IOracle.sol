pragma solidity ^0.6.12;

interface IOracle {
    event Update(uint currPriceMA7, uint currPricetime);

    function lastUpdateTime() external view returns (uint32);
    function period() external view returns (uint32);
    function token0PriceMA() external view returns (uint);
    function update() external;
    function collatPrice(address tokenAddr) external view returns (uint);
    function getSPAPrice() external view returns (uint);
    function getUSDsPrice() external returns (uint);
    function getUSDsPrice_Average() external returns (uint);
    function getETHPrice() external view returns (uint);
    function getAssetPrice(address assetAddress) external view returns (uint);
    function ETHPricePrecision() external view returns (uint);
    function collatPricePrecision(address tokenAddr) external view returns (uint);
    function SPAPricePrecision() external view returns (uint);
    function USDsPricePrecision() external view returns (uint);
    function USDsInOutRatio() external view returns (uint);
    function USDsInOutRatioPrecision() external view returns (uint);
}
