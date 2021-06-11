//To-do: fix presion

pragma solidity ^0.6.12;
import "./VaultStorage.sol";
import "../libraries/Ownable.sol";
import "../libraries/SafeERC20.sol";
import "../libraries/MyMath.sol";
import "../libraries/Helpers.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/ISperaxToken.sol";

contract VaultCore is VaultStorage, Ownable {
	using SafeERC20 for IERC20;
	using SafeMath for uint;
	using MyMath for uint;

	modifier whenMintRedeemAllowed {
		require(mintRedeemAllowed, "Mint & redeem paused");
		_;
	}


	function calculateSwapFeeIn() public returns (uint swapFeeIn) {
		return 1000;
	}
	function calculateSwapFeeOut() public returns (uint swapFeeOut) {
		return 1000;
	}


	function mint(address collaAddr, uint USDsAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr], "Collateral not supported");
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_mint(collaAddr, USDsAmt);
	}

	function _mint(
		address collaAddr,
		uint USDsAmt
	) internal whenMintRedeemAllowed {
		uint priceColla = uint(IOracle(oracleAddr).price(collaAddr));
		uint priceSPA = uint(IOracle(oracleAddr).getSPAPrice());
		uint swapFee = calculateSwapFeeIn();
		uint SPABurnAmt = USDsAmt.mul(chi).div(chiPresion).div(priceSPA);
		if (swapFee > 0) {
			SPABurnAmt = SPABurnAmt.add(SPABurnAmt.mul(swapFee).div(swapFeePresion));
		}
		ISperaxToken(SPATokenAddr).burnFrom(msg.sender, SPABurnAmt);

		//Deposit collaeral
		uint CollaDepAmt = USDsAmt.mul(chiPresion - chi).div(chiPresion).div(priceColla);
		if (swapFee > 0) {
			CollaDepAmt = CollaDepAmt.add(CollaDepAmt.mul(swapFee).div(swapFeePresion));
		}
		IERC20(collaAddr).safeTransferFrom(msg.sender, collaValut, CollaDepAmt);

		//Mint USDs
		USDsInstance.mint(msg.sender, USDsAmt);
		USDsInstance.mint(USDsFeeValut, USDsAmt.mul(swapFee).div(swapFeePresion));
	}

	function redeem(address collaAddr, uint USDsAmt)
		public
		whenMintRedeemAllowed
	{
		require(supportedCollat[collaAddr], "Collateral not supported");
		require(USDsAmt > 0, "Amount needs to be greater than 0");
		_redeem(collaAddr, USDsAmt);
	}


	function _redeem(
		address collaAddr,
		uint USDsAmt
	) internal whenMintRedeemAllowed {
		uint priceColla = uint(IOracle(oracleAddr).price(collaAddr));
		//FixedPoint.uq112x112 priceSPAuq = IOracle(oracleAddr).priceSPAuq();
		uint priceSPA = uint(IOracle(oracleAddr).getSPAPrice());
		uint swapFee = calculateSwapFeeOut();
		uint SPAMintAmt = USDsAmt.mul(chi).div(chiPresion).div(priceSPA);
		if (swapFee > 0) {
			SPAMintAmt = SPAMintAmt.sub(SPAMintAmt.mul(swapFee).div(swapFeePresion));
		}
		IERC20(collaAddr).safeTransferFrom(SPAValut, msg.sender, SPAMintAmt);

		//Unlock collaeral
		uint CollaUnlockAmt = USDsAmt.mul(chiPresion - chi).div(chiPresion).div(priceColla);
		if (swapFee > 0) {
			CollaUnlockAmt = CollaUnlockAmt.sub(CollaUnlockAmt.mul(swapFee).div(swapFeePresion));
		}
		IERC20(collaAddr).safeTransferFrom(collaValut, msg.sender, CollaUnlockAmt);

		//Burn USDs
		USDsInstance.burn(msg.sender, USDsAmt.sub(USDsAmt.mul(swapFee).div(swapFeePresion)));
		USDsInstance.transfer(USDsFeeValut, USDsAmt.mul(swapFee).div(swapFeePresion));
	}

	/**
	 * @dev Calculate the total value of assets held by the Vault and all
	 *      strategies and update the supply of USDs.
	 */
	function rebase() public {
		_rebase();
	}

	/**
	 * @dev Calculate the total value of assets held by the Vault and all
	 *      strategies and update the supply of USDs, optionaly sending a
	 *      portion of the yield to the trustee.
	 */
	function _rebase() internal {
		uint256 totalSupply = USDsInstance.totalSupply();
		uint256 vaultValue = _totalValue();

		if (vaultValue > totalSupply && totalSupply != 0) {
			USDsInstance.changeSupply(vaultValue);
		}
	}

	/**
     * @dev Determine the total value of assets held by the vault and its
     *         strategies.
     * @return value Total value in USD (1e18)
     */
    function totalValue() external view returns (uint256 value) {
        value = _totalValue();
    }

    /**
     * @dev Internal Calculate the total value of the assets held by the
     *         vault and its strategies.
     * @return value Total value in USD (1e18)
     */
    function _totalValue() internal view returns (uint256 value) {
        return _totalValueInVault().add(_totalValueInStrategies());
    }

    /**
     * @dev Internal to calculate total value of all assets held in Vault.
     * @return value in ETH (1e18)
     */
    function _totalValueInVault() internal view returns (uint256 value) {
        // for (uint256 y = 0; y < allCollat.length; y++) {
        //     IERC20 asset = IERC20(allCollat[y]);
        //     uint256 assetDecimals = Helpers.getDecimals(allCollat[y]);
        //     uint256 balance = asset.balanceOf(address(this));
        //     if (balance > 0) {
        //         value = value.add(balance.scaleBy(int8(18 - assetDecimals)));
        //     }
        // }
    }

    /**
     * @dev Internal to calculate total value of all assets held in Strategies.
     * @return value in ETH (1e18)
     */
    function _totalValueInStrategies() internal view returns (uint256 value) {
        for (uint256 i = 0; i < allStrategies.length; i++) {
            value = value.add(_totalValueInStrategy(allStrategies[i]));
        }
    }

    /**
     * @dev Internal to calculate total value of all assets held by strategy.
     * @param _strategyAddr Address of the strategy
     * @return value in ETH (1e18)
     */
    function _totalValueInStrategy(address _strategyAddr)
        internal
        view
        returns (uint256 value)
    {
        value = 0;
    }

	/**
     * @notice Get the balance of an asset held in Vault and all strategies.
     * @param _asset Address of asset
     * @return uint256 Balance of asset in decimals of asset
     */
    function checkBalance(address _asset) external view returns (uint256) {
        return _checkBalance(_asset);
    }

    /**
     * @notice Get the balance of an asset held in Vault and all strategies.
     * @param _asset Address of asset
     * @return balance Balance of asset in decimals of asset
     */
    function _checkBalance(address _asset)
        internal
        view
        returns (uint256 balance)
    {
        IERC20 asset = IERC20(_asset);
        balance = asset.balanceOf(address(this));
        // for (uint256 i = 0; i < allStrategies.length; i++) {
        //     IStrategy strategy = IStrategy(allStrategies[i]);
        //     if (strategy.supportsAsset(_asset)) {
        //         balance = balance.add(strategy.checkBalance(_asset));
        //     }
        // }
    }



}
