// // File: @openzeppelin/contracts-upgradeable/math/SafeMathUpgradeable.sol

// // SPDX-License-Identifier: MIT

// pragma solidity >=0.6.0 <0.8.0;

// /**
//  * @dev Wrappers over Solidity's arithmetic operations with added overflow
//  * checks.
//  *
//  * Arithmetic operations in Solidity wrap on overflow. This can easily result
//  * in bugs, because programmers usually assume that an overflow raises an
//  * error, which is the standard behavior in high level programming languages.
//  * `SafeMath` restores this intuition by reverting the transaction when an
//  * operation overflows.
//  *
//  * Using this library instead of the unchecked operations eliminates an entire
//  * class of bugs, so it's recommended to use it always.
//  */
// library SafeMathUpgradeable {
//     /**
//      * @dev Returns the addition of two unsigned integers, with an overflow flag.
//      *
//      * _Available since v3.4._
//      */
//     function tryAdd(uint256 a, uint256 b) internal pure returns (bool, uint256) {
//         uint256 c = a + b;
//         if (c < a) return (false, 0);
//         return (true, c);
//     }

//     /**
//      * @dev Returns the substraction of two unsigned integers, with an overflow flag.
//      *
//      * _Available since v3.4._
//      */
//     function trySub(uint256 a, uint256 b) internal pure returns (bool, uint256) {
//         if (b > a) return (false, 0);
//         return (true, a - b);
//     }

//     /**
//      * @dev Returns the multiplication of two unsigned integers, with an overflow flag.
//      *
//      * _Available since v3.4._
//      */
//     function tryMul(uint256 a, uint256 b) internal pure returns (bool, uint256) {
//         // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
//         // benefit is lost if 'b' is also tested.
//         // See: https://github.com/OpenZeppelin/openzeppelin-contracts/pull/522
//         if (a == 0) return (true, 0);
//         uint256 c = a * b;
//         if (c / a != b) return (false, 0);
//         return (true, c);
//     }

//     /**
//      * @dev Returns the division of two unsigned integers, with a division by zero flag.
//      *
//      * _Available since v3.4._
//      */
//     function tryDiv(uint256 a, uint256 b) internal pure returns (bool, uint256) {
//         if (b == 0) return (false, 0);
//         return (true, a / b);
//     }

//     /**
//      * @dev Returns the remainder of dividing two unsigned integers, with a division by zero flag.
//      *
//      * _Available since v3.4._
//      */
//     function tryMod(uint256 a, uint256 b) internal pure returns (bool, uint256) {
//         if (b == 0) return (false, 0);
//         return (true, a % b);
//     }

//     /**
//      * @dev Returns the addition of two unsigned integers, reverting on
//      * overflow.
//      *
//      * Counterpart to Solidity's `+` operator.
//      *
//      * Requirements:
//      *
//      * - Addition cannot overflow.
//      */
//     function add(uint256 a, uint256 b) internal pure returns (uint256) {
//         uint256 c = a + b;
//         require(c >= a, "SafeMath: addition overflow");
//         return c;
//     }

//     /**
//      * @dev Returns the subtraction of two unsigned integers, reverting on
//      * overflow (when the result is negative).
//      *
//      * Counterpart to Solidity's `-` operator.
//      *
//      * Requirements:
//      *
//      * - Subtraction cannot overflow.
//      */
//     function sub(uint256 a, uint256 b) internal pure returns (uint256) {
//         require(b <= a, "SafeMath: subtraction overflow");
//         return a - b;
//     }

//     /**
//      * @dev Returns the multiplication of two unsigned integers, reverting on
//      * overflow.
//      *
//      * Counterpart to Solidity's `*` operator.
//      *
//      * Requirements:
//      *
//      * - Multiplication cannot overflow.
//      */
//     function mul(uint256 a, uint256 b) internal pure returns (uint256) {
//         if (a == 0) return 0;
//         uint256 c = a * b;
//         require(c / a == b, "SafeMath: multiplication overflow");
//         return c;
//     }

//     /**
//      * @dev Returns the integer division of two unsigned integers, reverting on
//      * division by zero. The result is rounded towards zero.
//      *
//      * Counterpart to Solidity's `/` operator. Note: this function uses a
//      * `revert` opcode (which leaves remaining gas untouched) while Solidity
//      * uses an invalid opcode to revert (consuming all remaining gas).
//      *
//      * Requirements:
//      *
//      * - The divisor cannot be zero.
//      */
//     function div(uint256 a, uint256 b) internal pure returns (uint256) {
//         require(b > 0, "SafeMath: division by zero");
//         return a / b;
//     }

//     /**
//      * @dev Returns the remainder of dividing two unsigned integers. (unsigned integer modulo),
//      * reverting when dividing by zero.
//      *
//      * Counterpart to Solidity's `%` operator. This function uses a `revert`
//      * opcode (which leaves remaining gas untouched) while Solidity uses an
//      * invalid opcode to revert (consuming all remaining gas).
//      *
//      * Requirements:
//      *
//      * - The divisor cannot be zero.
//      */
//     function mod(uint256 a, uint256 b) internal pure returns (uint256) {
//         require(b > 0, "SafeMath: modulo by zero");
//         return a % b;
//     }

//     /**
//      * @dev Returns the subtraction of two unsigned integers, reverting with custom message on
//      * overflow (when the result is negative).
//      *
//      * CAUTION: This function is deprecated because it requires allocating memory for the error
//      * message unnecessarily. For custom revert reasons use {trySub}.
//      *
//      * Counterpart to Solidity's `-` operator.
//      *
//      * Requirements:
//      *
//      * - Subtraction cannot overflow.
//      */
//     function sub(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) {
//         require(b <= a, errorMessage);
//         return a - b;
//     }

//     /**
//      * @dev Returns the integer division of two unsigned integers, reverting with custom message on
//      * division by zero. The result is rounded towards zero.
//      *
//      * CAUTION: This function is deprecated because it requires allocating memory for the error
//      * message unnecessarily. For custom revert reasons use {tryDiv}.
//      *
//      * Counterpart to Solidity's `/` operator. Note: this function uses a
//      * `revert` opcode (which leaves remaining gas untouched) while Solidity
//      * uses an invalid opcode to revert (consuming all remaining gas).
//      *
//      * Requirements:
//      *
//      * - The divisor cannot be zero.
//      */
//     function div(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) {
//         require(b > 0, errorMessage);
//         return a / b;
//     }

//     /**
//      * @dev Returns the remainder of dividing two unsigned integers. (unsigned integer modulo),
//      * reverting with custom message when dividing by zero.
//      *
//      * CAUTION: This function is deprecated because it requires allocating memory for the error
//      * message unnecessarily. For custom revert reasons use {tryMod}.
//      *
//      * Counterpart to Solidity's `%` operator. This function uses a `revert`
//      * opcode (which leaves remaining gas untouched) while Solidity uses an
//      * invalid opcode to revert (consuming all remaining gas).
//      *
//      * Requirements:
//      *
//      * - The divisor cannot be zero.
//      */
//     function mod(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) {
//         require(b > 0, errorMessage);
//         return a % b;
//     }
// }

// // File: @openzeppelin/contracts-upgradeable/utils/AddressUpgradeable.sol



// pragma solidity >=0.6.2 <0.8.0;

// /**
//  * @dev Collection of functions related to the address type
//  */
// library AddressUpgradeable {
//     /**
//      * @dev Returns true if `account` is a contract.
//      *
//      * [IMPORTANT]
//      * ====
//      * It is unsafe to assume that an address for which this function returns
//      * false is an externally-owned account (EOA) and not a contract.
//      *
//      * Among others, `isContract` will return false for the following
//      * types of addresses:
//      *
//      *  - an externally-owned account
//      *  - a contract in construction
//      *  - an address where a contract will be created
//      *  - an address where a contract lived, but was destroyed
//      * ====
//      */
//     function isContract(address account) internal view returns (bool) {
//         // This method relies on extcodesize, which returns 0 for contracts in
//         // construction, since the code is only stored at the end of the
//         // constructor execution.

//         uint256 size;
//         // solhint-disable-next-line no-inline-assembly
//         assembly { size := extcodesize(account) }
//         return size > 0;
//     }

//     /**
//      * @dev Replacement for Solidity's `transfer`: sends `amount` wei to
//      * `recipient`, forwarding all available gas and reverting on errors.
//      *
//      * https://eips.ethereum.org/EIPS/eip-1884[EIP1884] increases the gas cost
//      * of certain opcodes, possibly making contracts go over the 2300 gas limit
//      * imposed by `transfer`, making them unable to receive funds via
//      * `transfer`. {sendValue} removes this limitation.
//      *
//      * https://diligence.consensys.net/posts/2019/09/stop-using-soliditys-transfer-now/[Learn more].
//      *
//      * IMPORTANT: because control is transferred to `recipient`, care must be
//      * taken to not create reentrancy vulnerabilities. Consider using
//      * {ReentrancyGuard} or the
//      * https://solidity.readthedocs.io/en/v0.5.11/security-considerations.html#use-the-checks-effects-interactions-pattern[checks-effects-interactions pattern].
//      */
//     function sendValue(address payable recipient, uint256 amount) internal {
//         require(address(this).balance >= amount, "Address: insufficient balance");

//         // solhint-disable-next-line avoid-low-level-calls, avoid-call-value
//         (bool success, ) = recipient.call{ value: amount }("");
//         require(success, "Address: unable to send value, recipient may have reverted");
//     }

