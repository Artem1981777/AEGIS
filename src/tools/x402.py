import json,subprocess
U="0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"
B="https://pro-api.coinmarketcap.com/x402/v3"
def get(path,q=""):
    url=B+path+("?"+q if q else "")
    c=["twak","x402","request",url,"--prefer-network","bsc","--prefer-asset",U]
    c+=["--prefer-method","permit2-exact","--max-payment","10000000000000000","--yes","--json"]
    o=subprocess.run(c,capture_output=True,text=True,timeout=120)
    t=o.stdout+o.stderr
    return json.loads(t[t.find("{"):])
def btc():
    return get("/cryptocurrency/quotes/latest","id=1")
