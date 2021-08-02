var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");

contract("VaultCore", async accounts => {
  it("should swapFeeIn flag toggle works", () => {
    let vaultCore;
    return VaultCore.deployed()
      .then(instance => {
        vaultCore = instance;
        return vaultCore.toggleSwapfeeInAllowed(false);
      })
      .then(() => {
        return vaultCore.calculateSwapFeeIn();
      })
      .then(swapFee => {
        assert.equal(swapFee, 0, "Swap Fee In disallowing not worked.");
      });
  });

  it("should swapFeeOut flag toggle works", () => {
    let vaultCore;
    return VaultCore.deployed()
      .then(instance => {
        vaultCore = instance;
        return vaultCore.toggleSwapfeeOutAllowed(false);
      })
      .then(() => {
        return vaultCore.calculateSwapFeeOut();
      })
      .then(swapFee => {
        assert.equal(swapFee, 0, "Swap Fee Out disallowing not worked.");
      });
  });

  it("should updating collateral list works fine", () => {
    let vaultCore;
    return VaultCore.deployed()
      .then(instance => {
        vaultCore = instance;
        return vaultCore.updateCollateralList("0x4f96fe3b7a6cf9725f59d353f723c1bdb64ca6aa", true);
      })
      .then(() => {
        assert.equal(vaultCore.supportedCollat["0x4f96fe3b7a6cf9725f59d353f723c1bdb64ca6aa"], true, "Collateral token not added to the list");
      });
  });
});