//     /**
//      * @dev Performs a Solidity function call using a low level `call`. A
//      * plain`call` is an unsafe replacement for a function call: use this
//      * function instead.
//      *
//      * If `target` reverts with a revert reason, it is bubbled up by this
//      * function (like regular Solidity function calls).
//      *
//      * Returns the raw returned data. To convert to the expected return value,
//      * use https://solidity.readthedocs.io/en/latest/units-and-global-variables.html?highlight=abi.decode#abi-encoding-and-decoding-functions[`abi.decode`].
//      *
//      * Requirements:
//      *
//      * - `target` must be a contract.
//      * - calling `target` with `data` must not revert.
//      *
//      * _Available since v3.1._
//      */
//     function functionCall(address target, bytes memory data) internal returns (bytes memory) {
//       return functionCall(target, data, "Address: low-level call failed");
//     }

//     /**
//      * @dev Same as {xref-Address-functionCall-address-bytes-}[`functionCall`], but with
//      * `errorMessage` as a fallback revert reason when `target` reverts.
//      *
//      * _Available since v3.1._
//      */
//     function functionCall(address target, bytes memory data, string memory errorMessage) internal returns (bytes memory) {
//         return functionCallWithValue(target, data, 0, errorMessage);
//     }

//     /**
//      * @dev Same as {xref-Address-functionCall-address-bytes-}[`functionCall`],
//      * but also transferring `value` wei to `target`.
//      *
//      * Requirements:
//      *
//      * - the calling contract must have an ETH balance of at least `value`.
//      * - the called Solidity function must be `payable`.
//      *
//      * _Available since v3.1._
//      */
//     function functionCallWithValue(address target, bytes memory data, uint256 value) internal returns (bytes memory) {
//         return functionCallWithValue(target, data, value, "Address: low-level call with value failed");
//     }

//     /**
//      * @dev Same as {xref-Address-functionCallWithValue-address-bytes-uint256-}[`functionCallWithValue`], but
//      * with `errorMessage` as a fallback revert reason when `target` reverts.
//      *
//      * _Available since v3.1._
//      */
//     function functionCallWithValue(address target, bytes memory data, uint256 value, string memory errorMessage) internal returns (bytes memory) {
//         require(address(this).balance >= value, "Address: insufficient balance for call");
//         require(isContract(target), "Address: call to non-contract");

//         // solhint-disable-next-line avoid-low-level-calls
//         (bool success, bytes memory returndata) = target.call{ value: value }(data);
//         return _verifyCallResult(success, returndata, errorMessage);
//     }

//     /**
//      * @dev Same as {xref-Address-functionCall-address-bytes-}[`functionCall`],
//      * but performing a static call.
//      *
//      * _Available since v3.3._
//      */
//     function functionStaticCall(address target, bytes memory data) internal view returns (bytes memory) {
//         return functionStaticCall(target, data, "Address: low-level static call failed");
//     }

//     /**
//      * @dev Same as {xref-Address-functionCall-address-bytes-string-}[`functionCall`],
//      * but performing a static call.
//      *
//      * _Available since v3.3._
//      */
//     function functionStaticCall(address target, bytes memory data, string memory errorMessage) internal view returns (bytes memory) {
//         require(isContract(target), "Address: static call to non-contract");

//         // solhint-disable-next-line avoid-low-level-calls
//         (bool success, bytes memory returndata) = target.staticcall(data);
//         return _verifyCallResult(success, returndata, errorMessage);
//     }

//     function _verifyCallResult(bool success, bytes memory returndata, string memory errorMessage) private pure returns(bytes memory) {
//         if (success) {
//             return returndata;
//         } else {
//             // Look for revert reason and bubble it up if present
//             if (returndata.length > 0) {
//                 // The easiest way to bubble the revert reason is using memory via assembly

//                 // solhint-disable-next-line no-inline-assembly
//                 assembly {
//                     let returndata_size := mload(returndata)
//                     revert(add(32, returndata), returndata_size)
//                 }
//             } else {
//                 revert(errorMessage);
//             }
//         }
//     }
// }

// // File: @openzeppelin/contracts-upgradeable/proxy/Initializable.sol



// // solhint-disable-next-line compiler-version
// pragma solidity >=0.4.24 <0.8.0;


// /**
//  * @dev This is a base contract to aid in writing upgradeable contracts, or any kind of contract that will be deployed
//  * behind a proxy. Since a proxied contract can't have a constructor, it's common to move constructor logic to an
//  * external initializer function, usually called `initialize`. It then becomes necessary to protect this initializer
//  * function so it can only be called once. The {initializer} modifier provided by this contract will have this effect.
//  *
//  * TIP: To avoid leaving the proxy in an uninitialized state, the initializer function should be called as early as
//  * possible by providing the encoded function call as the `_data` argument to {UpgradeableProxy-constructor}.
//  *
//  * CAUTION: When used with inheritance, manual care must be taken to not invoke a parent initializer twice, or to ensure
//  * that all initializers are idempotent. This is not verified automatically as constructors are by Solidity.
//  */
// abstract contract Initializable {

//     /**
//      * @dev Indicates that the contract has been initialized.
//      */
//     bool private _initialized;

//     /**
//      * @dev Indicates that the contract is in the process of being initialized.
//      */
//     bool private _initializing;

//     /**
//      * @dev Modifier to protect an initializer function from being invoked twice.
//      */
//     modifier initializer() {
//         require(_initializing || _isConstructor() || !_initialized, "Initializable: contract is already initialized");

//         bool isTopLevelCall = !_initializing;
//         if (isTopLevelCall) {
//             _initializing = true;
//             _initialized = true;
//         }

//         _;

//         if (isTopLevelCall) {
//             _initializing = false;
//         }
//     }

//     /// @dev Returns true if and only if the function is running in the constructor
//     function _isConstructor() private view returns (bool) {
//         return !AddressUpgradeable.isContract(address(this));
//     }
// }

// // File: @openzeppelin/contracts-upgradeable/utils/ContextUpgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;


// /*
//  * @dev Provides information about the current execution context, including the
//  * sender of the transaction and its data. While these are generally available
//  * via msg.sender and msg.data, they should not be accessed in such a direct
//  * manner, since when dealing with GSN meta-transactions the account sending and
//  * paying for execution may not be the actual sender (as far as an application
//  * is concerned).
//  *
//  * This contract is only required for intermediate, library-like contracts.
//  */
// abstract contract ContextUpgradeable is Initializable {
//     function __Context_init() internal initializer {
//         __Context_init_unchained();
//     }

//     function __Context_init_unchained() internal initializer {
//     }
//     function _msgSender() internal view virtual returns (address payable) {
//         return msg.sender;
//     }

//     function _msgData() internal view virtual returns (bytes memory) {
//         this; // silence state mutability warning without generating bytecode - see https://github.com/ethereum/solidity/issues/2691
//         return msg.data;
//     }
//     uint256[50] private __gap;
// }

// // File: @openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;


// /**
//  * @dev Contract module which provides a basic access control mechanism, where
//  * there is an account (an owner) that can be granted exclusive access to
//  * specific functions.
//  *
//  * By default, the owner account will be the one that deploys the contract. This
//  * can later be changed with {transferOwnership}.
//  *
//  * This module is used through inheritance. It will make available the modifier
//  * `onlyOwner`, which can be applied to your functions to restrict their use to
//  * the owner.
//  */
// abstract contract OwnableUpgradeable is Initializable, ContextUpgradeable {
//     address private _owner;

//     event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

//     /**
//      * @dev Initializes the contract setting the deployer as the initial owner.
//      */
//     function __Ownable_init() internal initializer {
//         __Context_init_unchained();
//         __Ownable_init_unchained();
//     }

//     function __Ownable_init_unchained() internal initializer {
//         address msgSender = _msgSender();
//         _owner = msgSender;
//         emit OwnershipTransferred(address(0), msgSender);
//     }

//     /**
//      * @dev Returns the address of the current owner.
//      */
//     function owner() public view virtual returns (address) {
//         return _owner;
//     }

//     /**
//      * @dev Throws if called by any account other than the owner.
//      */
//     modifier onlyOwner() {
//         require(owner() == _msgSender(), "Ownable: caller is not the owner");
//         _;
//     }

//     /**
//      * @dev Leaves the contract without owner. It will not be possible to call
//      * `onlyOwner` functions anymore. Can only be called by the current owner.
//      *
//      * NOTE: Renouncing ownership will leave the contract without an owner,
//      * thereby removing any functionality that is only available to the owner.
//      */
//     function renounceOwnership() public virtual onlyOwner {
//         emit OwnershipTransferred(_owner, address(0));
//         _owner = address(0);
//     }

//     /**
//      * @dev Transfers ownership of the contract to a new account (`newOwner`).
//      * Can only be called by the current owner.
//      */
//     function transferOwnership(address newOwner) public virtual onlyOwner {
//         require(newOwner != address(0), "Ownable: new owner is the zero address");
//         emit OwnershipTransferred(_owner, newOwner);
//         _owner = newOwner;
//     }
//     uint256[49] private __gap;
// }

// // File: @openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;


// /**
//  * @dev Contract module that helps prevent reentrant calls to a function.
//  *
//  * Inheriting from `ReentrancyGuard` will make the {nonReentrant} modifier
//  * available, which can be applied to functions to make sure there are no nested
//  * (reentrant) calls to them.
//  *
//  * Note that because there is a single `nonReentrant` guard, functions marked as
//  * `nonReentrant` may not call one another. This can be worked around by making
//  * those functions `private`, and then adding `external` `nonReentrant` entry
//  * points to them.
//  *
//  * TIP: If you would like to learn more about reentrancy and alternative ways
//  * to protect against it, check out our blog post
//  * https://blog.openzeppelin.com/reentrancy-after-istanbul/[Reentrancy After Istanbul].
//  */
// abstract contract ReentrancyGuardUpgradeable is Initializable {
//     // Booleans are more expensive than uint256 or any type that takes up a full
//     // word because each write operation emits an extra SLOAD to first read the
//     // slot's contents, replace the bits taken up by the boolean, and then write
//     // back. This is the compiler's defense against contract upgrades and
//     // pointer aliasing, and it cannot be disabled.

