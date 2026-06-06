// dashboard/wallet.js multi-wallet EVM connect (EIP-6963 + EIP-1193)
(function () {
  "use strict";
  var CHAIN = {
    chainId: "0x61",
    chainName: "BNB Smart Chain Testnet",
    nativeCurrency: { name: "tBNB", symbol: "tBNB", decimals: 18 },
    rpcUrls: ["https://data-seed-prebsc-1-s1.binance.org:8545/"],
    blockExplorerUrls: ["https://testnet.bscscan.com"]
  };
  var SHOWCASE = [
    { name: "MetaMask", rdns: "io.metamask", domain: "metamask.io", url: "https://metamask.io/download" },
    { name: "Trust Wallet", rdns: "com.trustwallet.app", domain: "trustwallet.com", url: "https://trustwallet.com/download" },
    { name: "Coinbase Wallet", rdns: "com.coinbase.wallet", domain: "coinbase.com", url: "https://www.coinbase.com/wallet/downloads" },
    { name: "OKX Wallet", rdns: "com.okex.wallet", domain: "okx.com", url: "https://www.okx.com/web3" },
    { name: "Rabby", rdns: "io.rabby", domain: "rabby.io", url: "https://rabby.io" },
    { name: "Binance Web3", rdns: "com.binance.wallet", domain: "binance.com", url: "https://www.binance.com/en/web3wallet" },
    { name: "Rainbow", rdns: "me.rainbow", domain: "rainbow.me", url: "https://rainbow.me" }
  ];
  var providers = [];
  var current = null, account = null;
  function favicon(d) { return "https://www.google.com/s2/favicons?domain=" + d + "&sz=64"; }
  function short(a) { return a.slice(0, 6) + "..." + a.slice(-4); }
  var css = ""
    + "#aegis-wc{position:fixed;top:14px;right:14px;z-index:9999}"
    + ".awc-btn{background:#F0B90B;color:#0b0e11;border:none;border-radius:10px;padding:9px 14px;font-weight:700;cursor:pointer;font-size:13px}"
    + ".awc-pill{background:#1b1f24;color:#e6e8eb;border:1px solid #2a2f36;border-radius:10px;padding:7px 10px;display:flex;align-items:center;gap:8px;font-size:13px}"
    + ".awc-pill img{width:18px;height:18px;border-radius:5px}"
    + ".awc-dot{width:8px;height:8px;border-radius:50%;background:#2ecc71}"
    + ".awc-x{cursor:pointer;opacity:.6;margin-left:4px}"
    + ".awc-ov{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:10000;display:none;align-items:center;justify-content:center}"
    + ".awc-modal{background:#14181d;border:1px solid #2a2f36;border-radius:16px;width:340px;max-width:92vw;padding:18px;color:#e6e8eb;font-size:14px}"
    + ".awc-h{display:flex;justify-content:space-between;align-items:center}"
    + ".awc-h b{font-size:16px}"
    + ".awc-sub{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#7a828c;margin:14px 0 6px}"
    + ".awc-row{display:flex;align-items:center;gap:12px;padding:10px;border-radius:10px;cursor:pointer;border:1px solid transparent}"
    + ".awc-row:hover{background:#1b1f24;border-color:#2a2f36}"
    + ".awc-row img{width:28px;height:28px;border-radius:8px}"
    + ".awc-row .nm{font-weight:600}"
    + ".awc-row .tag{margin-left:auto;font-size:11px;color:#7a828c}"
    + ".awc-row .tag.on{color:#2ecc71}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  var root = document.createElement("div"); root.id = "aegis-wc"; document.body.appendChild(root);
  var ov = document.createElement("div"); ov.className = "awc-ov"; document.body.appendChild(ov);
  ov.addEventListener("click", function (e) { if (e.target === ov) closeModal(); });
  function openModal() { ov.style.display = "flex"; renderModal(); }
  function closeModal() { ov.style.display = "none"; }
  function sub(txt) { var s = document.createElement("div"); s.className = "awc-sub"; s.textContent = txt; return s; }
  function rowFor(name, icon, tag, onClick, on) {
    var r = document.createElement("div"); r.className = "awc-row";
    var im = document.createElement("img"); im.src = icon; im.onerror = function () { im.style.visibility = "hidden"; };
    var nm = document.createElement("span"); nm.className = "nm"; nm.textContent = name;
    var tg = document.createElement("span"); tg.className = "tag" + (on ? " on" : ""); tg.textContent = tag;
    r.appendChild(im); r.appendChild(nm); r.appendChild(tg);
    r.addEventListener("click", onClick); return r;
  }
  function renderButton() {
    root.innerHTML = "";
    if (account) {
      var pill = document.createElement("div"); pill.className = "awc-pill";
      var dot = document.createElement("span"); dot.className = "awc-dot"; pill.appendChild(dot);
      if (current && current.info && current.info.icon) { var im = document.createElement("img"); im.src = current.info.icon; pill.appendChild(im); }
      var ad = document.createElement("span"); ad.textContent = short(account); pill.appendChild(ad);
      var x = document.createElement("span"); x.className = "awc-x"; x.textContent = "x"; x.addEventListener("click", disconnect); pill.appendChild(x);
      root.appendChild(pill);
    } else {
      var b = document.createElement("button"); b.className = "awc-btn"; b.textContent = "Connect Wallet"; b.addEventListener("click", openModal); root.appendChild(b);
    }
  }
  function renderModal() {
    ov.innerHTML = "";
    var modal = document.createElement("div"); modal.className = "awc-modal";
    var h = document.createElement("div"); h.className = "awc-h";
    var t = document.createElement("b"); t.textContent = "Connect a wallet"; h.appendChild(t);
    var cx = document.createElement("span"); cx.className = "awc-x"; cx.textContent = "x"; cx.addEventListener("click", closeModal); h.appendChild(cx);
    modal.appendChild(h);
    var seen = {};
    if (providers.length) {
      modal.appendChild(sub("Detected"));
      providers.forEach(function (p) { seen[p.info.rdns] = true; modal.appendChild(rowFor(p.info.name, p.info.icon, "Connect", function () { connect(p); }, true)); });
    }
    modal.appendChild(sub("Popular EVM wallets"));
    SHOWCASE.forEach(function (w) { if (seen[w.rdns]) return; modal.appendChild(rowFor(w.name, favicon(w.domain), "Install", function () { window.open(w.url, "_blank"); }, false)); });
    ov.appendChild(modal);
  }
  async function ensureChain(prov) {
    try { await prov.request({ method: "wallet_switchEthereumChain", params: [{ chainId: CHAIN.chainId }] }); }
    catch (e) { try { await prov.request({ method: "wallet_addEthereumChain", params: [CHAIN] }); } catch (e2) {} }
  }
  async function connect(detail) {
    var prov = detail.provider;
    try {
      var accs = await prov.request({ method: "eth_requestAccounts" });
      account = accs && accs[0]; current = detail;
      await ensureChain(prov);
      if (prov.on) { prov.on("accountsChanged", function (a) { account = a && a[0]; if (account) renderButton(); else disconnect(); }); }
      closeModal(); renderButton();
    } catch (e) { alert("Connect failed: " + (e && e.message ? e.message : e)); }
  }
  function disconnect() { account = null; current = null; renderButton(); }
  window.addEventListener("eip6963:announceProvider", function (e) {
    var d = e.detail;
    if (!providers.some(function (p) { return p.info.uuid === d.info.uuid; })) { providers.push(d); if (ov.style.display === "flex") renderModal(); }
  });
  window.dispatchEvent(new Event("eip6963:requestProvider"));
  renderButton();
})();
