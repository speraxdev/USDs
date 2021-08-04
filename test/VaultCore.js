var VaultCore = artifacts.require("../contracts/vault/VaultCore.sol");
var Oracle = artifacts.require("../contracts/oracle/Oracle.sol");

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

  it("should mint USDs", async () => {
    let vaultCore;
    let oracle;
    oracle = await Oracle.deployed();
    vaultCore = await VaultCore.deployed();
    await oracle.updatePriceList("0x07de306ff27a2b630b1141956844eb1552b956b5", "0x2ca5A90D34cA333661083F89D831f757A9A50148", 8);
    await vaultCore.updateCollateralList("0x07de306ff27a2b630b1141956844eb1552b956b5", true);
    const initial = await web3.eth.getBalance(accounts[0]);
    console.log(`Initial: ${initial.toString()}`);
    const receipt = await vaultCore.mintWithSPA("0x07de306ff27a2b630b1141956844eb1552b956b5", 10000);
    console.log(`Response: ${JSON.stringify(receipt)}`);
    // const gasUsed = receipt.receipt.gasUsed;
    // console.log(`GasUsed: ${receipt.receipt.gasUsed}`);

    // // Obtain gasPrice from the transaction
    // const tx = await web3.eth.getTransaction(receipt.tx);
    // const gasPrice = tx.gasPrice;
    // console.log(`GasPrice: ${tx.gasPrice}`);
    
    // Final balance
    const final = await web3.eth.getBalance(accounts[0]);
    console.log(`Final: ${final.toString()}`);


    // const redeemReceipt = await vaultCore.redeem("0x07de306ff27a2b630b1141956844eb1552b956b5", 10);
    // console.log(`Second Response: ${redeemReceipt}`);
    // Final balance
    // const secondFinal = await web3.eth.getBalance(accounts[0]);
    // console.log(`Second Final: ${secondFinal.toString()}`);
    assert.equal(final.toString(), initial.toString(), "Must be equal");
  });
});