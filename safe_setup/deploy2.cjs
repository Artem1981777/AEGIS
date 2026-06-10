/* AEGIS — Safe + Allowance Module deployer (fresh agent delegate)
   Stages:
     node deploy.cjs setup   deploy Safe, enable module, add delegate, set daily cap
     node deploy.cjs pull    delegate pulls 1 USDT from the Safe (live on-chain PoC)
     node deploy.cjs status   print allowance + balances
   Owner = governor (.governor_key). Delegate = fresh key (.delegate_key, auto-generated).
   Treasury is funded from the cloud wallet via TWAK between setup and pull. */
const fs = require('fs');
const os = require('os');
const path = require('path');
const { ethers } = require('ethers');
const safeDeploy = require('@safe-global/safe-deployments');
const modDeploy = require('@safe-global/safe-modules-deployments');

const AEGIS = path.join(os.homedir(), 'AEGIS');
const RPC = 'https://bsc-dataseed.binance.org';
const CHAIN_ID = 56;
const NET = '56';
const VERSION = '1.3.0';
const USDT = '0x55d398326f99059fF775485246999027B3197955';
const ONE = 10n ** 18n;
const CAP = 5n * ONE;
const PULL = 1n * ONE;
const RESET_MIN = 1440;
const SALT = 20260610n;
const DELEGATE_GAS = ethers.parseEther('0.0008');
const GOV_KEY_FILE = path.join(AEGIS, '.governor_key');
const DEL_KEY_FILE = path.join(AEGIS, '.delegate_key');
const SAFE_FILE = path.join(AEGIS, '.safe_address');
const AM_FALLBACK = '0xCFbFaC74C26F8647cBDb8c5caf80BB5b32E43134';

function readKey(f) { return fs.readFileSync(f, 'utf8').trim().replace(/^0x/, ''); }
function loadSafe() { return fs.existsSync(SAFE_FILE) ? fs.readFileSync(SAFE_FILE, 'utf8').trim() : null; }

