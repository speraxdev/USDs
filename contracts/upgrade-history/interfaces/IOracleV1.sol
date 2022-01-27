// used by OracleV1-3, TwoPoolStrategyV1, VaultCoreV1-4. VaultCoreToolsV1-3
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

interface IOracleV1 {
    function getCollateralPrice(address collateralAddr) external view returns (uint);
    function getUSDCprice() external view returns (uint);
    function getSPAprice() external view returns (uint);
    function getUSDsPrice() external view returns (uint);
    function getUSDsPrice_average() external view returns (uint);
    function getCollateralPrice_prec(address collateralAddr) external view returns (uint);
    function getUSDCprice_prec() external view returns (uint);
    function getSPAprice_prec() external view returns (uint);
    function getUSDsPrice_prec() external view returns (uint);
    function updateInOutRatio() external;
    function USDsInOutRatio() external view returns (uint);
    function USDsInOutRatio_prec() external view returns (uint32);
}
