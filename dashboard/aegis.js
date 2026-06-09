(function () {
  var IMG = "aegis.jpg";
  var css = [
    ".aegis-wrap{position:fixed;right:16px;bottom:16px;z-index:99999;width:300px;font-family:inherit}",
    ".aegis-card{position:relative;background:linear-gradient(180deg,rgba(10,14,24,.92),rgba(6,9,16,.97));border:1px solid var(--ag,#00e5ff);border-radius:16px;padding:12px;box-shadow:0 0 40px rgba(0,0,0,.6);transition:border-color .6s,box-shadow .6s}",
    ".aegis-fig{position:relative;width:100%;height:250px;overflow:hidden;border-radius:12px;background:radial-gradient(circle at 50% 34%,rgba(0,229,255,.12),transparent 62%)}",
    ".aegis-img{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);height:104%;filter:drop-shadow(0 0 16px var(--ag,#00e5ff));transition:filter .6s;-webkit-mask-image:radial-gradient(ellipse 72% 82% at 50% 42%,#000 58%,transparent 82%);mask-image:radial-gradient(ellipse 72% 82% at 50% 42%,#000 58%,transparent 82%)}",
    ".aegis-scan{position:absolute;left:0;right:0;height:42%;background:linear-gradient(180deg,transparent,rgba(0,229,255,.12),transparent);animation:agScan 3.6s linear infinite;pointer-events:none}",
    "@keyframes agScan{0%{top:-42%}100%{top:100%}}",
    ".aegis-ring{position:absolute;left:50%;top:16%;width:56px;height:56px;transform:translate(-50%,-50%);border-radius:50%;border:2px solid var(--ag,#00e5ff);animation:agPulse 2.6s ease-out infinite;pointer-events:none}",
    "@keyframes agPulse{0%{opacity:.7;transform:translate(-50%,-50%) scale(.5)}100%{opacity:0;transform:translate(-50%,-50%) scale(2.3)}}",
    ".aegis-hd{display:flex;align-items:center;gap:8px;margin:10px 2px 2px;font-weight:700;letter-spacing:.14em;font-size:13px;color:#dff4ff}",
    ".aegis-dot{width:9px;height:9px;border-radius:50%;background:var(--ag,#00e5ff);box-shadow:0 0 12px var(--ag,#00e5ff);animation:agBlink 1.6s ease-in-out infinite}",
    "@keyframes agBlink{0%,100%{opacity:1}50%{opacity:.3}}",
    ".aegis-say{min-height:56px;font-size:12.5px;line-height:1.5;color:#e3eefb;background:rgba(0,229,255,.06);border-left:2px solid var(--ag,#00e5ff);padding:8px 10px;border-radius:8px;margin-top:6px}",
    ".aegis-bar{display:flex;gap:8px;margin-top:8px}",
    ".aegis-b{flex:1;cursor:pointer;border:1px solid rgba(0,229,255,.4);background:transparent;color:#bfe9ff;border-radius:8px;padding:7px 4px;font-size:12px;transition:background .2s}",
    ".aegis-b:hover{background:rgba(0,229,255,.12)}"
  ].join("");
  var s = document.createElement("style");
  s.textContent = css;
  document.head.appendChild(s);

  var wrap = document.createElement("div");
  wrap.className = "aegis-wrap";
  wrap.innerHTML =
    '<div class="aegis-card">' +
    '<div class="aegis-fig"><span class="aegis-ring"></span><img class="aegis-img" src="' + IMG + '" alt="AEGIS"><span class="aegis-scan"></span></div>' +
    '<div class="aegis-hd"><span class="aegis-dot"></span>AEGIS SENTINEL</div>' +
    '<div class="aegis-say" id="agSay">Initializing systems...</div>' +
    '<div class="aegis-bar"><button class="aegis-b" id="agVoice">\ud83d\udd0a Voice: off</button><button class="aegis-b" id="agRef">\u21bb Refresh</button></div>' +
    '</div>';
  document.body.appendChild(wrap);

  function glow(c) { wrap.style.setProperty("--ag", c); }

  var voiceOn = false, last = "";
  var bv = document.getElementById("agVoice");
  bv.onclick = function () {
    voiceOn = !voiceOn;
    bv.textContent = (voiceOn ? "\ud83d\udd0a Voice: on" : "\ud83d\udd0a Voice: off");
    if (voiceOn) say(last);
  };
  function say(t) {
    if (!voiceOn || !t || !window.speechSynthesis) return;
    try {
      speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(t);
      u.lang = "en-US"; u.rate = 1; u.pitch = 0.85;
      speechSynthesis.speak(u);
    } catch (e) {}
  }

  var tm = null;
  function type(t) {
    var el = document.getElementById("agSay");
    if (!el) return;
    clearInterval(tm);
    el.textContent = "";
    var i = 0;
    tm = setInterval(function () {
      el.textContent = t.slice(0, ++i);
      if (i >= t.length) clearInterval(tm);
    }, 16);
  }

  function sig(a, n) {
    if (!a) return null;
    for (var i = 0; i < a.length; i++) {
      if (a[i] && a[i].name === n) return a[i].value;
    }
    return null;
  }

  function narrate(st) {
    var d = st.decision || {};
    var verdict = (d.verdict || "").toString();
    var alert = /VETO|KILL/i.test(verdict) || (st.drawdown != null && Number(st.drawdown) >= 25);
    glow(alert ? "#ff5b2e" : "#00e5ff");
    var fg = sig(st.signals, "Fear & Greed");
    var vol = sig(st.signals, "Volatility (ann)");
    var p = [];
    p.push("AEGIS is on guard.");
    if (st.regime) p.push("Market regime: " + st.regime + ".");
    if (fg != null) p.push("Fear and Greed index " + fg + ".");
    if (vol != null) p.push("Volatility " + vol + ".");
    if (d.side && d.token) p.push("Signal: " + d.side + " " + d.token + (d.confidence != null ? (", confidence " + d.confidence + " percent") : "") + ".");
    if (verdict) p.push("Sentinel verdict: " + verdict + (d.reason ? (". Reason: " + d.reason) : "") + ".");
    if (st.pnlPct != null) p.push("Return " + (st.pnlPct >= 0 ? "plus " : "minus ") + Math.abs(st.pnlPct) + " percent.");
    if (st.x402BtcUsd != null) p.push("Bitcoin price via x402: " + Math.round(st.x402BtcUsd) + " dollars.");
    var t = p.join(" ");
    last = t;
    type(t);
    say(t);
  }

  function load() {
    fetch("state.json?ts=" + Date.now())
      .then(function (r) { return r.json(); })
      .then(narrate)
      .catch(function () { type("AEGIS is on guard. Awaiting trading cycle data."); });
  }

  document.getElementById("agRef").onclick = load;
  load();
  setInterval(load, 20000);
})();