async function main() {
  const stage = (process.argv[2] || 'setup').toLowerCase();
  const provider = new ethers.JsonRpcProvider(RPC, CHAIN_ID);

  const governor = new ethers.Wallet('0x' + readKey(GOV_KEY_FILE), provider);
  if (!fs.existsSync(DEL_KEY_FILE)) {
    const w = ethers.Wallet.createRandom();
    fs.writeFileSync(DEL_KEY_FILE, w.privateKey.replace(/^0x/, ''), { mode: 0o600 });
    console.log('GENERATED_DELEGATE=' + w.address);
  }
  const delegate = new ethers.Wallet('0x' + readKey(DEL_KEY_FILE), provider);
  console.log('GOVERNOR=' + governor.address);
  console.log('DELEGATE=' + delegate.address);

  const pf = safeDeploy.getProxyFactoryDeployment({ version: VERSION, network: NET });
  const singleton = safeDeploy.getSafeL2SingletonDeployment({ version: VERSION, network: NET });
  const fbh = safeDeploy.getCompatibilityFallbackHandlerDeployment({ version: VERSION, network: NET });
  const am = modDeploy.getAllowanceModuleDeployment({ network: NET }) || modDeploy.getAllowanceModuleDeployment({});

  const PF_ADDR = pf.networkAddresses[NET];
  const SINGLETON_ADDR = singleton.networkAddresses[NET];
  const FBH_ADDR = fbh.networkAddresses[NET];
  const AM_ADDR = (am.networkAddresses && am.networkAddresses[NET]) || AM_FALLBACK;

  const proxyFactory = new ethers.Contract(PF_ADDR, pf.abi, governor);
  const safeIface = new ethers.Interface(singleton.abi);
  const amIface = new ethers.Interface(am.abi);
  const preSig = '0x' + '0'.repeat(24) + governor.address.slice(2).toLowerCase() + '0'.repeat(64) + '01';

  async function execTx(safeAddr, to, data) {
    const safe = new ethers.Contract(safeAddr, singleton.abi, governor);
    const tx = await safe.execTransaction(to, 0, data, 0, 0, 0, 0, ethers.ZeroAddress, ethers.ZeroAddress, preSig);
    return (await tx.wait()).hash;
  }

  if (stage === 'setup') {
    const gbal = await provider.getBalance(governor.address);
    console.log('GOV_BNB=' + ethers.formatEther(gbal));
    if (gbal < ethers.parseEther('0.008')) {
      console.error('ERROR: governor low on BNB. Fund it via TWAK first: twak transfer --to ' + governor.address + ' --amount 0.015 --token c20000714');
      process.exit(10);
    }
    if ((await provider.getBalance(delegate.address)) < DELEGATE_GAS) {
      const t = await governor.sendTransaction({ to: delegate.address, value: DELEGATE_GAS });
      await t.wait();
      console.log('FUNDED_DELEGATE_GAS_tx=' + t.hash);
    }
    let safeAddr = loadSafe();
    if (safeAddr && (await provider.getCode(safeAddr)) !== '0x') {
      console.log('SAFE_EXISTS=' + safeAddr);
    } else {
      const setupData = safeIface.encodeFunctionData('setup', [
        [governor.address], 1, ethers.ZeroAddress, '0x', FBH_ADDR, ethers.ZeroAddress, 0, ethers.ZeroAddress
      ]);
      const tx = await proxyFactory.createProxyWithNonce(SINGLETON_ADDR, setupData, SALT);
      const r = await tx.wait();
      for (const log of r.logs) {
        try { const p = proxyFactory.interface.parseLog(log); if (p && p.name === 'ProxyCreation') safeAddr = p.args[0]; } catch (e) {}
      }
      if (!safeAddr) { console.error('ERROR: ProxyCreation not found'); process.exit(11); }
      fs.writeFileSync(SAFE_FILE, safeAddr);
      console.log('SAFE_DEPLOYED=' + safeAddr + ' tx=' + r.hash);
    }
    const safe = new ethers.Contract(safeAddr, singleton.abi, governor);
    if (!(await safe.isModuleEnabled(AM_ADDR))) {
      console.log('ENABLE_MODULE_tx=' + await execTx(safeAddr, safeAddr, safeIface.encodeFunctionData('enableModule', [AM_ADDR])));
    } else { console.log('MODULE_ALREADY_ENABLED=' + AM_ADDR); }
    console.log('ADD_DELEGATE_tx=' + await execTx(safeAddr, AM_ADDR, amIface.encodeFunctionData('addDelegate', [delegate.address])));
    console.log('SET_ALLOWANCE_tx=' + await execTx(safeAddr, AM_ADDR, amIface.encodeFunctionData('setAllowance', [delegate.address, USDT, CAP, RESET_MIN, 0])));

    const al = await new ethers.Contract(AM_ADDR, am.abi, provider).getTokenAllowance(safeAddr, delegate.address, USDT);
    console.log('ALLOWANCE[amount,spent,resetMin,lastReset,nonce]=' + Array.from(al).map(x => x.toString()).join(','));
    console.log('---');
    console.log('SAFE_ADDRESS=' + safeAddr);
    console.log('ALLOWANCE_MODULE=' + AM_ADDR);
    console.log('NEXT: fund the Safe with 1 USDT from the cloud wallet via TWAK, then run: node deploy.cjs pull');
  } else if (stage === 'pull') {
    const safeAddr = loadSafe();
    if (!safeAddr) { console.error('ERROR: no .safe_address; run setup first'); process.exit(12); }
    const erc20 = new ethers.Contract(USDT, ['function balanceOf(address) view returns (uint256)'], provider);
    const safeUsdt = await erc20.balanceOf(safeAddr);
    console.log('SAFE_USDT=' + ethers.formatUnits(safeUsdt, 18));
    if (safeUsdt < PULL) { console.error('ERROR: Safe has < 1 USDT; fund it via TWAK first'); process.exit(13); }
    const amDel = new ethers.Contract(AM_ADDR, am.abi, delegate);
    const tx = await amDel.executeAllowanceTransfer(safeAddr, USDT, delegate.address, PULL, ethers.ZeroAddress, 0, delegate.address, '0x');
    const r = await tx.wait();
    console.log('POC_PULL_tx=' + r.hash);
    const al = await new ethers.Contract(AM_ADDR, am.abi, provider).getTokenAllowance(safeAddr, delegate.address, USDT);
    console.log('ALLOWANCE_AFTER[amount,spent,resetMin,lastReset,nonce]=' + Array.from(al).map(x => x.toString()).join(','));
    console.log('DELEGATE_USDT=' + ethers.formatUnits(await erc20.balanceOf(delegate.address), 18));
  } else if (stage === 'status') {
    const safeAddr = loadSafe();
    console.log('SAFE=' + safeAddr);
    if (safeAddr) {
      const al = await new ethers.Contract(AM_ADDR, am.abi, provider).getTokenAllowance(safeAddr, delegate.address, USDT);
      console.log('ALLOWANCE[amount,spent,resetMin,lastReset,nonce]=' + Array.from(al).map(x => x.toString()).join(','));
    }
    console.log('GOV_BNB=' + ethers.formatEther(await provider.getBalance(governor.address)));
    console.log('DEL_BNB=' + ethers.formatEther(await provider.getBalance(delegate.address)));
  } else {
    console.error('Unknown stage: ' + stage);
    process.exit(1);
  }
}
main().catch(e => { console.error('FATAL', e.message || e); process.exit(1); });
