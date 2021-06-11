pragma solidity ^0.6.12;

//inspired by https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/math/SafeCast.sol

library MyMath {
    //inspired by https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/math/SafeCast.sol
    /**
     * @dev Returns the downcasted uint112 from uint256, reverting on
     * overflow (when the input is greater than largest uint112).
     *
     *
     * Requirements:
     *
     * - input must fit into 112 bits
     */
      function toUint112(uint256 value) internal pure returns (uint112) {
          require(value < 2**112, "SafeCast: value doesnt fit in 112 bits");
          return uint112(value);
      }
}
