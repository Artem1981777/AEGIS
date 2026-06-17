(function(){
  "use strict";
  var WALLET = "0xA7a448F0093c3e5cC1930031cAe4184E5BdDB67E";
  var EXPLORER = "https://bscscan.com/address/" + WALLET;
  function short(a){ return a.slice(0,6) + "..." + a.slice(-4); }
  var css = ""
    + "#aegis-wc{position:fixed;top:14px;right:14px;z-index:9999}"
    + ".awc-pill{background:#1b1f24;color:#e6e8eb;border:1px solid #2a2f36;border-radius:10px;padding:7px 12px;display:flex;align-items:center;gap:8px;font-size:13px;text-decoration:none}"
    + ".awc-pill:hover{border-color:#F0B90B}"
    + ".awc-dot{width:8px;height:8px;border-radius:50%;background:#2ecc71}"
    + ".awc-lab{color:#7a828c;font-size:11px;text-transform:uppercase;letter-spacing:.05em}"
    + ".awc-addr{font-family:monospace;font-weight:600}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  var root = document.createElement("a");
  root.id = "aegis-wc"; root.className = "awc-pill";
  root.href = EXPLORER; root.target = "_blank"; root.rel = "noopener";
  root.title = "AEGIS competition trading wallet on BscScan";
  root.innerHTML = '<span class="awc-dot"></span><span class="awc-lab">Trading wallet</span><span class="awc-addr">' + short(WALLET) + '</span>';
  document.body.appendChild(root);
})();