//     // The values being non-zero value makes deployment a bit more expensive,
//     // but in exchange the refund on every call to nonReentrant will be lower in
//     // amount. Since refunds are capped to a percentage of the total
//     // transaction's gas, it is best to keep them low in cases like this one, to
//     // increase the likelihood of the full refund coming into effect.
//     uint256 private constant _NOT_ENTERED = 1;
//     uint256 private constant _ENTERED = 2;

//     uint256 private _status;

//     function __ReentrancyGuard_init() internal initializer {
//         __ReentrancyGuard_init_unchained();
//     }

//     function __ReentrancyGuard_init_unchained() internal initializer {
//         _status = _NOT_ENTERED;
//     }

//     /**
//      * @dev Prevents a contract from calling itself, directly or indirectly.
//      * Calling a `nonReentrant` function from another `nonReentrant`
//      * function is not supported. It is possible to prevent this from happening
//      * by making the `nonReentrant` function external, and make it call a
//      * `private` function that does the actual work.
//      */
//     modifier nonReentrant() {
//         // On the first call to nonReentrant, _notEntered will be true
//         require(_status != _ENTERED, "ReentrancyGuard: reentrant call");

//         // Any calls to nonReentrant after this point will fail
//         _status = _ENTERED;

//         _;

//         // By storing the original value once again, a refund is triggered (see
//         // https://eips.ethereum.org/EIPS/eip-2200)
//         _status = _NOT_ENTERED;
//     }
//     uint256[49] private __gap;
// }

// // File: contracts/libraries/StableMath.sol


// pragma solidity ^0.6.12;


// // Based on StableMath from Stability Labs Pty. Ltd.
// // https://github.com/mstable/mStable-contracts/blob/master/contracts/shared/StableMath.sol

// library StableMath {
//     using SafeMathUpgradeable for uint256;

//     /**
//      * @dev Scaling unit for use in specific calculations,
//      * where 1 * 10**18, or 1e18 represents a unit '1'
//      */
//     uint256 private constant FULL_SCALE = 1e18;

//     /***************************************
//                     Helpers
//     ****************************************/

//     /**
//      * @dev Adjust the scale of an integer
//      * @param adjustment Amount to adjust by e.g. scaleBy(1e18, -1) == 1e17
//      */
//     function scaleBy(uint256 x, int8 adjustment)
//         internal
//         pure
//         returns (uint256)
//     {
//         if (adjustment > 0) {
//             x = x.mul(10**uint256(adjustment));
//         } else if (adjustment < 0) {
//             x = x.div(10**uint256(adjustment * -1));
//         }
//         return x;
//     }

//     /***************************************
//                Precise Arithmetic
//     ****************************************/

//     /**
//      * @dev Multiplies two precise units, and then truncates by the full scale
//      * @param x Left hand input to multiplication
//      * @param y Right hand input to multiplication
//      * @return Result after multiplying the two inputs and then dividing by the shared
//      *         scale unit
//      */
//     function mulTruncate(uint256 x, uint256 y) internal pure returns (uint256) {
//         return mulTruncateScale(x, y, FULL_SCALE);
//     }

//     /**
//      * @dev Multiplies two precise units, and then truncates by the given scale. For example,
//      * when calculating 90% of 10e18, (10e18 * 9e17) / 1e18 = (9e36) / 1e18 = 9e18
//      * @param x Left hand input to multiplication
//      * @param y Right hand input to multiplication
//      * @param scale Scale unit
//      * @return Result after multiplying the two inputs and then dividing by the shared
//      *         scale unit
//      */
//     function mulTruncateScale(
//         uint256 x,
//         uint256 y,
//         uint256 scale
//     ) internal pure returns (uint256) {
//         // e.g. assume scale = fullScale
//         // z = 10e18 * 9e17 = 9e36
//         uint256 z = x.mul(y);
//         // return 9e38 / 1e18 = 9e18
//         return z.div(scale);
//     }

//     /**
//      * @dev Multiplies two precise units, and then truncates by the full scale, rounding up the result
//      * @param x Left hand input to multiplication
//      * @param y Right hand input to multiplication
//      * @return Result after multiplying the two inputs and then dividing by the shared
//      *          scale unit, rounded up to the closest base unit.
//      */
//     function mulTruncateCeil(uint256 x, uint256 y)
//         internal
//         pure
//         returns (uint256)
//     {
//         // e.g. 8e17 * 17268172638 = 138145381104e17
//         uint256 scaled = x.mul(y);
//         // e.g. 138145381104e17 + 9.99...e17 = 138145381113.99...e17
//         uint256 ceil = scaled.add(FULL_SCALE.sub(1));
//         // e.g. 13814538111.399...e18 / 1e18 = 13814538111
//         return ceil.div(FULL_SCALE);
//     }

//     /**
//      * @dev Precisely divides two units, by first scaling the left hand operand. Useful
//      *      for finding percentage weightings, i.e. 8e18/10e18 = 80% (or 8e17)
//      * @param x Left hand input to division
//      * @param y Right hand input to division
//      * @return Result after multiplying the left operand by the scale, and
//      *         executing the division on the right hand input.
//      */
//     function divPrecisely(uint256 x, uint256 y)
//         internal
//         pure
//         returns (uint256)
//     {
//         // e.g. 8e18 * 1e18 = 8e36
//         uint256 z = x.mul(FULL_SCALE);
//         // e.g. 8e36 / 10e18 = 8e17
//         return z.div(y);
//     }
// }

// // File: arb-bridge-peripherals/contracts/tokenbridge/arbitrum/IArbToken.sol


// /*
//  * Copyright 2020, Offchain Labs, Inc.
//  *
//  * Licensed under the Apache License, Version 2.0 (the "License");
//  * you may not use this file except in compliance with the License.
//  * You may obtain a copy of the License at
//  *
//  *    http://www.apache.org/licenses/LICENSE-2.0
//  *
//  * Unless required by applicable law or agreed to in writing, software
//  * distributed under the License is distributed on an "AS IS" BASIS,
//  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  * See the License for the specific language governing permissions and
//  * limitations under the License.
//  */

// /**
//  * @title Minimum expected interface for L2 token that interacts with the L2 token bridge (this is the interface necessary
//  * for a custom token that interacts with the bridge, see TestArbCustomToken.sol for an example implementation).
//  */
// pragma solidity ^0.6.11;

// interface IArbToken {
//     /**
//      * @notice should increase token supply by amount, and should (probably) only be callable by the L1 bridge.
//      */
//     function bridgeMint(address account, uint256 amount) external;

//     /**
//      * @notice should decrease token supply by amount, and should (probably) only be callable by the L1 bridge.
//      */
//     function bridgeBurn(address account, uint256 amount) external;

//     /**
//      * @return address of layer 1 token
//      */
//     function l1Address() external view returns (address);
// }

// // File: contracts/interfaces/IUSDs.sol


// pragma solidity ^0.6.12;

// interface IUSDs {
//     function mint(address _account, uint256 _amount) external;
//     function burn(address _account, uint256 _amount) external;
//     function changeSupply(uint256 _newTotalSupply) external;
//     function mintedViaUsers() external view returns (uint256);
//     function burntViaUsers() external view returns (uint256);
// }

// // File: @openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;

// /**
//  * @dev Interface of the ERC20 standard as defined in the EIP.
//  */
// interface IERC20Upgradeable {
//     /**
//      * @dev Returns the amount of tokens in existence.
//      */
//     function totalSupply() external view returns (uint256);

//     /**
//      * @dev Returns the amount of tokens owned by `account`.
//      */
//     function balanceOf(address account) external view returns (uint256);

//     /**
//      * @dev Moves `amount` tokens from the caller's account to `recipient`.
//      *
//      * Returns a boolean value indicating whether the operation succeeded.
//      *
//      * Emits a {Transfer} event.
//      */
//     function transfer(address recipient, uint256 amount) external returns (bool);

//     /**
//      * @dev Returns the remaining number of tokens that `spender` will be
//      * allowed to spend on behalf of `owner` through {transferFrom}. This is
//      * zero by default.
//      *
//      * This value changes when {approve} or {transferFrom} are called.
//      */
//     function allowance(address owner, address spender) external view returns (uint256);

//     /**
//      * @dev Sets `amount` as the allowance of `spender` over the caller's tokens.
//      *
//      * Returns a boolean value indicating whether the operation succeeded.
//      *
//      * IMPORTANT: Beware that changing an allowance with this method brings the risk
//      * that someone may use both the old and the new allowance by unfortunate
//      * transaction ordering. One possible solution to mitigate this race
//      * condition is to first reduce the spender's allowance to 0 and set the
//      * desired value afterwards:
//      * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
//      *
//      * Emits an {Approval} event.
//      */
//     function approve(address spender, uint256 amount) external returns (bool);

//     /**
//      * @dev Moves `amount` tokens from `sender` to `recipient` using the
//      * allowance mechanism. `amount` is then deducted from the caller's
//      * allowance.
//      *
//      * Returns a boolean value indicating whether the operation succeeded.
//      *
//      * Emits a {Transfer} event.
//      */
//     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

//     /**
//      * @dev Emitted when `value` tokens are moved from one account (`from`) to
//      * another (`to`).
//      *
//      * Note that `value` may be zero.
//      */
//     event Transfer(address indexed from, address indexed to, uint256 value);

//     /**
//      * @dev Emitted when the allowance of a `spender` for an `owner` is set by
//      * a call to {approve}. `value` is the new allowance.
//      */
//     event Approval(address indexed owner, address indexed spender, uint256 value);
// }

// // File: @openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;





