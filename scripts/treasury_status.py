import os, sys, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.tools import safe_allowance

def main():
    snap = safe_allowance.get_allowance()
    print(json.dumps(snap, indent=2))
    if not snap.get("ok"):
        print("treasury snapshot failed; state.json not updated")
        return
    state_path = os.path.join(ROOT, "dashboard", "state.json")
    try:
        with open(state_path) as f:
            state = json.load(f)
    except Exception:
        state = {}
    state["treasury"] = {
        "cap_usdt": snap["cap_usdt"],
        "spent_usdt": snap["spent_usdt"],
        "remaining_usdt": snap["remaining_usdt"],
        "safe": snap["safe"],
        "module": snap["module"],
        "delegate": snap["delegate"],
        "reset_min": snap["reset_min"],
        "updated_at": int(time.time()),
    }
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
    print("state.json updated with treasury tile data")

if __name__ == "__main__":
    main()
