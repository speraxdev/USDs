

pragma solidity ^0.6.7;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IUniswapV2Pair.sol";
import {UniswapV2OracleLibrary} from "../libraries/UniswapV2OracleLibrary.sol";
import {SafeMath} from "../libraries/SafeERC20.sol";

contract PriceConsumerV3 {
	using SafeMath for *;
    using UniswapV2OracleLibrary for *;

    struct Observation {
        uint timestamp;
        uint price0Cumulative;
    }

    uint32 public constant PERIOD = 6 hours;
    uint8 public constant RESOLUTION = 112;
    uint256 public constant INI_PERIOD_PRICETIME = (uint(90000) << RESOLUTION).mul(PERIOD);
    uint256 public BASE_PRICETIME = (1 weeks).div(PERIOD).mul(INI_PERIOD_PRICETIME);
    IUniswapV2Pair public immutable pair;
    uint public pricetimeCorrection;
    uint32 public override lastTime;
    Observation[29] public override observations;
    uint256 public oldestIndex;
    uint256 public override token0PriceMA7;
	
    AggregatorV3Interface internal priceFeedETH;
    AggregatorV3Interface internal priceFeedUSDC;

    constructor(address pair_) public {
    	//Kovan
        priceFeedETH = AggregatorV3Interface(0x9326BFA02ADD2366b30bacB125260Af641031331);
        priceFeedUSDC = AggregatorV3Interface(0x9211c6b3BF41A10F78539810Cf5c64e1BB78Ec60);
        //Mainnet
        //priceFeedETH = AggregatorV3Interface(0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419);
        //priceFeedUSDC = AggregatorV3Interface(0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6);

        pair = IUniswapV2Pair(pair_);
        lastTime = uint32(now % 2 ** 32);
        oldestIndex = 0;

        ( , pricetimeCorrection, ) = pair_.currentCumulativePrices();
        // obtain the cumulative pricetime from uniswapv2 pair deployment to now

        token1PriceMA7 = uint(90000) << RESOLUTION;
        for (uint256 i = 0; i < token1Pricetimes.length; i++) {
            token1Pricetimes[i] = INI_PERIOD_PRICETIME.mul(i).add(pricetimeCorrection);
        }


    }

    /**
     * Returns the latest price
     */
    function getETHPrice() public view returns (int) {
        (
            uint80 roundID, 
            int price,
            uint startedAt,–
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



    /**
     * @notice update the price of token0 to the latest
     * @dev the price would be updated only once per PERIOD time
     */
    function update() external {
        // check if enough time has elapsed for a new update
        uint32 currTime = uint32(now % 2 ** 32);
        uint32 timeElapsed = currTime - lastTime;
        require(timeElapsed >= PERIOD, "update() : the time elapsed is too short.");

        // query the lastest pricetime (plus BASE_PRICETIME)
        (, uint256 price0Cumulative, ) =
            address(pair).currentCumulativePrices();
        uint256 newPricetime = price0Cumulative.add(BASE_PRICETIME);

        // update the past-7-day pricetime array and oldestIndex
        observations[oldestIndex].price0Cumulative = newPricetime;
        observations[oldestIndex].timestamp = now;
        oldestIndex = oldestIndex.add(1).mod(observations.length);

        // calculate the newest token0PriceMA7
        // notice that the index corresponding to the newPricetime is (oldestIndex - 1) % observations.length
        uint256 newestIndex;
        if (oldestIndex == 0) {
            newestIndex = observations.length.sub(1);
        } else {
            newestIndex = oldestIndex.sub(1);
        }

        uint32 timeElapsedOneWeek = uint32((observations[newestIndex].timestamp - observations[oldestIndex].timestamp) % 2**32)
        token0PriceMA7 = (observations[newestIndex].price0Cumulative - observations[oldestIndex].price0Cumulative) / timeElapsedOneWeek;

        lastTime = currTime;
    }







}

