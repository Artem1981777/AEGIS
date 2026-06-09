const DEMO={
equity:10250,pnlValue:250,pnlPct:2.5,drawdown:4.2,winRate:61,sharpe:1.8,tradesToday:3,regime:"TREND",
decision:{token:"CAKE",side:"BUY",size:8,confidence:72,verdict:"APPROVE",reason:"Within risk limits"},
equitySeries:[9000,9050,8980,9120,9210,9180,9300,9420,9380,9510,9600,9555,9680,9720,9810,9790,9900,9980,10040,10010,10120,10180,10240,10250],
btSeries:[10000,10120,9980,10250,10400,10330,10560,10720,10680,10910,11050,11240,11180,11420,11600,11550,11820,12010,12180,12260,12440,12610,12780,13800],
allocation:[{token:"USDT",pct:40},{token:"BNB",pct:32},{token:"CAKE",pct:18},{token:"ETH",pct:10}],
risk:{drawdownUsed:17,exposure:55,dailyTradesUsed:15},
positions:[{token:"BNB",side:"BUY",size:14,entry:"612.40",mark:"628.10",pnl:2.6},{token:"CAKE",side:"BUY",size:8,entry:"2.41",mark:"2.50",pnl:3.7},{token:"ETH",side:"SELL",size:6,entry:"3180",mark:"3155",pnl:0.8}],
trades:[{time:"14:02",token:"CAKE",side:"BUY",size:8,price:"2.41"},{time:"13:40",token:"BNB",side:"BUY",size:6,price:"612.40"},{time:"12:55",token:"ETH",side:"SELL",size:6,price:"3180"}],
signals:[{name:"Fear & Greed",value:"62 (Greed)"},{name:"Trend strength",value:"+0.58"},{name:"Volatility (ann)",value:"47%"},{name:"Funding rate",value:"+0.012%"}],
reasoning:["Regime classified as TREND (F&G 62, trend +0.58).","Momentum on CAKE confirmed across 1h / 4h.","Sentinel: size within per-trade and drawdown limits.","Proposed BUY 8% -> APPROVE."],
backtest:{ret:38,maxDd:12,sharpe:2.1,trades:142,winRate:58},
infra:[{name:"TWAK CLI",ok:true},{name:"CoinMarketCap Hub",ok:true},{name:"LLM Claude",ok:true},{name:"BSC RPC",ok:true},{name:"x402 Metering",ok:true},{name:"Vector Memory",ok:true}],
events:[{time:"14:02",msg:"Trade executed BUY CAKE 8%"},{time:"14:00",msg:"Sentinel APPROVE within limits"},{time:"13:30",msg:"Regime to TREND"},{time:"12:10",msg:"Heartbeat all systems OK"}]
};
const $=id=>document.getElementById(id);
const fmt=n=>Number(n).toLocaleString("en-US");
function spark(arr){const w=600,h=130,p=8,mn=Math.min(...arr),mx=Math.max(...arr);const pts=arr.map((v,i)=>[p+i*(w-2*p)/(arr.length-1),h-p-(v-mn)/((mx-mn)||1)*(h-2*p)]);const line=pts.map((q,i)=>(i?"L":"M")+q[0].toFixed(1)+" "+q[1].toFixed(1)).join(" ");const area=line+" L "+(w-p)+" "+h+" L "+p+" "+h+" Z";return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><path class="area" d="${area}"/><path class="line" d="${line}"/></svg>`;}
function gauge(lab,val,color){const r=40,c=2*Math.PI*r,off=c*(1-Math.min(val,100)/100);return `<div class="gauge"><svg viewBox="0 0 96 96"><circle class="track" cx="48" cy="48" r="${r}" fill="none" stroke-width="9"/><circle class="val" cx="48" cy="48" r="${r}" fill="none" stroke="${color}" stroke-width="9" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}"/></svg><div class="num">${val}%</div><div class="lab">${lab}</div></div>`;}
function kpiCard(k){return `<div class="card kpi"><div class="k">${k[0]}</div><div class="v ${k[2]||""}">${k[1]}</div></div>`;}
function render(s){
$("tk-equity").textContent=fmt(s.equity);
const pn=$("tk-pnl");pn.textContent=(s.pnlValue>=0?"+":"")+fmt(s.pnlValue);pn.className=s.pnlValue>=0?"pos":"neg";
$("kpis").innerHTML=[["Equity",fmt(s.equity),""],["PnL Today",(s.pnlPct>=0?"+":"")+s.pnlPct+"%",s.pnlPct>=0?"pos":"neg"],["Drawdown",s.drawdown+"%",""],["Win Rate",s.winRate+"%",""],["Sharpe",s.sharpe,""],["Trades",s.tradesToday,""]].map(kpiCard).join("");
$("dToken").textContent=s.decision.token;
const sd=$("dSide");sd.textContent=s.decision.side;sd.className=s.decision.side==="BUY"?"buy":"sell";
$("dSize").textContent=s.decision.size+" %";$("dConf").textContent=s.decision.confidence+" %";
const v=$("dVerdict");v.textContent=s.decision.verdict;v.className="pill "+({APPROVE:"approve",RESIZE:"resize",VETO:"veto",KILL:"veto"}[s.decision.verdict]||"approve");
$("dReason").textContent=s.decision.reason;
$("spark").innerHTML=spark(s.equitySeries);
$("alloc").innerHTML=s.allocation.map(a=>`<div><div class="lab"><span>${a.token}</span><span class="k">${a.pct}%</span></div><div class="bar"><i style="width:${a.pct}%"></i></div></div>`).join("");
const g=[gauge("DD used",s.risk.drawdownUsed,"#fb7185"),gauge("Exposure",s.risk.exposure,"#7c5cff"),gauge("Daily trades",s.risk.dailyTradesUsed,"#22d3ee")].join("");
$("gauges").innerHTML=g;if($("gauges2"))$("gauges2").innerHTML=g;
$("positionsBody").innerHTML=s.positions.map(p=>`<tr><td><b>${p.token}</b></td><td class="${p.side==="BUY"?"buy":"sell"}">${p.side}</td><td>${p.size}%</td><td class="mono">${p.entry}</td><td class="mono">${p.mark}</td><td class="mono ${p.pnl>=0?"pos":"neg"}">${p.pnl>=0?"+":""}${p.pnl}%</td></tr>`).join("");
$("trades").innerHTML=s.trades.map(t=>`<div class="it"><span class="t">${t.time}</span><span><b>${t.token}</b> <span class="${t.side==="BUY"?"buy":"sell"}">${t.side}</span> ${t.size}% @ ${t.price}</span></div>`).join("");
$("signals").innerHTML=s.signals.map(x=>`<div class="row"><span class="k">${x.name}</span><span class="mono">${x.value}</span></div>`).join("");
$("reasoning").innerHTML=s.reasoning.map(r=>`<div>- ${r}</div>`).join("");
$("regimeVal").textContent=s.regime;
const b=s.backtest;
$("btMetrics").innerHTML=[["Total Return","+"+b.ret+"%","pos"],["Max DD",b.maxDd+"%","neg"],["Sharpe",b.sharpe,""],["Trades",b.trades,""],["Win Rate",b.winRate+"%",""]].map(kpiCard).join("");
$("btSpark").innerHTML=spark(s.btSeries||s.equitySeries);
$("infra").innerHTML=s.infra.map(i=>`<div class="it"><span class="sdot ${i.ok?"ok":"down"}"></span>${i.name}</div>`).join("");
$("events").innerHTML=s.events.map(e=>`<div class="it"><span class="t">${e.time}</span><span>${e.msg}</span></div>`).join("");
}
$("nav").addEventListener("click",e=>{const b=e.target.closest(".nav-item");if(!b)return;document.querySelectorAll(".nav-item").forEach(n=>n.classList.remove("active"));b.classList.add("active");document.querySelectorAll(".tab").forEach(t=>t.classList.add("hidden"));$("tab-"+b.dataset.tab).classList.remove("hidden");$("pageTitle").textContent=b.dataset.title;window.scrollTo({top:0,behavior:"smooth"});});
function initTilt(){if(window.matchMedia("(hover:none)").matches)return;document.querySelectorAll(".tilt").forEach(c=>{c.addEventListener("pointermove",e=>{const r=c.getBoundingClientRect();const px=(e.clientX-r.left)/r.width-.5,py=(e.clientY-r.top)/r.height-.5;c.style.transform="perspective(900px) rotateY("+(px*8).toFixed(2)+"deg) rotateX("+(-py*8).toFixed(2)+"deg)";});c.addEventListener("pointerleave",()=>{c.style.transform="";});});}
async function boot(){let s=JSON.parse(JSON.stringify(DEMO));try{const r=await fetch("state.json",{cache:"no-store"});if(r.ok)s=Object.assign(s,await r.json());}catch(e){}render(s);initTilt();}
boot();