// /**
//  * @dev Implementation of the {IERC20} interface.
//  *
//  * This implementation is agnostic to the way tokens are created. This means
//  * that a supply mechanism has to be added in a derived contract using {_mint}.
//  * For a generic mechanism see {ERC20PresetMinterPauser}.
//  *
//  * TIP: For a detailed writeup see our guide
//  * https://forum.zeppelin.solutions/t/how-to-implement-erc20-supply-mechanisms/226[How
//  * to implement supply mechanisms].
//  *
//  * We have followed general OpenZeppelin guidelines: functions revert instead
//  * of returning `false` on failure. This behavior is nonetheless conventional
//  * and does not conflict with the expectations of ERC20 applications.
//  *
//  * Additionally, an {Approval} event is emitted on calls to {transferFrom}.
//  * This allows applications to reconstruct the allowance for all accounts just
//  * by listening to said events. Other implementations of the EIP may not emit
//  * these events, as it isn't required by the specification.
//  *
//  * Finally, the non-standard {decreaseAllowance} and {increaseAllowance}
//  * functions have been added to mitigate the well-known issues around setting
//  * allowances. See {IERC20-approve}.
//  */
// contract ERC20Upgradeable is Initializable, ContextUpgradeable, IERC20Upgradeable {
//     using SafeMathUpgradeable for uint256;

//     mapping (address => uint256) private _balances;

//     mapping (address => mapping (address => uint256)) private _allowances;

//     uint256 private _totalSupply;

//     string private _name;
//     string private _symbol;
//     uint8 private _decimals;

//     /**
//      * @dev Sets the values for {name} and {symbol}, initializes {decimals} with
//      * a default value of 18.
//      *
//      * To select a different value for {decimals}, use {_setupDecimals}.
//      *
//      * All three of these values are immutable: they can only be set once during
//      * construction.
//      */
//     function __ERC20_init(string memory name_, string memory symbol_) internal initializer {
//         __Context_init_unchained();
//         __ERC20_init_unchained(name_, symbol_);
//     }

//     function __ERC20_init_unchained(string memory name_, string memory symbol_) internal initializer {
//         _name = name_;
//         _symbol = symbol_;
//         _decimals = 18;
//     }

//     /**
//      * @dev Returns the name of the token.
//      */
//     function name() public view virtual returns (string memory) {
//         return _name;
//     }

//     /**
//      * @dev Returns the symbol of the token, usually a shorter version of the
//      * name.
//      */
//     function symbol() public view virtual returns (string memory) {
//         return _symbol;
//     }

//     /**
//      * @dev Returns the number of decimals used to get its user representation.
//      * For example, if `decimals` equals `2`, a balance of `505` tokens should
//      * be displayed to a user as `5,05` (`505 / 10 ** 2`).
//      *
//      * Tokens usually opt for a value of 18, imitating the relationship between
//      * Ether and Wei. This is the value {ERC20} uses, unless {_setupDecimals} is
//      * called.
//      *
//      * NOTE: This information is only used for _display_ purposes: it in
//      * no way affects any of the arithmetic of the contract, including
//      * {IERC20-balanceOf} and {IERC20-transfer}.
//      */
//     function decimals() public view virtual returns (uint8) {
//         return _decimals;
//     }

//     /**
//      * @dev See {IERC20-totalSupply}.
//      */
//     function totalSupply() public view virtual override returns (uint256) {
//         return _totalSupply;
//     }

//     /**
//      * @dev See {IERC20-balanceOf}.
//      */
//     function balanceOf(address account) public view virtual override returns (uint256) {
//         return _balances[account];
//     }

//     /**
//      * @dev See {IERC20-transfer}.
//      *
//      * Requirements:
//      *
//      * - `recipient` cannot be the zero address.
//      * - the caller must have a balance of at least `amount`.
//      */
//     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
//         _transfer(_msgSender(), recipient, amount);
//         return true;
//     }

//     /**
//      * @dev See {IERC20-allowance}.
//      */
//     function allowance(address owner, address spender) public view virtual override returns (uint256) {
//         return _allowances[owner][spender];
//     }

//     /**
//      * @dev See {IERC20-approve}.
//      *
//      * Requirements:
//      *
//      * - `spender` cannot be the zero address.
//      */
//     function approve(address spender, uint256 amount) public virtual override returns (bool) {
//         _approve(_msgSender(), spender, amount);
//         return true;
//     }

//     /**
//      * @dev See {IERC20-transferFrom}.
//      *
//      * Emits an {Approval} event indicating the updated allowance. This is not
//      * required by the EIP. See the note at the beginning of {ERC20}.
//      *
//      * Requirements:
//      *
//      * - `sender` and `recipient` cannot be the zero address.
//      * - `sender` must have a balance of at least `amount`.
//      * - the caller must have allowance for ``sender``'s tokens of at least
//      * `amount`.
//      */
//     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
//         _transfer(sender, recipient, amount);
//         _approve(sender, _msgSender(), _allowances[sender][_msgSender()].sub(amount, "ERC20: transfer amount exceeds allowance"));
//         return true;
//     }

//     /**
//      * @dev Atomically increases the allowance granted to `spender` by the caller.
//      *
//      * This is an alternative to {approve} that can be used as a mitigation for
//      * problems described in {IERC20-approve}.
//      *
//      * Emits an {Approval} event indicating the updated allowance.
//      *
//      * Requirements:
//      *
//      * - `spender` cannot be the zero address.
//      */
//     function increaseAllowance(address spender, uint256 addedValue) public virtual returns (bool) {
//         _approve(_msgSender(), spender, _allowances[_msgSender()][spender].add(addedValue));
//         return true;
//     }

//     /**
//      * @dev Atomically decreases the allowance granted to `spender` by the caller.
//      *
//      * This is an alternative to {approve} that can be used as a mitigation for
//      * problems described in {IERC20-approve}.
//      *
//      * Emits an {Approval} event indicating the updated allowance.
//      *
//      * Requirements:
//      *
//      * - `spender` cannot be the zero address.
//      * - `spender` must have allowance for the caller of at least
//      * `subtractedValue`.
//      */
//     function decreaseAllowance(address spender, uint256 subtractedValue) public virtual returns (bool) {
//         _approve(_msgSender(), spender, _allowances[_msgSender()][spender].sub(subtractedValue, "ERC20: decreased allowance below zero"));
//         return true;
//     }

//     /**
//      * @dev Moves tokens `amount` from `sender` to `recipient`.
//      *
//      * This is internal function is equivalent to {transfer}, and can be used to
//      * e.g. implement automatic token fees, slashing mechanisms, etc.
//      *
//      * Emits a {Transfer} event.
//      *
//      * Requirements:
//      *
//      * - `sender` cannot be the zero address.
//      * - `recipient` cannot be the zero address.
//      * - `sender` must have a balance of at least `amount`.
//      */
//     function _transfer(address sender, address recipient, uint256 amount) internal virtual {
//         require(sender != address(0), "ERC20: transfer from the zero address");
//         require(recipient != address(0), "ERC20: transfer to the zero address");

//         _beforeTokenTransfer(sender, recipient, amount);

//         _balances[sender] = _balances[sender].sub(amount, "ERC20: transfer amount exceeds balance");
//         _balances[recipient] = _balances[recipient].add(amount);
//         emit Transfer(sender, recipient, amount);
//     }

//     /** @dev Creates `amount` tokens and assigns them to `account`, increasing
//      * the total supply.
//      *
//      * Emits a {Transfer} event with `from` set to the zero address.
//      *
//      * Requirements:
//      *
//      * - `to` cannot be the zero address.
//      */
//     function _mint(address account, uint256 amount) internal virtual {
//         require(account != address(0), "ERC20: mint to the zero address");

//         _beforeTokenTransfer(address(0), account, amount);

//         _totalSupply = _totalSupply.add(amount);
//         _balances[account] = _balances[account].add(amount);
//         emit Transfer(address(0), account, amount);
//     }

//     /**
//      * @dev Destroys `amount` tokens from `account`, reducing the
//      * total supply.
//      *
//      * Emits a {Transfer} event with `to` set to the zero address.
//      *
//      * Requirements:
//      *
//      * - `account` cannot be the zero address.
//      * - `account` must have at least `amount` tokens.
//      */
//     function _burn(address account, uint256 amount) internal virtual {
//         require(account != address(0), "ERC20: burn from the zero address");

//         _beforeTokenTransfer(account, address(0), amount);

//         _balances[account] = _balances[account].sub(amount, "ERC20: burn amount exceeds balance");
//         _totalSupply = _totalSupply.sub(amount);
//         emit Transfer(account, address(0), amount);
//     }

//     /**
//      * @dev Sets `amount` as the allowance of `spender` over the `owner` s tokens.
//      *
//      * This internal function is equivalent to `approve`, and can be used to
//      * e.g. set automatic allowances for certain subsystems, etc.
//      *
//      * Emits an {Approval} event.
//      *
//      * Requirements:
//      *
//      * - `owner` cannot be the zero address.
//      * - `spender` cannot be the zero address.
//      */
//     function _approve(address owner, address spender, uint256 amount) internal virtual {
//         require(owner != address(0), "ERC20: approve from the zero address");
//         require(spender != address(0), "ERC20: approve to the zero address");

//         _allowances[owner][spender] = amount;
//         emit Approval(owner, spender, amount);
//     }

//     /**
//      * @dev Sets {decimals} to a value other than the default one of 18.
//      *
//      * WARNING: This function should only be called from the constructor. Most
//      * applications that interact with token contracts will not expect
//      * {decimals} to ever change, and may work incorrectly if it does.
//      */
//     function _setupDecimals(uint8 decimals_) internal virtual {
//         _decimals = decimals_;
//     }

//     /**
//      * @dev Hook that is called before any transfer of tokens. This includes
//      * minting and burning.
//      *
//      * Calling conditions:
//      *
//      * - when `from` and `to` are both non-zero, `amount` of ``from``'s tokens
//      * will be to transferred to `to`.
//      * - when `from` is zero, `amount` tokens will be minted for `to`.
//      * - when `to` is zero, `amount` of ``from``'s tokens will be burned.
//      * - `from` and `to` are never both zero.
//      *
//      * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
//      */
//     function _beforeTokenTransfer(address from, address to, uint256 amount) internal virtual { }
//     uint256[44] private __gap;
// }

