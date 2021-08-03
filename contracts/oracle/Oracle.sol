
// To-do:
// change int()
pragma solidity ^0.6.12;

import "@openzeppelin/contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol";

import { USDs } from "../token/USDs.sol";
import "../interfaces/AggregatorV3Interface.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IUniswapV2Pair.sol";
import "../libraries/UniswapV2OracleLibrary.sol";

/**
 * @title Oracle - the oracle contract for Spark
 * @author Sperax Dev Team
 * @notice this contract gets data from UniswapV2 pair and feed these data into the main contact of Spark, i.e. Spark.sol
 * @dev this contract draws insights from "ExampleOracleSimple.sol" by UniswapV2 team
 */

contract Oracle is Initializable, IOracle, OwnableUpgradeable {
    using SafeMathUpgradeable for *;

    event Update(uint currPriceMA, uint currPricetime);

	event PriceListUpdated(
		address indexed token,
		address indexed aggregator,
        uint256 precision
	);

	event PeriodUpdated(
		uint256 indexed oldPeriod,
        uint256 indexed newPeriod,
        uint256 timestamp
	);

    struct token0Pricetime {
       uint32 timestamp;
       uint price0Cumulative;
    }


    //
    // Constants & Immutables
    //
    uint8 public constant FREQUENCY = 24;

    //
    // Core State Variables
    //
    // the moving average price of token0 denominated in token1
    // frequency = 24, default period = 1 hours ==> default timespan is 1 days
    uint public override token0PriceMA;
    IUniswapV2Pair private _pair;

    //
    // Auxilliary State Variables
    //
    // the per-period cumulative pricetimes, i.e. the UniswapV2 price*time values, of token0
    token0Pricetime[FREQUENCY+1] public token0Pricetimes;
    uint32 public pricetimeOldestIndex;
    // the timstamp of the lastest price update
    uint32 public override lastUpdateTime;
    // the default period of one price update is 1 hours
    uint32 public override period;
	AggregatorV3Interface priceFeedETH;

    uint public override ETHPricePrecision;
    uint public override USDsPricePrecision;
    uint public override SPAPricePrecision;

    //  For swap fee:
    uint[FREQUENCY+1] public USDsInflow;
    uint[FREQUENCY+1] public USDsOutflow;
    uint public override USDsInOutRatio;
    uint public override USDsInOutRatioPrecision;
    USDs public USDsInstance;

    address[] public tokenAddresses;
    mapping(address => uint256) public tokenAddressIndex;
    mapping(address => AggregatorV3Interface) public priceFeeds;
    mapping(address => uint256) public pricePrecisions;

	// AggregatorV3Interface priceFeedUSDC;
	// AggregatorV3Interface priceFeedUSDT;
	// AggregatorV3Interface priceFeedDAI;

	// address public USDCAddr;
	// address public USDTAddr;
	// address public DAIAddr;
    // uint public USDCPricePrecision;
    // uint public USDTPricePrecision;
    // uint public DAIPricePrecision;

    //
    // Initializer
    //
    function initialize(
        address pair_, address USDsToken_
    ) public initializer {
        OwnableUpgradeable.__Ownable_init();

        // Initialize variables
        period = 1 hours;
        // USDCAddr = 0xb7a4F3E9097C08dA09517b5aB877F7a917224ede;
        // USDCPricePrecision = 10**8;
        // priceFeedUSDC = AggregatorV3Interface(0x9211c6b3BF41A10F78539810Cf5c64e1BB78Ec60);
        ETHPricePrecision = 10**8;
        USDsPricePrecision = 10**18;
        SPAPricePrecision = 10**8;
        USDsInOutRatioPrecision = 10000000;

        priceFeedETH = AggregatorV3Interface(0x9326BFA02ADD2366b30bacB125260Af641031331);
        uint32 constructTime = uint32(now % 2 ** 32);
        _pair = IUniswapV2Pair(pair_);
        lastUpdateTime = constructTime;

        // obtain the cumulative pricetime from uniswapv2 pair deployment to now
        (uint pricetimeCorrection, , ) = UniswapV2OracleLibrary.currentCumulativePrices(pair_);

        // set up initial conditions
        // assume that 1 ETH = 2500 USD, 1 SPA = 0.02 USD, so 1 ETH = 125,000 SPA
        uint iniToken0Price = 125000;
        uint resolution = 112;
        uint unitPricetime = (iniToken0Price << resolution) * period;
        uint basePricetime = unitPricetime * FREQUENCY;

        // simulate the pricetimes of the past 7 days, including necessary correction
        token0PriceMA = iniToken0Price << resolution;
        for (uint i = 0; i < (FREQUENCY+1); i++) {
            token0Pricetimes[i].price0Cumulative = unitPricetime
                                                   .mul(i)
                                                   .add(pricetimeCorrection)
                                                   .sub(basePricetime);
            token0Pricetimes[i].timestamp = constructTime - period * uint32(FREQUENCY - i);
        }
        USDsInstance = USDs(USDsToken_);

        for (uint i = 0; i < (FREQUENCY+1); i++) {
            USDsInflow[i] = 0;
            USDsOutflow[i] = 0;
        }
    }

    //
    // Getter Function
    //
    /**
     * @notice get the address of the token pair pool
     * @return the pair pool address
     */
    function getPairAddr() external view returns (address) {
        return address(_pair);
    }

    //
    // Owner Only Function: changePeriod
    //

    /**
     * @notice change updating period
     * @dev the frequency of update always remains the same
     * @param newPeriod new minimal period in between two updates
     */
    function changePeriod(uint32 newPeriod) external onlyOwner {
        emit PeriodUpdated(period, newPeriod, block.timestamp);

        period = newPeriod;
    }

    /**
        Update price list
     */
    function updatePriceList(address assetAddress, address aggregatorAddress, uint256 precision) external onlyOwner {
        if (tokenAddressIndex[assetAddress] == 0) {
            tokenAddresses.push(assetAddress);
            tokenAddressIndex[assetAddress] = tokenAddresses.length;
        }
        priceFeeds[assetAddress] = AggregatorV3Interface(aggregatorAddress);
        pricePrecisions[assetAddress] = 10 ** precision;

        emit PriceListUpdated(assetAddress, aggregatorAddress, precision);
    }

    //
    // Core Functions
    //

	function getETHPrice() public view override returns (uint) {
		(
			uint80 roundID,
			int price,
			uint startedAt,
			uint timeStamp,
			uint80 answeredInRound
		) = priceFeedETH.latestRoundData();
		return uint(price);
	}

	function getAssetPrice(address assetAddress) public view returns (uint) {
		(
			uint80 roundID,
			int price,
			uint startedAt,
			uint timeStamp,
			uint80 answeredInRound
		) = priceFeeds[assetAddress].latestRoundData();
		return uint(price);
	}

    //to-do
	function getSPAPrice() external view override returns (uint) {
		uint ETHPrice = getETHPrice();

        uint token0PriceMA_NoPrec = token0PriceMA.div(2**112);
        //failing case: 1 ETH > 10^25 SPA or token0PriceMA/2**112 < ETHPrice
        return ETHPrice.mul(2**112).div(token0PriceMA);
	}

    function getUSDsPrice() external view override returns (uint) {
		return 1 * USDsPricePrecision;
	}

	function collatPrice(address tokenAddr) external view override returns (uint) {
		return getAssetPrice(tokenAddr);
	}

    function collatPricePrecision(address tokenAddr) external view override returns (uint) {
        return pricePrecisions[tokenAddr];
	}


    /**
     * @notice update the price of token0 to the latest
     * @dev the price would be updated only once per period time
     */
    function update() external override {
        // check if enough time has elapsed for a new update
        uint32 currTime = uint32(now % 2 ** 32);
        uint32 timeElapsed = currTime - lastUpdateTime;
        require(timeElapsed >= period, "update() : the time elapsed is too short.");


        // query the lastest pricetime
        (uint price0Cumulative, , ) = UniswapV2OracleLibrary.currentCumulativePrices(address(_pair));

        // update the past-7-day pricetime array and record
        uint32 indexNew = pricetimeOldestIndex;
        uint32 indexOld = (indexNew + 1) % (FREQUENCY+1);
        token0Pricetimes[indexNew].price0Cumulative = price0Cumulative;
        token0Pricetimes[indexNew].timestamp = currTime;

        // calculate the new moving average price of token0
        uint timeElapsedMA =
            uint(token0Pricetimes[indexNew].timestamp - token0Pricetimes[indexOld].timestamp); // notice: overflow is preferred
        token0PriceMA = token0Pricetimes[indexNew].price0Cumulative
                         .sub(token0Pricetimes[indexOld].price0Cumulative)
                         .div(timeElapsedMA);

        // update global status
        lastUpdateTime = currTime;
        pricetimeOldestIndex = indexOld;
        emit Update(token0PriceMA, price0Cumulative);

        USDsInflow[indexNew] = USDsInstance._totalMinted();
        USDsOutflow[indexNew] = USDsInstance._totalBurnt();

        uint USDsInflowOneDay = USDsInflow[indexNew].sub(USDsInflow[indexOld]);
        uint USDsOutflowOneDay = USDsOutflow[indexNew].sub(USDsOutflow[indexOld]);
        if (USDsInOutRatio == 0) {
            USDsInOutRatio = USDsInOutRatioPrecision;
        } else {
            USDsInOutRatio = USDsOutflowOneDay.div(USDsInOutRatio);
        }

    }
}
