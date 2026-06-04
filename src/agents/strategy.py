from src.risk.sentinel import TradeProposal


def propose_trade(regime, token, vol, slippage_bps=30, base_size_pct=10.0):
    """Rule-based strategy stub (to be replaced by the LLM agent).

    Maps a regime to a trade proposal. Returns a TradeProposal.
    """
    if regime == "risk_off":
        return TradeProposal(token=token, side="sell", size_pct=base_size_pct, est_slippage_bps=slippage_bps, token_vol_annual=vol)
    if regime == "trend":
        return TradeProposal(token=token, side="buy", size_pct=base_size_pct, est_slippage_bps=slippage_bps, token_vol_annual=vol)
    return TradeProposal(token=token, side="buy", size_pct=base_size_pct / 2, est_slippage_bps=slippage_bps, token_vol_annual=vol)