// // File: @openzeppelin/contracts-upgradeable/drafts/IERC20PermitUpgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;

// /**
//  * @dev Interface of the ERC20 Permit extension allowing approvals to be made via signatures, as defined in
//  * https://eips.ethereum.org/EIPS/eip-2612[EIP-2612].
//  *
//  * Adds the {permit} method, which can be used to change an account's ERC20 allowance (see {IERC20-allowance}) by
//  * presenting a message signed by the account. By not relying on `{IERC20-approve}`, the token holder account doesn't
//  * need to send a transaction, and thus is not required to hold Ether at all.
//  */
// interface IERC20PermitUpgradeable {
//     /**
//      * @dev Sets `value` as the allowance of `spender` over `owner`'s tokens,
//      * given `owner`'s signed approval.
//      *
//      * IMPORTANT: The same issues {IERC20-approve} has related to transaction
//      * ordering also apply here.
//      *
//      * Emits an {Approval} event.
//      *
//      * Requirements:
//      *
//      * - `spender` cannot be the zero address.
//      * - `deadline` must be a timestamp in the future.
//      * - `v`, `r` and `s` must be a valid `secp256k1` signature from `owner`
//      * over the EIP712-formatted function arguments.
//      * - the signature must use ``owner``'s current nonce (see {nonces}).
//      *
//      * For more information on the signature format, see the
//      * https://eips.ethereum.org/EIPS/eip-2612#specification[relevant EIP
//      * section].
//      */
//     function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) external;

//     /**
//      * @dev Returns the current nonce for `owner`. This value must be
//      * included whenever a signature is generated for {permit}.
//      *
//      * Every successful call to {permit} increases ``owner``'s nonce by one. This
//      * prevents a signature from being used multiple times.
//      */
//     function nonces(address owner) external view returns (uint256);

//     /**
//      * @dev Returns the domain separator used in the encoding of the signature for `permit`, as defined by {EIP712}.
//      */
//     // solhint-disable-next-line func-name-mixedcase
//     function DOMAIN_SEPARATOR() external view returns (bytes32);
// }

// // File: @openzeppelin/contracts-upgradeable/cryptography/ECDSAUpgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;

// /**
//  * @dev Elliptic Curve Digital Signature Algorithm (ECDSA) operations.
//  *
//  * These functions can be used to verify that a message was signed by the holder
//  * of the private keys of a given address.
//  */
// library ECDSAUpgradeable {
//     /**
//      * @dev Returns the address that signed a hashed message (`hash`) with
//      * `signature`. This address can then be used for verification purposes.
//      *
//      * The `ecrecover` EVM opcode allows for malleable (non-unique) signatures:
//      * this function rejects them by requiring the `s` value to be in the lower
//      * half order, and the `v` value to be either 27 or 28.
//      *
//      * IMPORTANT: `hash` _must_ be the result of a hash operation for the
//      * verification to be secure: it is possible to craft signatures that
//      * recover to arbitrary addresses for non-hashed data. A safe way to ensure
//      * this is by receiving a hash of the original message (which may otherwise
//      * be too long), and then calling {toEthSignedMessageHash} on it.
//      */
//     function recover(bytes32 hash, bytes memory signature) internal pure returns (address) {
//         // Check the signature length
//         if (signature.length != 65) {
//             revert("ECDSA: invalid signature length");
//         }

//         // Divide the signature in r, s and v variables
//         bytes32 r;
//         bytes32 s;
//         uint8 v;

//         // ecrecover takes the signature parameters, and the only way to get them
//         // currently is to use assembly.
//         // solhint-disable-next-line no-inline-assembly
//         assembly {
//             r := mload(add(signature, 0x20))
//             s := mload(add(signature, 0x40))
//             v := byte(0, mload(add(signature, 0x60)))
//         }

//         return recover(hash, v, r, s);
//     }

//     /**
//      * @dev Overload of {ECDSA-recover-bytes32-bytes-} that receives the `v`,
//      * `r` and `s` signature fields separately.
//      */
//     function recover(bytes32 hash, uint8 v, bytes32 r, bytes32 s) internal pure returns (address) {
//         // EIP-2 still allows signature malleability for ecrecover(). Remove this possibility and make the signature
//         // unique. Appendix F in the Ethereum Yellow paper (https://ethereum.github.io/yellowpaper/paper.pdf), defines
//         // the valid range for s in (281): 0 < s < secp256k1n ÷ 2 + 1, and for v in (282): v ∈ {27, 28}. Most
//         // signatures from current libraries generate a unique signature with an s-value in the lower half order.
//         //
//         // If your library generates malleable signatures, such as s-values in the upper range, calculate a new s-value
//         // with 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 - s1 and flip v from 27 to 28 or
//         // vice versa. If your library also generates signatures with 0/1 for v instead 27/28, add 27 to v to accept
//         // these malleable signatures as well.
//         require(uint256(s) <= 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0, "ECDSA: invalid signature 's' value");
//         require(v == 27 || v == 28, "ECDSA: invalid signature 'v' value");

//         // If the signature is valid (and not malleable), return the signer address
//         address signer = ecrecover(hash, v, r, s);
//         require(signer != address(0), "ECDSA: invalid signature");

//         return signer;
//     }

//     /**
//      * @dev Returns an Ethereum Signed Message, created from a `hash`. This
//      * replicates the behavior of the
//      * https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sign[`eth_sign`]
//      * JSON-RPC method.
//      *
//      * See {recover}.
//      */
//     function toEthSignedMessageHash(bytes32 hash) internal pure returns (bytes32) {
//         // 32 is the length in bytes of hash,
//         // enforced by the type signature above
//         return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
//     }
// }

// // File: @openzeppelin/contracts-upgradeable/utils/CountersUpgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;


// /**
//  * @title Counters
//  * @author Matt Condon (@shrugs)
//  * @dev Provides counters that can only be incremented or decremented by one. This can be used e.g. to track the number
//  * of elements in a mapping, issuing ERC721 ids, or counting request ids.
//  *
//  * Include with `using Counters for Counters.Counter;`
//  * Since it is not possible to overflow a 256 bit integer with increments of one, `increment` can skip the {SafeMath}
//  * overflow check, thereby saving gas. This does assume however correct usage, in that the underlying `_value` is never
//  * directly accessed.
//  */
// library CountersUpgradeable {
//     using SafeMathUpgradeable for uint256;

//     struct Counter {
//         // This variable should never be directly accessed by users of the library: interactions must be restricted to
//         // the library's function. As of Solidity v0.5.2, this cannot be enforced, though there is a proposal to add
//         // this feature: see https://github.com/ethereum/solidity/issues/4637
//         uint256 _value; // default: 0
//     }

//     function current(Counter storage counter) internal view returns (uint256) {
//         return counter._value;
//     }

//     function increment(Counter storage counter) internal {
//         // The {SafeMath} overflow check can be skipped here, see the comment at the top
//         counter._value += 1;
//     }

//     function decrement(Counter storage counter) internal {
//         counter._value = counter._value.sub(1);
//     }
// }

// // File: @openzeppelin/contracts-upgradeable/drafts/EIP712Upgradeable.sol



// pragma solidity >=0.6.0 <0.8.0;


// /**
//  * @dev https://eips.ethereum.org/EIPS/eip-712[EIP 712] is a standard for hashing and signing of typed structured data.
//  *
//  * The encoding specified in the EIP is very generic, and such a generic implementation in Solidity is not feasible,
//  * thus this contract does not implement the encoding itself. Protocols need to implement the type-specific encoding
//  * they need in their contracts using a combination of `abi.encode` and `keccak256`.
//  *
//  * This contract implements the EIP 712 domain separator ({_domainSeparatorV4}) that is used as part of the encoding
//  * scheme, and the final step of the encoding to obtain the message digest that is then signed via ECDSA
//  * ({_hashTypedDataV4}).
//  *
//  * The implementation of the domain separator was designed to be as efficient as possible while still properly updating
//  * the chain id to protect against replay attacks on an eventual fork of the chain.
//  *
//  * NOTE: This contract implements the version of the encoding known as "v4", as implemented by the JSON RPC method
//  * https://docs.metamask.io/guide/signing-data.html[`eth_signTypedDataV4` in MetaMask].
//  *
//  * _Available since v3.4._
//  */
// abstract contract EIP712Upgradeable is Initializable {
//     /* solhint-disable var-name-mixedcase */
//     bytes32 private _HASHED_NAME;
//     bytes32 private _HASHED_VERSION;
//     bytes32 private constant _TYPE_HASH = keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)");
//     /* solhint-enable var-name-mixedcase */

//     /**
//      * @dev Initializes the domain separator and parameter caches.
//      *
//      * The meaning of `name` and `version` is specified in
//      * https://eips.ethereum.org/EIPS/eip-712#definition-of-domainseparator[EIP 712]:
//      *
//      * - `name`: the user readable name of the signing domain, i.e. the name of the DApp or the protocol.
//      * - `version`: the current major version of the signing domain.
//      *
//      * NOTE: These parameters cannot be changed except through a xref:learn::upgrading-smart-contracts.adoc[smart
//      * contract upgrade].
//      */
//     function __EIP712_init(string memory name, string memory version) internal initializer {
//         __EIP712_init_unchained(name, version);
//     }

//     function __EIP712_init_unchained(string memory name, string memory version) internal initializer {
//         bytes32 hashedName = keccak256(bytes(name));
//         bytes32 hashedVersion = keccak256(bytes(version));
//         _HASHED_NAME = hashedName;
//         _HASHED_VERSION = hashedVersion;
//     }

