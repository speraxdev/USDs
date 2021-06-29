// SPDX-License-Identifier: MIT
// Note: 00000000000000000000000006ee09ff6f4c83eab024173f5507515b0f810db0
pragma solidity ^0.6.12;

import "../interfaces/AggregatorV3Interface.sol";
import "../libraries/Ownable.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IUniswapV2Pair.sol";
import "../libraries/UniswapV2OracleLibrary.sol";
import "../libraries/SafeERC20.sol";
import { USDs } from "../token/USDs.sol";

/**
 * @title Oracle - the oracle contract for Spark
 * @author Sperax Dev Team
 * @notice this contract gets data from UniswapV2 pair and feed these data into the main contact of Spark, i.e. Spark.sol
 * @dev this contract draws insights from "ExampleOracleSimple.sol" by UniswapV2 team
 */

contract Oracle is IOracle, Ownable {
    using SafeMath for *;

    event Update(uint currPriceMA, uint currPricetime);

    struct token0Pricetime {
       uint32 timestamp;
       uint price0Cumulative;
    }


    //
    // Constants & Immutables
    //
    uint8 public constant FREQUENCY = 24;
    IUniswapV2Pair private immutable _pair;

    //
    // Core State Variables
    //
    // the moving average price of token0 denominated in token1
    // frequency = 24, default period = 1 hours ==> default timespan is 1 days
    uint public override token0PriceMA;

    //
    // Auxilliary State Variables
    //
    // the per-period cumulative pricetimes, i.e. the UniswapV2 price*time values, of token0
    token0Pricetime[FREQUENCY+1] public token0Pricetimes;
    uint32 public pricetimeOldestIndex;
    // the timstamp of the lastest price update
    uint32 public override lastUpdateTime;
    // the default period of one price update is 1 hours
    uint32 public override period = 1 hours;
	AggregatorV3Interface priceFeedETH;
	AggregatorV3Interface priceFeedUSDC;
	AggregatorV3Interface priceFeedDAI;
	AggregatorV3Interface priceFeedUSDT;

	address public USDCAddr = 0xb7a4F3E9097C08dA09517b5aB877F7a917224ede;
    address public USDTAddr = 0xf3e0d7bF58c5d455D31ef1c2d5375904dF525105;
    address public DAIAddr = 0x1528F3FCc26d13F7079325Fb78D9442607781c8C;

    uint public override ETHPricePrecision = 10**8;
    uint public USDCPricePrecision = 10**8;
    uint public override USDsPricePrecision = 10**18;
    uint public USDTPricePrecision = 10**8;
    uint public DAIPricePrecision = 10**8;
    uint public override SPAPricePrecision = 10**8 * 2**112;

    //  For swap fee:
    uint[FREQUENCY+1] public USDsInflow;
    uint[FREQUENCY+1] public USDsOutflow;
    uint USDsInOutRatio;
    uint USDsInOutRatioPrecision = 10000000;


    // USDs Instance
	USDs public USDsInstance;
    //
    // Constructor
    //
    constructor(address pair_, address USDsToken_) public {
		priceFeedETH = AggregatorV3Interface(0x9326BFA02ADD2366b30bacB125260Af641031331);
        priceFeedUSDC = AggregatorV3Interface(0x9211c6b3BF41A10F78539810Cf5c64e1BB78Ec60);
        priceFeedDAI = AggregatorV3Interface(0x777A68032a88E5A84678A77Af2CD65A7b3c0775a);
        priceFeedUSDT = AggregatorV3Interface(0x2ca5A90D34cA333661083F89D831f757A9A50148);
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
        period = newPeriod;
    }


    //
    // Core Functions
    //

	function getETHPrice() public view returns (int) {
		(
			uint80 roundID,
			int price,
			uint startedAt,
			uint timeStamp,
			uint80 answeredInRound
		) = priceFeedETH.latestRoundData();
		return price;
	}
	function getUSDCPrice() public view returns (int) {
		(
			uint80 roundID,
			int price,
			uint startedAt,
			uint timeStamp,
			uint80 answeredInRound
		) = priceFeedUSDC.latestRoundData();
		return price;
	}
	function getUSDTPrice() public view returns (int) {
		(
			uint80 roundID,
			int price,
			uint startedAt,
			uint timeStamp,
			uint80 answeredInRound
		) = priceFeedUSDT.latestRoundData();
		return price;
	}
	function getDAIPrice() public view returns (int) {
		(
			uint80 roundID,
			int price,
			uint startedAt,
			uint timeStamp,
			uint80 answeredInRound
		) = priceFeedDAI.latestRoundData();
		return price;
	}
	function getSPAPrice() public view override returns (int) {
		int ETHPrice = getETHPrice();
		return int(token0PriceMA.mul(uint(ETHPrice)));
	}

    function getUSDsPrice() public view override returns (int) {
		return int(1 * USDsPricePrecision);
	}

	function collatPrice(address tokenAddr) public view override returns (int) {
		if (tokenAddr == USDCAddr) {
			return getUSDCPrice();
		}
		if (tokenAddr == USDTAddr) {
			return getUSDTPrice();
		}
		if (tokenAddr == DAIAddr) {
			return getDAIPrice();
		}
	}

    function collatPricePrecision(address tokenAddr) public view override returns (uint) {
		if (tokenAddr == USDCAddr) {
			return USDCPricePrecision;
		}
		if (tokenAddr == USDTAddr) {
			return USDTPricePrecision;
		}
		if (tokenAddr == DAIAddr) {
			return DAIPricePrecision;
		}
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
    }
}
