(function () {
  var IMG = "aegis.jpg";
  var css = [
    "#aegisBg{position:fixed;inset:0;z-index:-2;overflow:hidden;pointer-events:none}",
    "#aegisBg .agb-img{position:absolute;inset:-8%;background:url('" + IMG + "') center 20%/cover no-repeat;opacity:.24;filter:saturate(1.2) contrast(1.05) drop-shadow(0 0 40px rgba(34,211,238,.4));animation:agbZoom 38s ease-in-out infinite;will-change:transform;transition:filter .8s}",
    "#aegisBg .agb-veil{position:absolute;inset:0;background:radial-gradient(70vw 60vh at 50% 30%,rgba(34,211,238,.10),transparent 60%),linear-gradient(180deg,rgba(7,10,18,.55) 0%,rgba(7,10,18,.78) 55%,rgba(7,10,18,.92) 100%)}",
    "#aegisBg .agb-scan{position:absolute;left:0;right:0;height:42%;background:linear-gradient(180deg,transparent,rgba(34,211,238,.06),transparent);animation:agbScan 8s linear infinite}",
    "#aegisBg .agb-glow{position:absolute;left:50%;top:26%;width:64vmin;height:64vmin;transform:translate(-50%,-50%);border-radius:50%;background:radial-gradient(circle,rgba(34,211,238,.14),transparent 66%);animation:agbPulse 5s ease-in-out infinite;transition:background .8s}",
    "@keyframes agbZoom{0%{transform:scale(1.06) translate(0,0)}50%{transform:scale(1.16) translate(-1.5%,-2%)}100%{transform:scale(1.06) translate(0,0)}}",
    "@keyframes agbScan{0%{top:-42%}100%{top:100%}}",
    "@keyframes agbPulse{0%,100%{opacity:.4}50%{opacity:.9}}",
    "@media (prefers-reduced-motion:reduce){#aegisBg .agb-img,#aegisBg .agb-scan,#aegisBg .agb-glow{animation:none}}"
  ].join("");
  var s = document.createElement("style");
  s.textContent = css;
  document.head.appendChild(s);

  var bg = document.createElement("div");
  bg.id = "aegisBg";
  bg.innerHTML =
    '<div class="agb-img"></div>' +
    '<div class="agb-scan"></div>' +
    '<div class="agb-glow"></div>' +
    '<div class="agb-veil"></div>';
  document.body.insertBefore(bg, document.body.firstChild);

  var glow = bg.querySelector(".agb-glow");
  var img = bg.querySelector(".agb-img");

  function apply(st) {
    var v = ((st.decision || {}).verdict || "").toString();
    var alert = /VETO|KILL/i.test(v) || (st.drawdown != null && Number(st.drawdown) >= 25);
    if (alert) {
      glow.style.background = "radial-gradient(circle,rgba(255,91,46,.20),transparent 66%)";
      img.style.filter = "saturate(1.3) contrast(1.08) drop-shadow(0 0 52px rgba(255,91,46,.55))";
    } else {
      glow.style.background = "radial-gradient(circle,rgba(34,211,238,.14),transparent 66%)";
      img.style.filter = "saturate(1.2) contrast(1.05) drop-shadow(0 0 40px rgba(34,211,238,.4))";
    }
  }

  function load() {
    fetch("state.json?ts=" + Date.now())
      .then(function (r) { return r.json(); })
      .then(apply)
      .catch(function () {});
  }
  load();
  setInterval(load, 20000);
})();