//     /**
//      * @dev Returns the domain separator for the current chain.
//      */
//     function _domainSeparatorV4() internal view returns (bytes32) {
//         return _buildDomainSeparator(_TYPE_HASH, _EIP712NameHash(), _EIP712VersionHash());
//     }

//     function _buildDomainSeparator(bytes32 typeHash, bytes32 name, bytes32 version) private view returns (bytes32) {
//         return keccak256(
//             abi.encode(
//                 typeHash,
//                 name,
//                 version,
//                 _getChainId(),
//                 address(this)
//             )
//         );
//     }

//     /**
//      * @dev Given an already https://eips.ethereum.org/EIPS/eip-712#definition-of-hashstruct[hashed struct], this
//      * function returns the hash of the fully encoded EIP712 message for this domain.
//      *
//      * This hash can be used together with {ECDSA-recover} to obtain the signer of a message. For example:
//      *
//      * ```solidity
//      * bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
//      *     keccak256("Mail(address to,string contents)"),
//      *     mailTo,
//      *     keccak256(bytes(mailContents))
//      * )));
//      * address signer = ECDSA.recover(digest, signature);
//      * ```
//      */
//     function _hashTypedDataV4(bytes32 structHash) internal view virtual returns (bytes32) {
//         return keccak256(abi.encodePacked("\x19\x01", _domainSeparatorV4(), structHash));
//     }

//     function _getChainId() private view returns (uint256 chainId) {
//         this; // silence state mutability warning without generating bytecode - see https://github.com/ethereum/solidity/issues/2691
//         // solhint-disable-next-line no-inline-assembly
//         assembly {
//             chainId := chainid()
//         }
//     }

//     /**
//      * @dev The hash of the name parameter for the EIP712 domain.
//      *
//      * NOTE: This function reads from storage by default, but can be redefined to return a constant value if gas costs
//      * are a concern.
//      */
//     function _EIP712NameHash() internal virtual view returns (bytes32) {
//         return _HASHED_NAME;
//     }

//     /**
//      * @dev The hash of the version parameter for the EIP712 domain.
//      *
//      * NOTE: This function reads from storage by default, but can be redefined to return a constant value if gas costs
//      * are a concern.
//      */
//     function _EIP712VersionHash() internal virtual view returns (bytes32) {
//         return _HASHED_VERSION;
//     }
//     uint256[50] private __gap;
// }

// // File: @openzeppelin/contracts-upgradeable/drafts/ERC20PermitUpgradeable.sol



// pragma solidity >=0.6.5 <0.8.0;







// /**
//  * @dev Implementation of the ERC20 Permit extension allowing approvals to be made via signatures, as defined in
//  * https://eips.ethereum.org/EIPS/eip-2612[EIP-2612].
//  *
//  * Adds the {permit} method, which can be used to change an account's ERC20 allowance (see {IERC20-allowance}) by
//  * presenting a message signed by the account. By not relying on `{IERC20-approve}`, the token holder account doesn't
//  * need to send a transaction, and thus is not required to hold Ether at all.
//  *
//  * _Available since v3.4._
//  */
// abstract contract ERC20PermitUpgradeable is Initializable, ERC20Upgradeable, IERC20PermitUpgradeable, EIP712Upgradeable {
//     using CountersUpgradeable for CountersUpgradeable.Counter;

//     mapping (address => CountersUpgradeable.Counter) private _nonces;

//     // solhint-disable-next-line var-name-mixedcase
//     bytes32 private _PERMIT_TYPEHASH;

//     /**
//      * @dev Initializes the {EIP712} domain separator using the `name` parameter, and setting `version` to `"1"`.
//      *
//      * It's a good idea to use the same `name` that is defined as the ERC20 token name.
//      */
//     function __ERC20Permit_init(string memory name) internal initializer {
//         __Context_init_unchained();
//         __EIP712_init_unchained(name, "1");
//         __ERC20Permit_init_unchained(name);
//     }

//     function __ERC20Permit_init_unchained(string memory name) internal initializer {
//         _PERMIT_TYPEHASH = keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"); // to take off
//     }

//     /**
//      * @dev See {IERC20Permit-permit}.
//      */
//     function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) public virtual override {
//         // solhint-disable-next-line not-rely-on-time
//         require(block.timestamp <= deadline, "ERC20Permit: expired deadline");

//         bytes32 structHash = keccak256(
//             abi.encode(
//                 _PERMIT_TYPEHASH,
//                 owner,
//                 spender,
//                 value,
//                 _nonces[owner].current(),
//                 deadline
//             )
//         );

//         bytes32 hash = _hashTypedDataV4(structHash);

//         address signer = ECDSAUpgradeable.recover(hash, v, r, s);
//         require(signer == owner, "ERC20Permit: invalid signature");

//         _nonces[owner].increment();
//         _approve(owner, spender, value);
//     }

//     /**
//      * @dev See {IERC20Permit-nonces}.
//      */
//     function nonces(address owner) public view override returns (uint256) {
//         return _nonces[owner].current();
//     }

//     /**
//      * @dev See {IERC20Permit-DOMAIN_SEPARATOR}.
//      */
//     // solhint-disable-next-line func-name-mixedcase
//     function DOMAIN_SEPARATOR() external view override returns (bytes32) {
//         return _domainSeparatorV4();
//     }
//     uint256[49] private __gap;
// }

// // File: arb-bridge-peripherals/contracts/tokenbridge/libraries/ITransferAndCall.sol


// pragma solidity >0.6.0 <0.8.0;


// interface ITransferAndCall is IERC20Upgradeable {
//     function transferAndCall(
//         address to,
//         uint256 value,
//         bytes memory data
//     ) external returns (bool success);

//     event Transfer(address indexed from, address indexed to, uint256 value, bytes data);
// }

// /**
//  * @notice note that implementation of ITransferAndCallReceiver is not expected to return a success bool
//  */
// interface ITransferAndCallReceiver {
//     function onTokenTransfer(
//         address _sender,
//         uint256 _value,
//         bytes memory _data
//     ) external;
// }

// // File: arb-bridge-peripherals/contracts/tokenbridge/libraries/TransferAndCallToken.sol


// pragma solidity >0.6.0 <0.8.0;



// // Implementation from https://github.com/smartcontractkit/LinkToken/blob/master/contracts/v0.6/TransferAndCallToken.sol
// /**
//  * @notice based on Implementation from https://github.com/smartcontractkit/LinkToken/blob/master/contracts/v0.6/ERC677Token.sol
//  * The implementation doesn't return a bool on onTokenTransfer. This is similar to the proposed 677 standard, but still incompatible - thus we don't refer to it as such.
//  */
// abstract contract TransferAndCallToken is ERC20Upgradeable, ITransferAndCall {
//     /**
//      * @dev transfer token to a contract address with additional data if the recipient is a contact.
//      * @param _to The address to transfer to.
//      * @param _value The amount to be transferred.
//      * @param _data The extra data to be passed to the receiving contract.
//      */
//     function transferAndCall(
//         address _to,
//         uint256 _value,
//         bytes memory _data
//     ) public virtual override returns (bool success) {
//         super.transfer(_to, _value);
//         emit Transfer(msg.sender, _to, _value, _data);
//         if (isContract(_to)) {
//             contractFallback(_to, _value, _data);
//         }
//         return true;
//     }

//     // PRIVATE

//     function contractFallback(
//         address _to,
//         uint256 _value,
//         bytes memory _data
//     ) private {
//         ITransferAndCallReceiver receiver = ITransferAndCallReceiver(_to);
//         receiver.onTokenTransfer(msg.sender, _value, _data);
//     }

//     function isContract(address _addr) private view returns (bool hasCode) {
//         uint256 length;
//         assembly {
//             length := extcodesize(_addr)
//         }
//         return length > 0;
//     }
// }

// // File: arb-bridge-peripherals/contracts/tokenbridge/libraries/aeERC20.sol


// /*
//  * Copyright 2020, Offchain Labs, Inc.
//  *
//  * Licensed under the Apache License, Version 2.0 (the "License");
//  * you may not use this file except in compliance with the License.
//  * You may obtain a copy of the License at
//  *
//  *    http://www.apache.org/licenses/LICENSE-2.0
//  *
//  * Unless required by applicable law or agreed to in writing, software
//  * distributed under the License is distributed on an "AS IS" BASIS,
//  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  * See the License for the specific language governing permissions and
//  * limitations under the License.
//  */

// pragma solidity ^0.6.11;



// /// @title Arbitrum extended ERC20
// /// @notice The recommended ERC20 implementation for Layer 2 tokens
// /// @dev This implements the ERC20 standard with transferAndCall extenstion/affordances
// contract aeERC20 is ERC20PermitUpgradeable, TransferAndCallToken {
//     using AddressUpgradeable for address;

//     // constructor() public initializer {
//     //     // this is expected to be used as the logic contract behind a proxy
//     //     // override the constructor if you don't wish to use the initialize method
//     // }

//     function _initialize(
//         string memory name_,
//         string memory symbol_,
//         uint8 decimals_
//     ) internal initializer {
//         __ERC20Permit_init(name_);
//         __ERC20_init(name_, symbol_);
//         _setupDecimals(decimals_);
//     }
// }

// // File: contracts/token/USDsL2.sol


// pragma solidity >=0.6.12;









// /**
//  * NOTE that this is an ERC20 token but the invariant that the sum of
//  * balanceOf(x) for all x is not >= totalSupply(). This is a consequence of the
//  * rebasing design. Any integrations with USDs should be aware.
//  */

//  /**
//   * @title USDs Token Contract on Arbitrum (L2)
//   * @dev ERC20 compatible contract for USDs
//   * @dev support rebase feature
//   * @dev inspired by OUSD: https://github.com/OriginProtocol/origin-dollar/blob/master/contracts/contracts/token/OUSD.sol
//   * @author Sperax Foundation
//   */
// contract USDsL2V2 is aeERC20, OwnableUpgradeable, IArbToken, IUSDs, ReentrancyGuardUpgradeable {
//     using SafeMathUpgradeable for uint256;
//     using StableMath for uint256;

