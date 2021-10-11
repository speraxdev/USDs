const { expect } = require("chai");
const { ethers, upgrades, waffle } = require("hardhat");

// USDS => 0xc5afcA584905d4608482BD7CF0cE7276ee4Eb86e
// Oracle => 0x4E33C0eCed6e7431871502D3F3fdC62151e30e30
// USDT => 0x07de306FF27a2B630B1141956844eB1552B956B5
// USDC => 0xb7a4F3E9097C08dA09517b5aB877F7a917224ede
// DAI => 0x4f96fe3b7a6cf9725f59d353f723c1bdb64ca6aa
// WETH => 0xd0a1e359811322d97991e03f863a0c30c2cf029c

describe("VaultCore contract", function () {
  let vaultCore;
  let vaultCoreHardhatToken;
  let vaultCoreLibrary;
  let vaultCoreLibraryHardhatToken;
  let spaContract;
  let usdsContract;
  let usdtContract;
  let owner;

  beforeEach(async function () {
    // Get the ContractFactory and Signers here.
    [owner] = await ethers.getSigners();
    // To deploy our contract, we just have to call Token.deploy() and await
    // for it to be deployed(), which happens once its transaction has been
    // mined.
    vaultCoreLibrary = await ethers.getContractFactory("VaultCoreLibrary");
    vaultCoreLibraryHardhatToken = await vaultCoreLibrary.deploy();

    vaultCore = await ethers.getContractFactory("VaultCore", {
      libraries: {
        VaultCoreLibrary: vaultCoreLibraryHardhatToken.address,
      },
    });
    vaultCoreHardhatToken = await upgrades.deployProxy(vaultCore, [], {unsafeAllowLinkedLibraries: true, unsafeAllow: ['external-library-linking']});
    const ownerOfVault = await vaultCoreHardhatToken.owner();
    console.log('ownerOfVault => ', ownerOfVault);
    await vaultCoreHardhatToken.updateUSDsAddress("0xc5afcA584905d4608482BD7CF0cE7276ee4Eb86e");
    await vaultCoreHardhatToken.updateOracleAddress("0x4E33C0eCed6e7431871502D3F3fdC62151e30e30");
    await vaultCoreHardhatToken.updateCollateralInfo("0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa", true, "0x0000000000000000000000000000000000000000", false, "0x0000000000000000000000000000000000000000", false);
    await vaultCoreHardhatToken.updateCollateralInfo("0x07de306FF27a2B630B1141956844eB1552B956B5", true, "0x0000000000000000000000000000000000000000", false, "0x0000000000000000000000000000000000000000", false);
    await vaultCoreHardhatToken.updateCollateralInfo("0xb7a4F3E9097C08dA09517b5aB877F7a917224ede", true, "0x0000000000000000000000000000000000000000", false, "0x0000000000000000000000000000000000000000", false);
    await vaultCoreHardhatToken.updateMintBurnPermission(true);

    spaContract = await ethers.getContractAt("ERC20Upgradeable", "0xbb5E27Ae27A6a7D092b181FbDdAc1A1004e9adff");
    console.log('spaContract.address => ', spaContract.address);
    await spaContract.connect(owner).approve(vaultCoreHardhatToken.address, ethers.utils.parseUnits("90000000", 18));
    console.log('spa approved');

    usdtContract = await ethers.getContractAt("ERC20Upgradeable", "0x07de306FF27a2B630B1141956844eB1552B956B5");
    console.log('usdtContract.address => ', usdtContract.address);
    await usdtContract.connect(owner).approve(vaultCoreHardhatToken.address, ethers.utils.parseUnits("90000000", 18));
    console.log('usdt approved');
  
    usdsContract = await ethers.getContractAt("USDs", "0xc5afcA584905d4608482BD7CF0cE7276ee4Eb86e");
    console.log('usdsContract.address => ', usdsContract.address);
    await usdsContract.connect(owner).changeVault(vaultCoreHardhatToken.address);
    console.log('USDs vault changed');
    await usdsContract.connect(owner).approve(vaultCoreHardhatToken.address, ethers.utils.parseUnits("90000000", 18));
    console.log('USDs approved');
  });

  describe("PUBLIC VARIABLES", function () {
    // `it` is another Mocha function. This is the one you use to define your
    // tests. It receives the test name, and a callback function.

    // If the callback function is async, Mocha will `await` it.
    it("Should set the right swapfee flag", async function () {
      // Expect receives a value, and wraps it in an Assertion object. These
      // objects have a lot of utility methods to assert values.

      // This test expects the owner variable stored in the contract to be equal
      // to our Signer's owner.
      await vaultCoreHardhatToken.updateSwapInOutFeePermission(false, true);
      expect(await vaultCoreHardhatToken.swapfeeInAllowed()).to.equal(false);
      expect(await vaultCoreHardhatToken.swapfeeOutAllowed()).to.equal(true);
    });

    it("Should mint with usds correct number of tokens", async function () {
      const usdsBeforeAmount = await usdsContract.balanceOf(owner.address);
      console.log('usds before amount', usdsBeforeAmount.toString());
      await vaultCoreHardhatToken.mintWithUSDs("0x07de306ff27a2b630b1141956844eb1552b956b5", ethers.utils.parseUnits("34000", 16), ethers.utils.parseUnits("30", 6), ethers.utils.parseUnits("1000", 16), ethers.utils.parseUnits("1", 21));
      const usdsAfterAmount = await usdsContract.balanceOf(owner.address);
      console.log('usds after amount', usdsAfterAmount.toString());
      expect(usdsBeforeAmount.add(ethers.utils.parseUnits("34000", 16))).to.equal(usdsAfterAmount);
    });

    it("Should mint with spa correct number of tokens", async function () {
      const spaBeforeAmount = await spaContract.balanceOf(owner.address);
      const usdtBeforeAmount = await usdtContract.balanceOf(owner.address);
      const usdsBeforeAmount = await usdsContract.balanceOf(owner.address);
      await vaultCoreHardhatToken.mintWithSPA("0x07de306ff27a2b630b1141956844eb1552b956b5", ethers.utils.parseUnits("1000", 16), ethers.utils.parseUnits("34000", 16), ethers.utils.parseUnits("30"), ethers.utils.parseUnits("1", 21));
      const spaAfterAmount = await spaContract.balanceOf(owner.address);
      console.log('spa changed amount', spaAfterAmount.sub(spaBeforeAmount).toString());
      const usdsAfterAmount = await usdsContract.balanceOf(owner.address);
      console.log('usds changed amount', usdsAfterAmount.sub(usdsBeforeAmount).toString());
      const usdtAfterAmount = await usdtContract.balanceOf(owner.address);
      console.log('usdt changed amount', usdtAfterAmount.sub(usdtBeforeAmount).toString());
      expect(spaBeforeAmount.sub(ethers.utils.parseUnits("1", 19))).to.equal(spaAfterAmount);
    });

    it("Should mint with collateral correct number of tokens", async function () {
      const spaBeforeAmount = await spaContract.balanceOf(owner.address);
      const usdtBeforeAmount = await usdtContract.balanceOf(owner.address);
      const usdsBeforeAmount = await usdsContract.balanceOf(owner.address);
      await vaultCoreHardhatToken.mintWithColla("0x07de306ff27a2b630b1141956844eb1552b956b5", ethers.utils.parseUnits("25", 0), ethers.utils.parseUnits("30000", 16), ethers.utils.parseUnits("1100", 16), ethers.utils.parseUnits("1", 21));
      const spaAfterAmount = await spaContract.balanceOf(owner.address);
      console.log('spa changed amount', spaAfterAmount.sub(spaBeforeAmount).toString());
      const usdsAfterAmount = await usdsContract.balanceOf(owner.address);
      console.log('usds changed amount', usdsAfterAmount.sub(usdsBeforeAmount).toString());
      const usdtAfterAmount = await usdtContract.balanceOf(owner.address);
      console.log('usdt changed amount', usdtAfterAmount.sub(usdtBeforeAmount).toString());
      expect(usdtBeforeAmount.sub(ethers.utils.parseUnits("25", 0))).to.equal(usdtAfterAmount);
    });

    it("Should mint with ethereum correct number of tokens", async function () {
      const spaBeforeAmount = await spaContract.balanceOf(owner.address);
      const usdsBeforeAmount = await usdsContract.balanceOf(owner.address);
      const ethBeforeAmount = await waffle.provider.getBalance(owner.address);
      console.log('eth before amount', ethBeforeAmount.toString());
      const gasEst = await vaultCoreHardhatToken.estimateGas.mintWithEth(ethers.utils.parseUnits("30000", 6), ethers.utils.parseUnits("1", 9), ethers.utils.parseUnits("1", 21), {value: ethers.utils.parseUnits('8', 6), from: owner.address});
      await vaultCoreHardhatToken.mintWithEth(ethers.utils.parseUnits("30000", 6), ethers.utils.parseUnits("1", 9), ethers.utils.parseUnits("1", 21), {value: ethers.utils.parseUnits('8', 6), from: owner.address});
      const ethAfterAmount = await waffle.provider.getBalance(owner.address);
      console.log('eth changed amount', ethBeforeAmount.sub(ethAfterAmount).sub(ethers.utils.parseUnits(gasEst.toString(), 9)).toString()); const spaAfterAmount = await spaContract.balanceOf(owner.address);
      console.log('spa changed amount', spaAfterAmount.sub(spaBeforeAmount).toString());
      const usdsAfterAmount = await usdsContract.balanceOf(owner.address);
      console.log('usds changed amount', usdsAfterAmount.sub(usdsBeforeAmount).toString());
      expect(ethBeforeAmount.sub(ethers.utils.parseUnits('8', 6))).to.above(ethAfterAmount);
    });

    it("Should redeem correct number of tokens", async function () {
      const spaBeforeAmount = await spaContract.balanceOf(owner.address);
      const usdtBeforeAmount = await usdtContract.balanceOf(owner.address);
      const usdsBeforeAmount = await usdsContract.balanceOf(owner.address);
      await vaultCoreHardhatToken.redeem("0x07de306ff27a2b630b1141956844eb1552b956b5", ethers.utils.parseUnits("30000", 16), ethers.utils.parseUnits("0", 0), ethers.utils.parseUnits("1100", 16), ethers.utils.parseUnits("1", 21));
      const spaAfterAmount = await spaContract.balanceOf(owner.address);
      console.log('spa changed amount', spaAfterAmount.sub(spaBeforeAmount).toString());
      const usdsAfterAmount = await usdsContract.balanceOf(owner.address);
      console.log('usds changed amount', usdsAfterAmount.sub(usdsBeforeAmount).toString());
      const usdtAfterAmount = await usdtContract.balanceOf(owner.address);
      console.log('usdt changed amount', usdtAfterAmount.sub(usdtBeforeAmount).toString());
      expect(usdsBeforeAmount.sub(ethers.utils.parseUnits("30000", 16))).to.equal(usdsAfterAmount);
    });

    it("Should mint with usds reverted with mint & redeem paused", async function () {
      await vaultCoreHardhatToken.updateMintBurnPermission(false);
      expect(vaultCoreHardhatToken.mintWithUSDs("0x07de306ff27a2b630b1141956844eb1552b956b5", ethers.utils.parseUnits("34000", 16), ethers.utils.parseUnits("30", 6), ethers.utils.parseUnits("1000", 16), ethers.utils.parseUnits("1", 21)))
      .to.be.revertedWith("Mint & redeem paused");
    });
  });
});
