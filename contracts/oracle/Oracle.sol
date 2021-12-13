// SPDX-License-Identifier: MIT
pragma solidity >=0.6.12;

import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/interfaces/FlagsInterface.sol";

import "../vault/VaultCore.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IUSDs.sol";
import "../libraries/OracleLibrary.sol";

/**
 * @title Oracle contract of USDs protocol
 * @dev providing collateral prices (from Chainlink)
 * @dev providing SPA and USDs prices (from Uniswap V3 pools)
 * @dev providing records of USDs inflow and outflow ratio
 * @author Sperax Inc
 */
contract Oracle is Initializable, IOracle, OwnableUpgradeable {
    using SafeMathUpgradeable for uint;
    uint public override USDsInOutRatio; // USDsInOutRatio is accurate after 24 hours (one iteration)
    uint32 public constant override USDsInOutRatio_prec = 10**6;
    uint8 public constant FREQUENCY = 6;
    uint32 public updateNextIndex;
    uint32 public lastUpdateTime; // the timstamp of the lastest update
    uint32 public updatePeriod; // the default updatePeriod of one update is 1 hours
    uint public constant USDCprice_prec = 10**8;
    uint public constant SPAprice_prec = 10**18;
    uint public constant USDsPrice_prec = 10**18;
    uint32 public movingAvgShortPeriod;
    uint32 public movingAvgLongPeriod;
    AggregatorV3Interface priceFeedUSDC;
    address public SPAaddr;
    address public USDCaddr;
    address public VaultAddr;
    address public USDsAddr;
    address public USDsOraclePool;
    address public SPAoraclePool;
    address public SPAoracleQuoteTokenAddr;
    address public USDsOracleQuoteTokenAddr;
    address constant private FLAG_ARBITRUM_SEQ_OFFLINE = address(bytes20(bytes32(uint256(keccak256("chainlink.flags.arbitrum-seq-offline")) - 1)));
    FlagsInterface internal chainlinkFlags;


    event USDsInOutRatioUpdated(
        uint USDsInOutRatio,
        uint USDsOutflow_average,
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
    event USDsAddressUpdated(address oldAddr, address newAddr);
    event VaultAddressUpdated(address oldAddr, address newAddr);
    event poolAddressesUpdated(
        address SPAoracleQuoteTokenAddr,
        address USDsOracleQuoteTokenAddr,
        address USDsOraclePool,
        address SPAoraclePool
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
    function initialize(address _priceFeedUSDC, address _SPAaddr, address _USDCaddr, address _chainlinkFlags) public initializer {
        OwnableUpgradeable.__Ownable_init();
        updatePeriod = 12 hours;
        lastUpdateTime = uint32(now % 2**32);
        priceFeedUSDC = AggregatorV3Interface(_priceFeedUSDC);
        SPAaddr = _SPAaddr;
        USDCaddr = _USDCaddr;
        movingAvgShortPeriod = 600;
        movingAvgLongPeriod = 3600;
        chainlinkFlags = FlagsInterface(_chainlinkFlags);
    }

    function updateUSDsAddress(address _USDsAddr) external onlyOwner {
        emit USDsAddressUpdated(USDsAddr, _USDsAddr);
        USDsAddr = _USDsAddr;
    }

    function updateVaultAddress(address _VaultAddr) external onlyOwner {
        emit VaultAddressUpdated(VaultAddr, _VaultAddr);
        VaultAddr = _VaultAddr;
    }

    function updateOraclePoolsAddress(address _SPAoracleQuoteTokenAddr, address _USDsOracleQuoteTokenAddr, address _USDsOraclePool, address _SPAoraclePool) external onlyOwner {
        SPAoracleQuoteTokenAddr = _SPAoracleQuoteTokenAddr;
        USDsOracleQuoteTokenAddr = _USDsOracleQuoteTokenAddr;
        USDsOraclePool = _USDsOraclePool;
        SPAoraclePool = _SPAoraclePool;
        emit poolAddressesUpdated(SPAoracleQuoteTokenAddr, USDsOracleQuoteTokenAddr, USDsOraclePool, SPAoraclePool);
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
        USDsInflow[indexNew] = IUSDs(USDsAddr).mintedViaUsers();
        USDsOutflow[indexNew] = IUSDs(USDsAddr).burntViaUsers();
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

    function getUSDCprice() external view override returns (uint) {
        return _getUSDCprice();
	}

    function getSPAprice() external view override returns (uint) {
        uint32 longestSec = OracleLibrary.getOldestObservationSecondsAgo(SPAoraclePool);
        uint32 period = movingAvgShortPeriod < longestSec ? movingAvgShortPeriod : longestSec;
        int24 timeWeightedAverageTick = OracleLibrary.consult(SPAoraclePool, period);
        uint quoteAmount = OracleLibrary.getQuoteAtTick(timeWeightedAverageTick, uint128(SPAprice_prec), SPAaddr, SPAoracleQuoteTokenAddr);
        uint SPAprice = _getUSDCprice().mul(quoteAmount).div(USDCprice_prec);
        return SPAprice;
    }

    function getUSDsPrice() external view override returns (uint) {
        if (USDsOraclePool == address(0)) {
            return USDsPrice_prec;
        }
        uint32 longestSec = OracleLibrary.getOldestObservationSecondsAgo(USDsOraclePool);
        uint32 period = movingAvgShortPeriod < longestSec ? movingAvgShortPeriod : longestSec;
        int24 timeWeightedAverageTick = OracleLibrary.consult(USDsOraclePool, period);
        uint quoteAmount = OracleLibrary.getQuoteAtTick(timeWeightedAverageTick, uint128(USDsPrice_prec), USDsAddr, USDsOracleQuoteTokenAddr);
        uint USDsPrice = _getCollateralPrice(USDsOracleQuoteTokenAddr).mul(quoteAmount).div(_getCollateralPrice_prec(USDsOracleQuoteTokenAddr));
        return USDsPrice;
    }

    function getUSDsPrice_average() external view override returns (uint) {
        if (USDsOraclePool == address(0)){
            return USDsPrice_prec;
        }
        uint32 longestSec = OracleLibrary.getOldestObservationSecondsAgo(USDsOraclePool);
        uint32 period = movingAvgLongPeriod < longestSec ? movingAvgLongPeriod : longestSec;
        int24 timeWeightedAverageTick = OracleLibrary.consult(USDsOraclePool, period);
        uint quoteAmount = OracleLibrary.getQuoteAtTick(timeWeightedAverageTick, uint128(USDsPrice_prec), USDsAddr, USDsOracleQuoteTokenAddr);
        uint USDsPrice_average = _getCollateralPrice(USDsOracleQuoteTokenAddr).mul(quoteAmount).div(_getCollateralPrice_prec(USDsOracleQuoteTokenAddr));
        return USDsPrice_average;
    }
    function getCollateralPrice_prec(address collateralAddr) external view override returns (uint) {
        collateralStruct memory  collateralInfo = collateralsInfo[collateralAddr];
        require(collateralInfo.supported, "getCollateralPrice_prec: Collateral not supported.");
        return _getCollateralPrice_prec(collateralAddr);
    }

    function getUSDCprice_prec() external view override returns (uint) {
        return USDCprice_prec;
    }

    function getSPAprice_prec() external view override returns (uint) {
        return SPAprice_prec;
    }

    function getUSDsPrice_prec() external view override returns (uint) {
        return USDsPrice_prec;
    }

    function _getCollateralPrice(address collateralAddr) internal view returns (uint) {
        bool isRaised = chainlinkFlags.getFlag(FLAG_ARBITRUM_SEQ_OFFLINE);
        if (isRaised) {
                // If flag is raised we shouldn't perform any critical operations
            revert("Chainlink feeds are not being updated");
        }
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


	function _getUSDCprice() internal view returns (uint) {
        bool isRaised = chainlinkFlags.getFlag(FLAG_ARBITRUM_SEQ_OFFLINE);
        if (isRaised) {
                // If flag is raised we shouldn't perform any critical operations
            revert("Chainlink feeds are not being updated");
        }
		(
            ,
            int price,
            ,
            ,
		) = priceFeedUSDC.latestRoundData();
		return uint(price);
	}

    function _getCollateralPrice_prec(address collateralAddr) internal view returns (uint) {
        collateralStruct memory  collateralInfo = collateralsInfo[collateralAddr];
        require(collateralInfo.supported, "_getCollateralPrice_prec: Collateral not supported.");
        return collateralInfo.price_prec;
	}


}