//     event TotalSupplyUpdated(
//         uint256 totalSupply,
//         uint256 rebasingCredits,
//         uint256 rebasingCreditsPerToken
//     );
//     event ArbitrumGatewayL1TokenChanged(address gateway, address l1token);

//     enum RebaseOptions { NotSet, OptOut, OptIn }

//     uint256 private constant MAX_SUPPLY = ~uint128(0); // (2^128) - 1
//     uint256 internal _totalSupply;    // the total supply of USDs
//     uint256 public totalMinted;    // the total num of USDs minted so far
//     uint256 public totalBurnt;     // the total num of USDs burnt so far
//     uint256 public mintedViaGateway;    // the total num of USDs minted so far
//     uint256 public burntViaGateway;     // the total num of USDs burnt so far
//     mapping(address => mapping(address => uint256)) private _allowances;
//     address public vaultAddress;    // the address where (i) all collaterals of USDs protocol reside, e.g. USDT, USDC, ETH, etc and (ii) major actions like USDs minting are initiated
//     // an user's balance of USDs is based on her balance of "credits."
//     // in a rebase process, her USDs balance will change according to her credit balance and the rebase ratio
//     mapping(address => uint256) private _creditBalances;
//     // the total number of credits of the USDs protocol
//     uint256 public rebasingCredits;
//     // the rebase ratio = num of credits / num of USDs
//     uint256 public rebasingCreditsPerToken;
//     // Frozen address/credits are non rebasing (value is held in contracts which
//     // do not receive yield unless they explicitly opt in)
//     uint256 public nonRebasingSupply;   // num of USDs that are not affected by rebase
//     mapping(address => uint256) public nonRebasingCreditsPerToken; // the rebase ratio of non-rebasing accounts just before they opt out
//     mapping(address => RebaseOptions) public rebaseState;          // the rebase state of each account, i.e. opt in or opt out

//     // Arbitrum Bridge
//     address public l2Gateway;
//     address public override l1Address;

//     function initialize(
//         string memory _nameArg,
//         string memory _symbolArg,
//         address _vaultAddress,
//         address _l2Gateway,
//         address _l1Address
//     ) public initializer {
//         aeERC20._initialize(_nameArg, _symbolArg, 18);
//         OwnableUpgradeable.__Ownable_init();
//         ReentrancyGuardUpgradeable.__ReentrancyGuard_init();
//         rebasingCreditsPerToken = 1e18;
//         vaultAddress = _vaultAddress;
//         l2Gateway = _l2Gateway;
//         l1Address = _l1Address;
//     }

//     /**
//      * @dev change the vault address
//      * @param newVault the new vault address
//      */
//     function changeVault(address newVault) external onlyOwner {
//         vaultAddress = newVault;
//     }

//     function version() public pure returns (uint) {
// 		return 2;
// 	}
    
//     /**
//      * @dev Verifies that the caller is the Savings Manager contract
//      */
//     modifier onlyVault() {
//         require(vaultAddress == msg.sender, "Caller is not the Vault");
//         _;
//     }

//     /**
//      * @dev check the current total supply of USDs
//      * @return The total supply of USDs.
//      */
//     function totalSupply() public view override returns (uint256) {
//         return _totalSupply;
//     }

//     /**
//      * @dev Gets the USDs balance of the specified address.
//      * @param _account Address to query the balance of.
//      * @return A uint256 representing the _amount of base units owned by the
//      *         specified address.
//      */
//     function balanceOf(address _account) public view override returns (uint256) {
//         if (_creditBalances[_account] == 0) return 0;
//         return
//             _creditBalances[_account].divPrecisely(_creditsPerToken(_account));
//     }

//     /**
//      * @dev Gets the credits balance of the specified address.
//      * @param _account The address to query the balance of.
//      * @return (uint256, uint256) Credit balance and credits per token of the
//      *         address
//      */
//     function creditsBalanceOf(address _account)
//         public
//         view
//         returns (uint256, uint256)
//     {
//         return (_creditBalances[_account], _creditsPerToken(_account));
//     }

//     /**
//      * @dev Transfer tokens to a specified address.
//      * @param _to the address to transfer to.
//      * @param _value the _amount to be transferred.
//      * @return true on success.
//      */
//     function transfer(address _to, uint256 _value) public override returns (bool) {
//         require(_to != address(0), "Transfer to zero address");
//         require(
//             _value <= balanceOf(msg.sender),
//             "Transfer greater than balance"
//         );

//         _executeTransfer(msg.sender, _to, _value);

//         emit Transfer(msg.sender, _to, _value);

//         return true;
//     }

//     /**
//      * @dev Transfer tokens from one address to another.
//      * @param _from The address you want to send tokens from.
//      * @param _to The address you want to transfer to.
//      * @param _value The _amount of tokens to be transferred.
//      */
//     function transferFrom(
//         address _from,
//         address _to,
//         uint256 _value
//     ) public override returns (bool) {
//         require(_to != address(0), "Transfer to zero address");
//         require(_value <= balanceOf(_from), "Transfer greater than balance");

//         // notice: allowance balnce check depends on "sub" non-negative check
//         _allowances[_from][msg.sender] = _allowances[_from][msg.sender].sub(
//             _value
//         );

//         _executeTransfer(_from, _to, _value);

//         emit Transfer(_from, _to, _value);

//         return true;
//     }

//     /**
//      * @dev Update the count of non rebasing credits in response to a transfer
//      * @param _from The address you want to send tokens from.
//      * @param _to The address you want to transfer to.
//      * @param _value Amount of USDs to transfer
//      */
//     function _executeTransfer(
//         address _from,
//         address _to,
//         uint256 _value
//     ) internal {
//         bool isNonRebasingTo = _isNonRebasingAccount(_to);
//         bool isNonRebasingFrom = _isNonRebasingAccount(_from);

//         // Credits deducted and credited might be different due to the
//         // differing creditsPerToken used by each account
//         uint256 creditsCredited = _value.mulTruncateCeil(_creditsPerToken(_to));
//         uint256 creditsDeducted = _value.mulTruncateCeil(_creditsPerToken(_from));

//         _creditBalances[_from] = _creditBalances[_from].sub(
//             creditsDeducted,
//             "Transfer amount exceeds balance"
//         );
//         _creditBalances[_to] = _creditBalances[_to].add(creditsCredited);

//         // update global stats
//         if (isNonRebasingTo && !isNonRebasingFrom) {
//             // Transfer to non-rebasing account from rebasing account, credits
//             // are removed from the non rebasing tally
//             nonRebasingSupply = nonRebasingSupply.add(_value);
//             // Update rebasingCredits by subtracting the deducted amount
//             rebasingCredits = rebasingCredits.sub(creditsDeducted);
//         } else if (!isNonRebasingTo && isNonRebasingFrom) {
//             // Transfer to rebasing account from non-rebasing account
//             // Decreasing non-rebasing credits by the amount that was sent
//             nonRebasingSupply = nonRebasingSupply.sub(_value);
//             // Update rebasingCredits by adding the credited amount
//             rebasingCredits = rebasingCredits.add(creditsCredited);
//         }
//     }

//     /**
//      * @dev Function to check the _amount of tokens that an owner has allowed to a _spender.
//      * @param _owner The address which owns the funds.
//      * @param _spender The address which will spend the funds.
//      * @return The number of tokens still available for the _spender.
//      */
//     function allowance(address _owner, address _spender)
//         public
//         view
//         override returns (uint256)
//     {
//         return _allowances[_owner][_spender];
//     }

//     /**
//      * @dev Approve the passed address to spend the specified _amount of tokens on behalf of
//      * msg.sender. This method is included for ERC20 compatibility.
//      * increaseAllowance and decreaseAllowance should be used instead.
//      * Changing an allowance with this method brings the risk that someone may transfer both
//      * the old and the new allowance - if they are both greater than zero - if a transfer
//      * transaction is mined before the later approve() call is mined.
//      *
//      * @param _spender The address which will spend the funds.
//      * @param _value The _amount of tokens to be spent.
//      */
//     function approve(address _spender, uint256 _value) public override returns (bool) {
//         _allowances[msg.sender][_spender] = _value;
//         emit Approval(msg.sender, _spender, _value);
//         return true;
//     }

//     /**
//      * @dev Increase the _amount of tokens that an owner has allowed to a _spender.
//      * This method should be used instead of approve() to avoid the double approval vulnerability
//      * described above.
//      * @param _spender The address which will spend the funds.
//      * @param _addedValue The _amount of tokens to increase the allowance by.
//      */
//     function increaseAllowance(address _spender, uint256 _addedValue)
//         public
//         override
//         returns (bool)
//     {
//         _allowances[msg.sender][_spender] = _allowances[msg.sender][_spender]
//             .add(_addedValue);
//         emit Approval(msg.sender, _spender, _allowances[msg.sender][_spender]);
//         return true;
//     }

//     /**
//      * @dev Decrease the _amount of tokens that an owner has allowed to a _spender.
//      * @param _spender The address which will spend the funds.
//      * @param _subtractedValue The _amount of tokens to decrease the allowance by.
//      */
//     function decreaseAllowance(address _spender, uint256 _subtractedValue)
//         public
//         override
//         returns (bool)
//     {
//         uint256 oldValue = _allowances[msg.sender][_spender];
//         if (_subtractedValue >= oldValue) {
//             _allowances[msg.sender][_spender] = 0;
//         } else {
//             _allowances[msg.sender][_spender] = oldValue.sub(_subtractedValue);
//         }
//         emit Approval(msg.sender, _spender, _allowances[msg.sender][_spender]);
//         return true;
//     }

