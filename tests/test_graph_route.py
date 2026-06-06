from src.graph.langgraph_app import route


def test_route_halts_on_veto():
    assert route({"decision": {"verdict": "VETO", "final_size_pct": 0}}) == "halt"


def test_route_halts_on_zero_size():
    assert route({"decision": {"verdict": "APPROVE", "final_size_pct": 0}}) == "halt"


def test_route_executes_on_approve():
    assert route({"decision": {"verdict": "APPROVE", "final_size_pct": 5.0}}) == "execute"


def test_route_halts_on_kill():
    assert route({"decision": {"verdict": "KILL", "final_size_pct": 10}}) == "halt"


def test_backtest_smoke():
    from src.backtest.backtest import run_backtest
    res = run_backtest()
    assert res is not None
