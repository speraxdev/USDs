pragma solidity ^0.6.12;

interface IOracle {
    event Update(uint256 currPriceMA7, uint256 currPricetime);

    function token1PriceMA7() external view returns (uint256);
    function lastTime() external view returns (uint32);
    // the format of lastTime complies with UniswapV2's uint32 format

}