//     /**
//      * @dev Mints new USDs tokens, increasing totalSupply.
//      * @param _account the account address the newly minted USDs will be attributed to
//      * @param _amount the amount of USDs that will be minted
//      */
//     function mint(address _account, uint256 _amount) external override onlyVault {
//         _mint(_account, _amount);
//     }

//     /**
//      * @dev Creates `_amount` tokens and assigns them to `_account`, increasing
//      * the total supply.
//      *
//      * Emits a {Transfer} event with `from` set to the zero address.
//      *
//      * Requirements
//      *
//      * - `to` cannot be the zero address.
//      * @param _account the account address the newly minted USDs will be attributed to
//      * @param _amount the amount of USDs that will be minted
//      */
//     function _mint(address _account, uint256 _amount) internal override nonReentrant {
//         require(_account != address(0), "Mint to the zero address");

//         bool isNonRebasingAccount = _isNonRebasingAccount(_account);

//         uint256 creditAmount = _amount.mulTruncateCeil(_creditsPerToken(_account));
//         _creditBalances[_account] = _creditBalances[_account].add(creditAmount);

//         // notice: If the account is non rebasing and doesn't have a set creditsPerToken
//         //          then set it i.e. this is a mint from a fresh contract

//         // update global stats
//         if (isNonRebasingAccount) {
//             nonRebasingSupply = nonRebasingSupply.add(_amount);
//         } else {
//             rebasingCredits = rebasingCredits.add(creditAmount);
//         }

//         _totalSupply = _totalSupply.add(_amount);
//         totalMinted = totalMinted.add(_amount);

//         require(_totalSupply < MAX_SUPPLY, "Max supply");

//         emit Transfer(address(0), _account, _amount);
//     }

//     /**
//      * @dev Burns tokens, decreasing totalSupply.
//      */
//     function burn(address account, uint256 amount) external override onlyVault {
//         _burn(account, amount);
//     }

//     /**
//      * @dev Destroys `_amount` tokens from `_account`, reducing the
//      * total supply.
//      *
//      * Emits a {Transfer} event with `to` set to the zero address.
//      *
//      * Requirements
//      *
//      * - `_account` cannot be the zero address.
//      * - `_account` must have at least `_amount` tokens.
//      */
//     function _burn(address _account, uint256 _amount) internal override nonReentrant {
//         require(_account != address(0), "Burn from the zero address");
//         if (_amount == 0) {
//             return;
//         }

//         bool isNonRebasingAccount = _isNonRebasingAccount(_account);
//         uint256 creditAmount = _amount.mulTruncateCeil(_creditsPerToken(_account));
//         uint256 currentCredits = _creditBalances[_account];

//         // Remove the credits, burning rounding errors
//         if (
//             currentCredits == creditAmount || currentCredits - 1 == creditAmount
//         ) {
//             // Handle dust from rounding
//             _creditBalances[_account] = 0;
//         } else if (currentCredits > creditAmount) {
//             _creditBalances[_account] = _creditBalances[_account].sub(
//                 creditAmount
//             );
//         } else {
//             revert("Remove exceeds balance");
//         }

//         // Remove from the credit tallies and non-rebasing supply
//         if (isNonRebasingAccount) {
//             nonRebasingSupply = nonRebasingSupply.sub(_amount);
//         } else {
//             rebasingCredits = rebasingCredits.sub(creditAmount);
//         }

//         _totalSupply = _totalSupply.sub(_amount);
//         totalBurnt = totalBurnt.add(_amount);
//         emit Transfer(_account, address(0), _amount);
//     }

//     /**
//      * @dev Get the credits per token for an account. Returns a fixed amount
//      *      if the account is non-rebasing.
//      * @param _account Address of the account.
//      */
//     function _creditsPerToken(address _account)
//         internal
//         view
//         returns (uint256)
//     {
//         if (nonRebasingCreditsPerToken[_account] != 0) {
//             return nonRebasingCreditsPerToken[_account];
//         } else {
//             return rebasingCreditsPerToken;
//         }
//     }

//     /**
//      * @dev Is an account using rebasing accounting or non-rebasing accounting?
//      *      Also, ensure contracts are non-rebasing if they have not opted in.
//      * @param _account Address of the account.
//      */
//     function _isNonRebasingAccount(address _account) internal returns (bool) {
//         bool isContract = AddressUpgradeable.isContract(_account);
//         if (isContract && rebaseState[_account] == RebaseOptions.NotSet) {
//             _ensureRebasingMigration(_account);
//         }
//         return nonRebasingCreditsPerToken[_account] > 0;
//     }

//     /**
//      * @dev Ensures internal account for rebasing and non-rebasing credits and
//      *      supply is updated following deployment of frozen yield change.
//      */
//     function _ensureRebasingMigration(address _account) internal {
//         if (nonRebasingCreditsPerToken[_account] == 0) {
//             // Set fixed credits per token for this account
//             nonRebasingCreditsPerToken[_account] = rebasingCreditsPerToken;
//             // Update non rebasing supply
//             nonRebasingSupply = nonRebasingSupply.add(balanceOf(_account));
//             // Update credit tallies
//             rebasingCredits = rebasingCredits.sub(_creditBalances[_account]);
//         }
//     }

//     /**
//      * @dev Add a contract address to the non rebasing exception list. I.e. the
//      * address's balance will be part of rebases so the account will be exposed
//      * to upside and downside.
//      */
//     function rebaseOptIn(address toOptIn) public onlyOwner nonReentrant {
//         require(_isNonRebasingAccount(toOptIn), "Account has not opted out");

//         // Convert balance into the same amount at the current exchange rate
//         uint256 newCreditBalance = _creditBalances[toOptIn]
//             .mul(rebasingCreditsPerToken)
//             .div(_creditsPerToken(toOptIn));

//         // Decreasing non rebasing supply
//         nonRebasingSupply = nonRebasingSupply.sub(balanceOf(toOptIn));

//         _creditBalances[toOptIn] = newCreditBalance;

//         // Increase rebasing credits, totalSupply remains unchanged so no
//         // adjustment necessary
//         rebasingCredits = rebasingCredits.add(_creditBalances[toOptIn]);

//         rebaseState[toOptIn] = RebaseOptions.OptIn;

//         // Delete any fixed credits per token
//         delete nonRebasingCreditsPerToken[toOptIn];
//     }

//     /**
//      * @dev Remove a contract address to the non rebasing exception list.
//      */
//     function rebaseOptOut(address toOptOut) public onlyOwner nonReentrant {
//         require(!_isNonRebasingAccount(toOptOut), "Account has not opted in");

//         // Increase non rebasing supply
//         nonRebasingSupply = nonRebasingSupply.add(balanceOf(toOptOut));
//         // Set fixed credits per token
//         nonRebasingCreditsPerToken[toOptOut] = rebasingCreditsPerToken;

//         // Decrease rebasing credits, total supply remains unchanged so no
//         // adjustment necessary
//         rebasingCredits = rebasingCredits.sub(_creditBalances[toOptOut]);

//         // Mark explicitly opted out of rebasing
//         rebaseState[toOptOut] = RebaseOptions.OptOut;
//     }

//     /**
//      * @dev The rebase function. Modify the supply without minting new tokens. This uses a change in
//      *      the exchange rate between "credits" and USDs tokens to change balances.
//      * @param _newTotalSupply New total supply of USDs.
//      */
//     function changeSupply(uint256 _newTotalSupply)
//         external
//         override
//         onlyVault
//         nonReentrant
//     {
//         require(_totalSupply > 0, "Cannot increase 0 supply");

//         // special case: if the total supply remains the same
//         if (_totalSupply == _newTotalSupply) {
//             emit TotalSupplyUpdated(
//                 _totalSupply,
//                 rebasingCredits,
//                 rebasingCreditsPerToken
//             );
//             return;
//         }

//         // check if the new total supply surpasses the MAX
//         _totalSupply = _newTotalSupply > MAX_SUPPLY
//             ? MAX_SUPPLY
//             : _newTotalSupply;
//         // calculate the new rebase ratio, i.e. credits per token
//         rebasingCreditsPerToken = rebasingCredits.divPrecisely(
//             _totalSupply.sub(nonRebasingSupply)
//         );

//         require(rebasingCreditsPerToken > 0, "Invalid change in supply");

//         // re-calculate the total supply to accomodate precision error
//         _totalSupply = rebasingCredits
//             .divPrecisely(rebasingCreditsPerToken)
//             .add(nonRebasingSupply);

//         emit TotalSupplyUpdated(
//             _totalSupply,
//             rebasingCredits,
//             rebasingCreditsPerToken
//         );
//     }

//     function mintedViaUsers() external view override returns (uint256) {
//         return totalMinted.sub(mintedViaGateway);
//     }

//     function burntViaUsers() external view override returns (uint256) {
//         return totalBurnt.sub(burntViaGateway);
//     }

//     // Arbitrum Bridge
//     /**
//      * @notice change the arbitrum bridge address and corresponding L1 token address
//      * @dev normally this function should not be called after token registration
//      * @param newL2Gateway the new bridge address
//      * @param newL1Address the new router address
//      */
//     function changeArbToken(address newL2Gateway, address newL1Address) external onlyOwner {
//         l2Gateway = newL2Gateway;
//         l1Address = newL1Address;
//         emit ArbitrumGatewayL1TokenChanged(l2Gateway, l1Address);
//     }

//     modifier onlyGateway() {
//         require(msg.sender == l2Gateway, "ONLY_l2GATEWAY");
//         _;
//     }

//     function bridgeMint(address account, uint256 amount) external override onlyGateway {
//         _mint(account, amount);
//         mintedViaGateway = mintedViaGateway.add(mintedViaGateway);
//     }

//     function bridgeBurn(address account, uint256 amount) external override onlyGateway {
//         _burn(account, amount);
//         burntViaGateway = burntViaGateway.add(burntViaGateway);
//     }
// }