/* sentinelDemoRenderer */
(function(){
  var cls={APPROVE:"approve",RESIZE:"resize",VETO:"veto",KILL:"kill"};
  fetch("sentinel_demo.json",{cache:"no-store"}).then(function(r){return r.ok?r.json():null;}).then(function(j){
    if(!j)return;
    var meta=document.getElementById("sdMeta");
    if(meta&&j.config){var c=j.config;meta.textContent="max_dd "+c.max_drawdown_pct+"pct   per-trade "+c.per_trade_max_pct+"pct   slippage "+c.max_slippage_bps+"bps   daily "+c.daily_trade_limit;}
    var tb=document.getElementById("sentinelDemo");
    if(!tb)return;
    tb.textContent="";
    (j.results||[]).forEach(function(x){
      var tr=document.createElement("tr");
      function cell(t,mono){var td=document.createElement("td");if(mono){td.className="mono";}td.textContent=t;tr.appendChild(td);}
      cell(x.scenario,false);
      cell(x.token,false);
      cell(x.requested_size_pct+"pct",true);
      var vtd=document.createElement("td");
      var sp=document.createElement("span");
      sp.className="pill "+(cls[String(x.verdict)]||"");
      sp.textContent=x.verdict;
      vtd.appendChild(sp);
      tr.appendChild(vtd);
      cell(x.approved_size_pct+"pct",true);
      cell(x.reason,false);
      tb.appendChild(tr);
    });
  }).catch(function(e){});
})();
