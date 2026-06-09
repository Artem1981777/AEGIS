// AEGIS — full on-chain Safe + Allowance Module setup. Runs entirely in Cloud Shell.
const fs = require('fs'); const os = require('os'); const path = require('path');
const { ethers } = require('ethers');
const { getProxyFactoryDeployment, getSafeL2SingletonDeployment, getCompatibilityFallbackHandlerDeployment } = require('@safe-global/safe-deployments');
const { getAllowanceModuleDeployment } = require('@safe-global/safe-modules-deployments');

const HOME = os.homedir(); const AEGIS = path.join(HOME, 'AEGIS');

// ---- config ----
const RPC = 'https://bsc-dataseed.binance.org';
const CHAIN_ID = 56;
const USDT = '0x55d398326f99059fF775485246999027B3197955'; // 18 decimals on BSC
const CLOUD_ADDR = '0xA7a448F0093c3e5cC1930031cAe4184E5BdDB67E'; // delegate (spender)
const UNIT = 10n ** 18n;
const CAP_USDT = 5n;       // on-chain daily hard cap
const DEPOSIT_USDT = 1n;   // treasury deposit for the test
const POC_PULL_USDT = 1n;  // set to 0n to skip the proof-pull and keep treasury funded
const RESET_MIN = 1440;    // daily reset
const SALT = 20260610n;
const GOV_GAS = ethers.parseEther('0.006');
const u = (n) => n * UNIT;

function loadEnv() {
  const out = {};
  for (const line of fs.readFileSync(path.join(AEGIS, '.env'), 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Za-z0-9_]+)\s*=\s*(.*)\s*$/);
    if (m) out[m[1]] = m[2].replace(/^['"]|['"]$/g, '');
  }
  return out;
}

