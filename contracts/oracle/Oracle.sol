// SPDX-License-Identifier: MIT
// To-do: change BaseTokenAddr
pragma solidity ^0.6.12;
pragma experimental ABIEncoderV2; //What's this for?


import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";

import "../token/USDs.sol";
import "../interfaces/AggregatorV3Interface.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IUniswapV2Pair.sol";
import "../libraries/UniswapV2OracleLibrary.sol";
import "../libraries/OracleLibrary.sol";

/**
 * @title Oracle - the oracle contract for Spark
 * @author Sperax Dev Team
 * @notice this contract gets data from UniswapV2 pair and feed these data into the main contact of Spark, i.e. Spark.sol
 * @dev this contract draws insights from "ExampleOracleSimple.sol" by UniswapV2 team
 */

contract Oracle is Initializable, IOracle, OwnableUpgradeable {
    using SafeMathUpgradeable for *;
    using OracleLibrary for *;

    uint public override USDsInOutRatio; // USDsInOutRatio is accurate after 24 hours (one iteration)
    uint public override USDsInOutRatio_prec;
    uint8 public constant FREQUENCY = 24;
    uint32 public updateNextIndex;
    uint32 public lastUpdateTime; // the timstamp of the lastest update
    uint32 public updatePeriod; // the default updatePeriod of one update is 1 hours
    uint public ETHprice_prec;
    uint public SPAprice_prec;
    uint public USDsPrice_prec;
    AggregatorV3Interface priceFeedETH;
    address public SPAaddr;
    address public USDsAddr;
    address public constant WETH9 = 0xd0A1E359811322d97991E03f863a0C30C2cF029C;
    address public USDsOraclePool;
    address public SPAoracleBaseTokenAddr;
    address public USDsOracleBaseTokenAddr;

    event USDsInOutRatioUpdated(
        uint USDsInOutRatio,
        uint USDsOutflow_average,
        uint USDsInflow_average,
        uint32 timeStamp,
        uint index
    );
    event updatePeriodChanged(
        uint32 newPeriod
    );
    event collateralInfoChanged(
        address _collateralAddr,
        bool _supported,
        AggregatorV3Interface _priceFeed,
        uint _price_prec
    );

    uint[FREQUENCY+1] public USDsInflow;
    uint[FREQUENCY+1] public USDsOutflow;
    mapping (address => collateralStruct) collateralsInfo;
    struct collateralStruct {
        address collateralAddr;
        bool supported;
        AggregatorV3Interface priceFeed;
        uint price_prec;
    }

    //
    // Initializer
    //
    function initialize(
        address _USDsAddr
    ) public initializer {
        OwnableUpgradeable.__Ownable_init();
        updatePeriod = 1 hours;
        USDsAddr = _USDsAddr;
        USDsInOutRatio_prec = 10000000; // Note: need to be less than (2^32 - 1)
        lastUpdateTime = uint32(now % 2 ** 32);
        SPAoracleBaseTokenAddr = WETH9;
        USDsOracleBaseTokenAddr = 0x2F375e94FC336Cdec2Dc0cCB5277FE59CBf1cAe5; //USDC Address
        priceFeedETH = AggregatorV3Interface(0x9326BFA02ADD2366b30bacB125260Af641031331);
        ETHprice_prec = 10**8;
        USDsPrice_prec = 10**18;
        SPAprice_prec = 10**8;
    }

    /**
     * @notice change updatePeriod
     * @dev the frequency of update always remains the same
     * @param newPeriod new minimal updatePeriod in between two updates
     */
    function changePeriod(uint32 newPeriod) external onlyOwner {
        updatePeriod = newPeriod;
        emit updatePeriodChanged(updatePeriod);
    }

    function updateCollateralInfo(address _collateralAddr, bool _supported, AggregatorV3Interface _priceFeed, uint _price_prec) external onlyOwner {
        collateralStruct storage updatedCollateral = collateralsInfo[_collateralAddr];
        updatedCollateral.collateralAddr = _collateralAddr;
        updatedCollateral.supported = _supported;
        updatedCollateral.priceFeed = _priceFeed;
        updatedCollateral.price_prec = _price_prec;
        emit collateralInfoChanged(_collateralAddr, _supported, _priceFeed, _price_prec);
    }

    /**
     * @notice update the price of token0 to the latest
     * @dev the price would be updated only once per updatePeriod time
     * @dev USDsInOutRatio is accurate after 24 hours (one iteration)
     */
    function updateInOutRatio() external override {
        uint32 currTime = uint32(now % 2 ** 32);
        uint32 timeElapsed = currTime - lastUpdateTime;
        require(currTime >= lastUpdateTime, "updateInOutRatio; error last update happened in the future");
        require(timeElapsed >= updatePeriod, "updateInOutRatio: the time elapsed is too short.");
        uint32 indexNew = updateNextIndex;
        uint32 indexOld = (indexNew + 1) % (FREQUENCY+1);
        USDsInflow[indexNew] = USDs(USDsAddr)._totalMinted();
        USDsOutflow[indexNew] = USDs(USDsAddr)._totalBurnt();
        uint USDsInflow_average = USDsInflow[indexNew].sub(USDsInflow[indexOld]);
        uint USDsOutflow_average = USDsOutflow[indexNew].sub(USDsOutflow[indexOld]);
        if (USDsInOutRatio == 0) {
            USDsInOutRatio = USDsInOutRatio_prec;
        } else {
            USDsInOutRatio = USDsOutflow_average.mul(USDsInOutRatio_prec).div(USDsInflow_average);
        }
        lastUpdateTime = currTime;
        updateNextIndex = indexOld;
        emit USDsInOutRatioUpdated(USDsInOutRatio, USDsOutflow_average, USDsInflow_average, lastUpdateTime, indexNew);
    }

    function getCollateralPrice(address collateralAddr) external view override returns (uint) {
        collateralStruct memory  collateralInfo = collateralsInfo[collateralAddr];
        require(collateralInfo.supported, "getCollateralPrice: Collateral not supported.");
        return _getCollateralPrice(collateralAddr);
    }

    function getETHprice() external view override returns (uint) {
        return _getETHprice();
	}

    function getSPAprice() external view override returns (uint) {
        int24 timeWeightedAverageTick = USDsOraclePool.consult(3600);
        //To-DO: confirm 1 or 10^18
        uint quoteAmount = timeWeightedAverageTick.getQuoteAtTick(10**18, SPAaddr, SPAoracleBaseTokenAddr);
        uint SPAPrice = _getETHprice().mul(SPAprice_prec).mul(quoteAmount).div(ETHprice_prec);
        return SPAPrice;
    }

    function getUSDsPrice() external view override returns (uint) {
        int24 timeWeightedAverageTick = USDsOraclePool.consult(3600);
        //To-DO: confirm 1 or 10^18
        uint quoteAmount = timeWeightedAverageTick.getQuoteAtTick(10**18, USDsAddr, USDsOracleBaseTokenAddr);
        uint USDsPrice = _getCollateralPrice(USDsOracleBaseTokenAddr).mul(USDsPrice_prec).mul(quoteAmount).div(_getCollateralPrice_prec(USDsOracleBaseTokenAddr));
        return USDsPrice;
    }

    function getUSDsPrice_average() external view override returns (uint) {
        int24 timeWeightedAverageTick = USDsOraclePool.consult(86400);
        //To-DO: confirm 1 or 10^18
        uint quoteAmount = timeWeightedAverageTick.getQuoteAtTick(10**18, USDsAddr, USDsOracleBaseTokenAddr);
        uint USDsPrice_average = _getCollateralPrice(USDsOracleBaseTokenAddr).mul(USDsPrice_prec).mul(quoteAmount).div(_getCollateralPrice_prec(USDsOracleBaseTokenAddr));
        return USDsPrice_average;
    }

    function getCollateralPrice_prec(address collateralAddr) external view override returns (uint) {
        collateralStruct memory  collateralInfo = collateralsInfo[collateralAddr];
        require(collateralInfo.supported, "getCollateralPrice_prec: Collateral not supported.");
        return _getCollateralPrice_prec(collateralAddr);
    }

    function getETHprice_prec() external view override returns (uint) {
        return ETHprice_prec;
    }

    function getSPAprice_prec() external view override returns (uint) {
        return SPAprice_prec;
    }

    function getUSDsPrice_prec() external view override returns (uint) {
        return USDsPrice_prec;
    }

    function _getCollateralPrice(address collateralAddr) internal view returns (uint) {
        collateralStruct memory  collateralInfo = collateralsInfo[collateralAddr];
        require(collateralInfo.supported, "_getCollateralPrice: Collateral not supported.");
        (
            ,
            int price,
            ,
            ,
        ) = collateralInfo.priceFeed.latestRoundData();
        return uint(price);
    }


	function _getETHprice() internal view returns (uint) {
		(
            ,
            int price,
            ,
            ,
		) = priceFeedETH.latestRoundData();
		return uint(price);
	}

    function _getCollateralPrice_prec(address collateralAddr) internal view returns (uint) {
        collateralStruct memory  collateralInfo = collateralsInfo[collateralAddr];
        require(collateralInfo.supported, "_getCollateralPrice_prec: Collateral not supported.");
        return collateralInfo.price_prec;
	}


}
