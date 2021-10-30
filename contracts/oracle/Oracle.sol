// SPDX-License-Identifier: MIT
// To-do: remove for testing purpose functions;
// To-do: check USDsInOutRatio_prec;
pragma solidity >=0.6.12;
//pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
//import "../libraries/openzeppelin/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";

import "../vault/VaultCore.sol";
import "../interfaces/AggregatorV3Interface.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IUSDs.sol";
//import "@uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol";
import "../libraries/OracleLibrary.sol";

/**
 * @title Oracle - the oracle contract for Spark
 * @author Sperax Dev Team
 * @notice this contract gets data from UniswapV2 pair and feed these data into the main contact of Spark, i.e. Spark.sol
 * @dev this contract draws insights from "ExampleOracleSimple.sol" by UniswapV2 team
 */

contract Oracle is Initializable, IOracle, OwnableUpgradeable {
    using SafeMathUpgradeable for uint;
    uint public override USDsInOutRatio; // USDsInOutRatio is accurate after 24 hours (one iteration)
    uint32 public constant override USDsInOutRatio_prec = 10**6;
    uint8 public constant FREQUENCY = 6;
    uint32 public updateNextIndex;
    uint32 public lastUpdateTime; // the timstamp of the lastest update
    uint32 public updatePeriod; // the default updatePeriod of one update is 1 hours
    uint public constant ETHprice_prec = 10**8;
    uint public constant SPAprice_prec = 10**18;
    uint public constant USDsPrice_prec = 10**18;
    uint32 public movingAvgShortPeriod;
    uint32 public movingAvgLongPeriod;
    AggregatorV3Interface priceFeedETH;
    address public SPAaddr;
    address public WETH;
    address public VaultAddr;
    address public USDsAddr;
    address public USDsOraclePool;
    address public SPAoraclePool;
    address public SPAoracleBaseTokenAddr;
    address public USDsOracleBaseTokenAddr;

    event USDsInOutRatioUpdated(
        uint USDsInOutRatio,
        uint USDsOnflow_average,
        uint USDsInflow_average,
        uint32 timeStamp,
        uint index
    );
    event periodChanged(
        uint32 updatePeriod,
        uint32 movingAvgShortPeriod,
        uint32 movingAvgLongPeriod
    );
    event collateralInfoChanged(
        address _collateralAddr,
        bool _supported,
        AggregatorV3Interface _priceFeed,
        uint _price_prec
    );

    uint[FREQUENCY+1] public USDsInflow;
    uint[FREQUENCY+1] public USDsOnflow;
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
    function initialize(address _priceFeedETH, address _SPAaddr, address _WETH) public initializer {
        OwnableUpgradeable.__Ownable_init();
        updatePeriod = 12 hours;
        lastUpdateTime = uint32(now % 2**32);
        priceFeedETH = AggregatorV3Interface(_priceFeedETH);
        SPAaddr = _SPAaddr;
        WETH = _WETH;
        movingAvgShortPeriod = 600;
        movingAvgLongPeriod = 3600;
    }

    //for testing purpose
    function updateUSDsAddress(address _USDsAddr) external onlyOwner {
        USDsAddr = _USDsAddr;
    }

    function updateVaultAddress(address _VaultAddr) external onlyOwner {
        VaultAddr = _VaultAddr;
    }

    function updateOraclePoolsAddress(address _SPAoracleBaseTokenAddr, address _USDsOracleBaseTokenAddr, address _USDsOraclePool, address _SPAoraclePool) external onlyOwner {
        SPAoracleBaseTokenAddr = _SPAoracleBaseTokenAddr;
        USDsOracleBaseTokenAddr = _USDsOracleBaseTokenAddr;
        USDsOraclePool = _USDsOraclePool;
        SPAoraclePool = _SPAoraclePool;
    }

    /**
     * @notice change updatePeriod
     * @dev the frequency of update always remains the same
     * @param _updatePeriod new minimal updatePeriod in between two updates
     * @param _movingAvgShortPeriod new moving average range of SPA and USDs price
     * @param _movingAvgLongPeriod new moving average range of USDs price on average (used in SwapFeeIn)
     */
    function changePeriod(uint32 _updatePeriod, uint32 _movingAvgShortPeriod, uint32 _movingAvgLongPeriod) external onlyOwner {
        updatePeriod = _updatePeriod;
        movingAvgShortPeriod =_movingAvgShortPeriod;
        movingAvgLongPeriod = _movingAvgLongPeriod;
        emit periodChanged(updatePeriod, movingAvgShortPeriod, movingAvgLongPeriod);
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
        require(currTime >= lastUpdateTime, "updateInOutRatio: error last update happened in the future");
        require(timeElapsed >= updatePeriod, "updateInOutRatio: the time elapsed is too short.");
        uint32 indexNew = updateNextIndex;
        uint32 indexOld = (indexNew + 1) % (FREQUENCY + 1);
        USDsInflow[indexNew] = IUSDs(USDsAddr).totalMinted();
        USDsOnflow[indexNew] = IUSDs(USDsAddr).totalBurnt();
        uint USDsInflow_average = USDsInflow[indexNew].sub(USDsInflow[indexOld]);
        uint USDsOnflow_average = USDsOnflow[indexNew].sub(USDsOnflow[indexOld]);
        if (USDsInOutRatio == 0) {
            USDsInOutRatio = USDsInOutRatio_prec;
        } else {
            USDsInOutRatio = USDsOnflow_average.mul(USDsInOutRatio_prec).div(USDsInflow_average);
        }
        lastUpdateTime = currTime;
        updateNextIndex = indexOld;
        emit USDsInOutRatioUpdated(USDsInOutRatio, USDsOnflow_average, USDsInflow_average, lastUpdateTime, indexNew);
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
        uint32 longestSec = OracleLibrary.getOldestObservationSecondsAgo(SPAoraclePool);
        uint32 period = movingAvgShortPeriod < longestSec ? movingAvgShortPeriod : longestSec;
        int24 timeWeightedAverageTick = OracleLibrary.consult(SPAoraclePool, period);
        uint quoteAmount = OracleLibrary.getQuoteAtTick(timeWeightedAverageTick, uint128(SPAprice_prec), SPAaddr, SPAoracleBaseTokenAddr);
        uint SPAprice = _getETHprice().mul(quoteAmount).div(ETHprice_prec);
        return SPAprice;
    }

    function getUSDsPrice() external view override returns (uint) {
        if (USDsOraclePool == address(0)) {
            return USDsPrice_prec;
        }
        uint32 longestSec = OracleLibrary.getOldestObservationSecondsAgo(USDsOraclePool);
        uint32 period = movingAvgShortPeriod < longestSec ? movingAvgShortPeriod : longestSec;
        int24 timeWeightedAverageTick = OracleLibrary.consult(USDsOraclePool, period);
        uint quoteAmount = OracleLibrary.getQuoteAtTick(timeWeightedAverageTick, uint128(USDsPrice_prec), VaultAddr, USDsOracleBaseTokenAddr);
        uint USDsPrice = _getCollateralPrice(USDsOracleBaseTokenAddr).mul(quoteAmount).div(_getCollateralPrice_prec(USDsOracleBaseTokenAddr));
        return USDsPrice;
    }

    function getUSDsPrice_average() external view override returns (uint) {
        if (USDsOraclePool == address(0)){
            return USDsPrice_prec;
        }
        uint32 longestSec = OracleLibrary.getOldestObservationSecondsAgo(USDsOraclePool);
        uint32 period = movingAvgLongPeriod < longestSec ? movingAvgLongPeriod : longestSec;
        int24 timeWeightedAverageTick = OracleLibrary.consult(USDsOraclePool, period);
        uint quoteAmount = OracleLibrary.getQuoteAtTick(timeWeightedAverageTick, uint128(USDsPrice_prec), VaultAddr, USDsOracleBaseTokenAddr);
        uint USDsPrice_average = _getCollateralPrice(USDsOracleBaseTokenAddr).mul(quoteAmount).div(_getCollateralPrice_prec(USDsOracleBaseTokenAddr));
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