async function main() {
  const provider = new ethers.JsonRpcProvider(RPC, CHAIN_ID);
  const env = loadEnv();

  let govPk = fs.readFileSync(path.join(AEGIS, '.governor_key'), 'utf8').trim();
  if (!govPk.startsWith('0x')) govPk = '0x' + govPk;
  const governor = new ethers.Wallet(govPk, provider);

  const pw = env.TWAK_WALLET_PASSWORD;
  if (!pw) throw new Error('TWAK_WALLET_PASSWORD not in .env');
  const ksJson = fs.readFileSync(path.join(AEGIS, 'aegis-wallet-backup.json'), 'utf8');
  const cloud = (await ethers.Wallet.fromEncryptedJson(ksJson, pw)).connect(provider);
  console.log('Governor :', governor.address);
  console.log('Cloud    :', cloud.address);
  if (cloud.address.toLowerCase() !== CLOUD_ADDR.toLowerCase())
    throw new Error('Decrypted ' + cloud.address + ' != expected ' + CLOUD_ADDR);

  const net = String(CHAIN_ID);
  const pf = getProxyFactoryDeployment({ version: '1.3.0', network: net });
  const sg = getSafeL2SingletonDeployment({ version: '1.3.0', network: net });
  const fb = getCompatibilityFallbackHandlerDeployment({ version: '1.3.0', network: net });
  const am = getAllowanceModuleDeployment({ network: net });
  if (!pf || !sg || !fb) throw new Error('Safe 1.3.0 deployment missing for BSC');
  if (!am) throw new Error('Allowance module deployment missing for BSC');
  const factoryAddr = pf.networkAddresses[net] || pf.defaultAddress;
  const singletonAddr = sg.networkAddresses[net] || sg.defaultAddress;
  const fbAddr = fb.networkAddresses[net] || fb.defaultAddress;
  const moduleAddr = (am.networkAddresses && am.networkAddresses[net]) || am.defaultAddress;
  console.log('Factory  :', factoryAddr, '\nSingleton:', singletonAddr, '\nModule   :', moduleAddr);

  const safeAbi = sg.abi, factoryAbi = pf.abi, moduleAbi = am.abi;
  const erc20Abi = ['function transfer(address,uint256) returns (bool)', 'function balanceOf(address) view returns (uint256)'];
  const safeIface = new ethers.Interface(safeAbi);
  const mIface = new ethers.Interface(moduleAbi);

  // 0) ensure governor has gas
  if ((await provider.getBalance(governor.address)) < ethers.parseEther('0.004')) {
    console.log('Funding governor gas from cloud...');
    const tx = await cloud.sendTransaction({ to: governor.address, value: GOV_GAS });
    await tx.wait(); console.log('  gas tx', tx.hash);
  }

  // 1) deploy Safe (resumable via .safe_address)
  const setupData = safeIface.encodeFunctionData('setup', [[governor.address], 1, ethers.ZeroAddress, '0x', fbAddr, ethers.ZeroAddress, 0, ethers.ZeroAddress]);
  const safeFile = path.join(AEGIS, '.safe_address');
  let safeAddr;
  if (fs.existsSync(safeFile)) { safeAddr = fs.readFileSync(safeFile, 'utf8').trim(); console.log('Existing Safe:', safeAddr); }
  else {
    console.log('Deploying Safe...');
    const factory = new ethers.Contract(factoryAddr, factoryAbi, governor);
    const dtx = await factory.createProxyWithNonce(singletonAddr, setupData, SALT);
    const rc = await dtx.wait();
    const fIface = new ethers.Interface(factoryAbi);
    for (const log of rc.logs) { try { const pl = fIface.parseLog(log); if (pl && pl.name === 'ProxyCreation') { safeAddr = pl.args[0]; break; } } catch (e) {} }
    if (!safeAddr) throw new Error('ProxyCreation event not found');
    fs.writeFileSync(safeFile, safeAddr); console.log('  Safe deployed:', safeAddr, 'tx', dtx.hash);
  }

  const safe = new ethers.Contract(safeAddr, safeAbi, governor);
  const moduleGov = new ethers.Contract(moduleAddr, moduleAbi, governor);
  const sig = '0x' + '000000000000000000000000' + governor.address.slice(2).toLowerCase() + '0'.repeat(64) + '01';
  const exec = async (to, data) => { const tx = await safe.execTransaction(to, 0, data, 0, 0, 0, 0, ethers.ZeroAddress, ethers.ZeroAddress, sig); return (await tx.wait()); };

  // 2) enable module
  if (!(await safe.isModuleEnabled(moduleAddr))) {
    console.log('Enabling allowance module...');
    const r = await exec(safeAddr, safeIface.encodeFunctionData('enableModule', [moduleAddr])); console.log('  tx', r.hash);
  } else console.log('Module already enabled');

  // 3) delegate + allowance
  const cur = await moduleGov.getTokenAllowance(safeAddr, cloud.address, USDT);
  if (BigInt(cur[0]) === 0n) {
    console.log('Adding delegate...'); await exec(moduleAddr, mIface.encodeFunctionData('addDelegate', [cloud.address]));
    console.log('Setting allowance (cap ' + CAP_USDT + ' USDT/day)...');
    await exec(moduleAddr, mIface.encodeFunctionData('setAllowance', [cloud.address, USDT, u(CAP_USDT), RESET_MIN, 0]));
  } else console.log('Allowance already set, amount(wei)=', cur[0].toString());

  // 4) fund treasury
  const usdtCloud = new ethers.Contract(USDT, erc20Abi, cloud);
  if ((await usdtCloud.balanceOf(safeAddr)) < u(DEPOSIT_USDT)) {
    console.log('Funding Safe with ' + DEPOSIT_USDT + ' USDT...');
    const tx = await usdtCloud.transfer(safeAddr, u(DEPOSIT_USDT)); await tx.wait(); console.log('  tx', tx.hash);
  } else console.log('Safe already funded');

  // 5) PoC: delegate pulls back via allowance (proof)
  if (POC_PULL_USDT > 0n) {
    console.log('PoC: delegate pulling ' + POC_PULL_USDT + ' USDT from Safe...');
    const moduleCloud = new ethers.Contract(moduleAddr, moduleAbi, cloud);
    const tx = await moduleCloud.executeAllowanceTransfer(safeAddr, USDT, cloud.address, u(POC_PULL_USDT), ethers.ZeroAddress, 0, cloud.address, '0x');
    await tx.wait(); console.log('  PoC tx', tx.hash);
  }

  const rem = await moduleGov.getTokenAllowance(safeAddr, cloud.address, USDT);
  console.log('\n===== AEGIS SAFE READY =====');
  console.log('SAFE_ADDRESS=' + safeAddr);
  console.log('ALLOWANCE_MODULE=' + moduleAddr);
  console.log('CAP_USDT=' + CAP_USDT + '  SPENT_WEI=' + rem[1].toString());
  console.log('Explorer: https://bscscan.com/address/' + safeAddr);
}
main().catch(e => { console.error('ERROR:', e.message || e); process.exit(1); });
