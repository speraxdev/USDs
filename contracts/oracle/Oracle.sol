// SPDX-License-Identifier: MIT
pragma solidity >=0.6.12;

import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/interfaces/FlagsInterface.sol";
import '@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol';

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
    uint128 public USDC_prec;
    uint128 public SPA_prec;
    uint128 public USDs_prec;
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
    address public constant UNISWAP_FACTORY= 0x1F98431c8aD98523631AE4a59f267346ea31F984;
    uint24 SPAoraclePoolFee;
    uint24 USDsOraclePoolFee;

    event USDsInOutRatioUpdated(
        uint USDsInOutRatio,
        uint USDsOutflow_average,
        uint USDsInflow_average,
        uint32 timeStamp,
        uint index
    );
    event PeriodChanged(
        uint32 updatePeriod,
        uint32 movingAvgShortPeriod,
        uint32 movingAvgLongPeriod
    );
    event CollateralInfoChanged(
        address _collateralAddr,
        bool _supported,
        AggregatorV3Interface _priceFeed,
        uint _price_prec
    );
    event USDsAddressUpdated(address oldAddr, address newAddr);
    event VaultAddressUpdated(address oldAddr, address newAddr);
    event UniPoolsSettingUpdated(
        address SPAoracleQuoteTokenAddr,
        address USDsOracleQuoteTokenAddr,
        uint24 SPAoraclePoolFee,
        uint24 USDsOraclePoolFee
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
        SPA_prec = uint128(10)**ERC20(SPAaddr).decimals();
        USDCaddr = _USDCaddr;
        USDC_prec = uint128(10)**ERC20(USDCaddr).decimals();
        movingAvgShortPeriod = 600;
        movingAvgLongPeriod = 3600;
        chainlinkFlags = FlagsInterface(_chainlinkFlags);
        SPAoracleQuoteTokenAddr = _USDCaddr;
        USDsOracleQuoteTokenAddr = _USDCaddr;
        SPAoraclePoolFee = 10000;
        USDsOraclePoolFee = 500;
    }

    function updateUSDsAddress(address _USDsAddr) external onlyOwner {
        USDsAddr = _USDsAddr;
        USDs_prec = uint128(10)**ERC20(USDsAddr).decimals();
        emit USDsAddressUpdated(USDsAddr, _USDsAddr);
    }

    function updateVaultAddress(address _VaultAddr) external onlyOwner {
        VaultAddr = _VaultAddr;
        emit VaultAddressUpdated(VaultAddr, _VaultAddr);
    }

    function updateUniPoolsSetting(
        address _SPAoracleQuoteTokenAddr,
        address _USDsOracleQuoteTokenAddr,
        uint24 _SPAoraclePoolFee,
        uint24 _USDsOraclePoolFee
    ) external onlyOwner {
        SPAoracleQuoteTokenAddr = _SPAoracleQuoteTokenAddr;
        USDsOracleQuoteTokenAddr = _USDsOracleQuoteTokenAddr;
        SPAoraclePoolFee = _SPAoraclePoolFee;
        USDsOraclePoolFee = _USDsOraclePoolFee;
        emit UniPoolsSettingUpdated(
            SPAoracleQuoteTokenAddr,
            USDsOracleQuoteTokenAddr,
            SPAoraclePoolFee,
            USDsOraclePoolFee
        );
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
        emit PeriodChanged(updatePeriod, movingAvgShortPeriod, movingAvgLongPeriod);
    }

    function updateCollateralInfo(address _collateralAddr, bool _supported, AggregatorV3Interface _priceFeed, uint _price_prec) external onlyOwner {
        collateralStruct storage updatedCollateral = collateralsInfo[_collateralAddr];
        updatedCollateral.collateralAddr = _collateralAddr;
        updatedCollateral.supported = _supported;
        updatedCollateral.priceFeed = _priceFeed;
        updatedCollateral.price_prec = _price_prec;
        emit CollateralInfoChanged(_collateralAddr, _supported, _priceFeed, _price_prec);
    }

    /**
     * @notice update the price of tokenA to the latest
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
        address SPAoraclePool = IUniswapV3Factory(UNISWAP_FACTORY).getPool(
            SPAaddr, SPAoracleQuoteTokenAddr, SPAoraclePoolFee
        );
        require(SPAoraclePool != address(0), 'SPA oracle pool does not exist.');
        uint128 SPAoracleQuoteToken_prec =
            uint128(10)**ERC20(SPAoracleQuoteTokenAddr).decimals();
        uint quoteTokenAmtPerSPA = _getUniMAPrice(
            SPAoraclePool,
            SPAaddr,
            SPAoracleQuoteTokenAddr,
            SPA_prec,
            SPAoracleQuoteToken_prec,
            movingAvgShortPeriod
        );
        return _getCollateralPrice(SPAoracleQuoteTokenAddr)
            .mul(quoteTokenAmtPerSPA)
            .mul(SPAprice_prec)
            .div(SPAoracleQuoteToken_prec)
            .div(USDCprice_prec);
    }

    function getUSDsPrice() external view override returns (uint) {
        address USDsOraclePool = IUniswapV3Factory(UNISWAP_FACTORY).getPool(
            USDsAddr, USDsOracleQuoteTokenAddr, USDsOraclePoolFee
        );
        if (USDsOraclePool == address(0)) {
            return USDsPrice_prec;
        }
        uint128 USDsOracleQuoteToken_prec =
            uint128(10)**ERC20(USDsOracleQuoteTokenAddr).decimals();
        uint quoteTokenAmtPerUSDs = _getUniMAPrice(
            USDsOraclePool,
            USDsAddr,
            USDsOracleQuoteTokenAddr,
            USDs_prec,
            USDsOracleQuoteToken_prec,
            movingAvgShortPeriod
        );
        return _getCollateralPrice(USDsOracleQuoteTokenAddr)
            .mul(quoteTokenAmtPerUSDs)
            .mul(USDsPrice_prec)
            .div(USDsOracleQuoteToken_prec)
            .div(USDCprice_prec);
    }

    function getUSDsPrice_average() external view override returns (uint) {
        address USDsOraclePool = IUniswapV3Factory(UNISWAP_FACTORY).getPool(
            USDsAddr, USDsOracleQuoteTokenAddr, USDsOraclePoolFee
        );
        if (USDsOraclePool == address(0)) {
            return USDsPrice_prec;
        }
        uint128 USDsOracleQuoteToken_prec =
            uint128(10)**ERC20(USDsOracleQuoteTokenAddr).decimals();
        uint quoteTokenAmtPerUSDs = _getUniMAPrice(
            USDsOraclePool,
            USDsAddr,
            USDsOracleQuoteTokenAddr,
            USDs_prec,
            USDsOracleQuoteToken_prec,
            movingAvgLongPeriod
        );
        return _getCollateralPrice(USDsOracleQuoteTokenAddr)
            .mul(quoteTokenAmtPerUSDs)
            .mul(USDsPrice_prec)
            .div(USDsOracleQuoteToken_prec)
            .div(USDCprice_prec);
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

    /**
     * @notice get the Uniswap V3 Moving Average (MA) of tokenBPertokenA
     * @dev tokenA is baseToken, tokenB is quoteToken
     *      e.g. for USDsPerSPA, tokenA = SPA and tokenB = USDs
     * @dev tokenBPertokenA has the same precision as tokenB
     */
    function _getUniMAPrice(
        address tokenAtokenBPool,
        address tokenA,
        address tokenB,
        uint128 tokenA_prec,
        uint128 tokenB_prec,
        uint32 movingAvgPeriod
    ) internal view returns(uint) {
        // get MA tick
        uint32 oldestObservationSecondsAgo =
            OracleLibrary.getOldestObservationSecondsAgo(tokenAtokenBPool);
        uint32 period = movingAvgPeriod < oldestObservationSecondsAgo ?
            movingAvgPeriod : oldestObservationSecondsAgo;
        int24 timeWeightedAverageTick =
            OracleLibrary.consult(tokenAtokenBPool, period);
        // get MA price from MA tick
        uint tokenBPertokenA = OracleLibrary.getQuoteAtTick(
            timeWeightedAverageTick,
            tokenA_prec,
            tokenA,
            tokenB
        );
        return tokenBPertokenA;
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
