(function(){
function tile(t){
  var cap=+t.cap_usdt||0,sp=+t.spent_usdt||0,rem=+t.remaining_usdt||Math.max(cap-sp,0);
  var pct=cap>0?Math.min(100,Math.round(sp/cap*100)):0,sf=t.safe||"";
  var h=document.getElementById("aegisTreasury");
  if(!h){h=document.createElement("div");h.id="aegisTreasury";var a=document.getElementById("kpis");if(a&&a.parentNode)a.parentNode.insertBefore(h,a.nextSibling);else document.body.insertBefore(h,document.body.firstChild);}
  h.style.cssText="margin:14px 0;padding:16px 18px;border-radius:16px;background:linear-gradient(135deg,rgba(124,92,255,.18),rgba(34,211,238,.10));border:1px solid rgba(124,92,255,.35)";
  function col(l,v,c){return '<div><div style="font-size:11px;color:#9aa0b5">'+l+'</div><div style="font-size:20px;font-weight:700;color:'+c+'">'+v.toFixed(2)+' USDT</div></div>';}
  h.innerHTML='<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px"><div style="font-weight:700;color:#e8e6ff">\ud83d\udee1\ufe0f On-chain Treasury Guard <span style="color:#22d3ee;font-size:12px">Safe Allowance Module</span></div><a href="https://bscscan.com/address/'+sf+'" target="_blank" style="color:#22d3ee;font-size:12px;text-decoration:none">'+sf.slice(0,6)+'\u2026'+sf.slice(-4)+' \u2197</a></div><div style="display:flex;gap:24px;margin-top:12px;flex-wrap:wrap">'+col("Daily cap",cap,"#fff")+col("Spent",sp,"#fb7185")+col("Remaining",rem,"#34d399")+'</div><div style="margin-top:12px;height:8px;border-radius:6px;background:rgba(255,255,255,.08);overflow:hidden"><div style="height:100%;width:'+pct+'%;background:linear-gradient(90deg,#7c5cff,#22d3ee)"></div></div><div style="margin-top:6px;font-size:11px;color:#9aa0b5">Agent cannot exceed this on-chain limit \u00b7 resets every '+(t.reset_min||1440)+' min</div>';
}
function boot(){fetch("state.json",{cache:"no-store"}).then(function(r){return r.ok?r.json():null;}).then(function(j){if(j&&j.treasury)tile(j.treasury);}).catch(function(e){});}
if(document.readyState!=="loading")boot();else document.addEventListener("DOMContentLoaded",boot);
})();
