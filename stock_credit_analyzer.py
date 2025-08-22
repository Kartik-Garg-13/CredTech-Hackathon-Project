# stock_credit_rating_analyzer.py (API Version)
# ------------------------------------------------------------
# This script has been converted into a FastAPI backend.
# It exposes an API endpoint to calculate credit scores for stocks.
# ------------------------------------------------------------

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple

import pandas as pd
import yfinance as yf
import feedparser
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- This creates the FastAPI web server instance ---
app = FastAPI()

# --- Add CORS Middleware ---
# This is crucial. It allows your React frontend (running on a different address)
# to make requests to this backend without being blocked by the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Config ----------------
# (Your NSE_COMPANIES dictionary and other configs remain here)
NSE_COMPANIES: Dict[str, str] = {
    "RELIANCE": "Reliance Industries Ltd",
    "TCS": "Tata Consultancy Services Ltd",
    "HDFCBANK": "HDFC Bank Ltd",
    # ... (the rest of your extensive list)
    "RADICO": "Radico Khaitan Ltd"
}
LARGE_CAP_CRORE = 100_000
MID_CAP_CRORE_LOW = 10_000

# ---------------- All Helper, Data Fetch, and Scoring Functions ----------------
# (All your functions like safe_ratio, pick_first, compute_features, 
# news_event_signal_for_company, score_yoy_growth, rating_grade, etc., remain here, unchanged)

def safe_ratio(n: Optional[float], d: Optional[float]) -> Optional[float]:
    if n is None or d is None: return None
    try:
        d = float(d)
        if d == 0.0: return None
        return float(n) / d
    except Exception:
        return None

def pick_first(df: pd.DataFrame, keys: List[str]) -> Optional[str]:
    if df is None or df.empty: return None
    lower_map = {str(idx).strip().lower(): idx for idx in df.index}
    for k in keys:
        key = k.strip().lower()
        if key in lower_map: return lower_map[key]
    return None

def clamp_event_score(x: Optional[float]) -> int:
    if x is None: return 0
    try: xi = int(round(float(x)))
    except Exception: return 0
    return max(-5, min(3, xi))

def format_ticker(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if symbol.endswith('.NS'): return symbol
    return f"{symbol}.NS"

def validate_nse_symbol(symbol: str) -> Tuple[bool, str]:
    symbol = symbol.strip().upper().replace('.NS', '')
    if symbol in NSE_COMPANIES: return True, NSE_COMPANIES[symbol]
    for nse_symbol, company_name in NSE_COMPANIES.items():
        if symbol in nse_symbol or nse_symbol in symbol: return True, company_name
    return True, symbol

POSITIVE_KEYWORDS = ["profit", "growth", "expansion", "order win", "funding", "merger", "record high", "revenue up", "earnings beat", "strong performance", "dividend", "acquisition"]
NEGATIVE_KEYWORDS = ["fraud", "default", "loss", "scam", "investigation", "penalty", "layoff", "lawsuit", "decline", "fall", "crash", "warning", "debt", "trouble", "crisis"]

def news_event_signal_for_company(company_name: str, top_n: int = 5) -> int:
    try:
        query = company_name.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        headlines = [entry.title for entry in feed.entries[:top_n]]
        score = 0
        for h in headlines:
            text = (h or "").lower()
            for w in POSITIVE_KEYWORDS:
                if w in text: score += 1
            for w in NEGATIVE_KEYWORDS:
                if w in text: score -= 1
        return clamp_event_score(score)
    except Exception as e:
        print(f"Warning: Could not fetch news for {company_name}: {e}")
        return 0

def get_market_cap_and_tier(yf_ticker: str) -> Tuple[Optional[float], str]:
    try:
        info = yf.Ticker(yf_ticker).info or {}
        mc = info.get("marketCap")
        if mc is None: return (None, "Mid")
        mc_crore = float(mc) / 1e7
        if mc_crore >= LARGE_CAP_CRORE: tier = "Large"
        elif mc_crore >= MID_CAP_CRORE_LOW: tier = "Mid"
        else: tier = "Small"
        return (mc_crore, tier)
    except Exception as e:
        print(f"Warning: Could not fetch market cap for {yf_ticker}: {e}")
        return (None, "Mid")

def compute_features(yf_ticker: str) -> Dict[str, Optional[float]]:
    try:
        t = yf.Ticker(yf_ticker)
        fin = t.financials if hasattr(t, "financials") else pd.DataFrame()
        cf = t.cashflow if hasattr(t, "cashflow") else pd.DataFrame()
        bs = t.balance_sheet if hasattr(t, "balance_sheet") else pd.DataFrame()
        rev_key = pick_first(fin, ["Total Revenue", "TotalRevenue", "Revenue"])
        ni_key = pick_first(fin, ["Net Income", "NetIncome", "Net income applicable to common shares"])
        revenue_now = fin.loc[rev_key].iloc[0] if rev_key is not None else None
        revenue_prev = fin.loc[rev_key].iloc[1] if (rev_key is not None and fin.shape[1] > 1) else None
        net_profit_now = fin.loc[ni_key].iloc[0] if ni_key is not None else None
        cfo_key = pick_first(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"])
        cfi_key = pick_first(cf, ["Investing Cash Flow", "Total Cashflows From Investing Activities"])
        cfo_now = cf.loc[cfo_key].iloc[0] if cfo_key is not None else None
        cfi_now = cf.loc[cfi_key].iloc[0] if cfi_key is not None else None
        debt_key = pick_first(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation", "Long-term debt"])
        debt_now = bs.loc[debt_key].iloc[0] if debt_key is not None else None
        debt_prev = bs.loc[debt_key].iloc[1] if (debt_key is not None and bs.shape[1] > 1) else None
        yoy_growth = None
        if revenue_now is not None and revenue_prev not in (None, 0): yoy_growth = ((float(revenue_now) - float(revenue_prev)) / abs(float(revenue_prev))) * 100.0
        pat_margin = None
        if revenue_now not in (None, 0) and net_profit_now is not None: pat_margin = (float(net_profit_now) / float(revenue_now)) * 100.0
        cfo_pat_ratio = safe_ratio(cfo_now, net_profit_now)
        cfi_rev_ratio = safe_ratio(cfi_now, revenue_now)
        borrowing_growth = None
        if debt_now is not None and debt_prev not in (None, 0): borrowing_growth = ((float(debt_now) - float(debt_prev)) / abs(float(debt_prev))) * 100.0
        end_date = datetime.now()
        start_date = end_date - timedelta(days=35)
        hist = t.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        stock_return = None
        if not hist.empty and len(hist["Close"]) > 1: stock_return = ((float(hist["Close"].iloc[-1]) - float(hist["Close"].iloc[0])) / float(hist["Close"].iloc[0])) * 100.0
        return {"YoY_Growth": round(yoy_growth, 2) if yoy_growth is not None else None, "PAT_Margin": round(pat_margin, 2) if pat_margin is not None else None, "CFO_PAT_Ratio": round(cfo_pat_ratio, 2) if cfo_pat_ratio is not None else None, "CFI_Revenue": round(cfi_rev_ratio, 4) if cfi_rev_ratio is not None else None, "Borrowing_Growth_%": round(borrowing_growth, 2) if borrowing_growth is not None else None, "Stock_Return_30D": round(stock_return, 2) if stock_return is not None else None}
    except Exception as e:
        print(f"Warning: Could not compute features for {yf_ticker}: {e}")
        return {"YoY_Growth": None, "PAT_Margin": None, "CFO_PAT_Ratio": None, "CFI_Revenue": None, "Borrowing_Growth_%": None, "Stock_Return_30D": None}

def score_yoy_growth(y: Optional[float], tier: str) -> Tuple[int, str]:
    if y is None: return 0, "NA"
    if tier in ("Large", "Mid"):
        if y > 2: return 2, ">2%"
        if 0 <= y <= 2: return 0, "0–2%"
        return -1, "<0%"
    if y > 5: return 2, ">5%"
    if 2 <= y <= 5: return 0, "2–5%"
    return -1, "<2%"

def score_pat_margin(p: Optional[float], tier: str) -> Tuple[int, str]:
    if p is None: return 0, "NA"
    if tier in ("Large", "Mid"):
        if p > 8: return 2, ">8%"
        if 2.5 <= p <= 8: return 1, "2.5–8%"
        return -2, "<2.5%"
    if p > 9: return 2, ">9%"
    if 2.5 <= p <= 9: return 1, "2.5–9%"
    return -2, "<2.5%"

def score_cfo_pat(r: Optional[float]) -> Tuple[int, str]:
    if r is None: return 0, "NA"
    if r > 1.0: return 2, ">1.0x"
    if 0.7 <= r <= 1.0: return 1, "0.7–1.0x"
    return -1, "<0.7x"

def score_cfi_rev(r: Optional[float], tier: str) -> Tuple[int, str]:
    if r is None: return 0, "NA"
    r_pct = r * 100
    if tier in ("Large", "Mid"):
        if r_pct > -10: return 2, ">-10%"
        if -20 <= r_pct <= -10: return 1, "-20% to -10%"
        return -1, "<-20%"
    if r_pct > -10: return 2, ">-10%"
    if -15 <= r_pct <= -10: return 1, "-15% to -10%"
    return -1, "<-15%"

def score_borrowing_growth(b: Optional[float], tier: str) -> Tuple[int, str]:
    if b is None: return 0, "NA"
    if tier in ("Large", "Mid"):
        if b < 10: return 2, "<10%"
        if 10 <= b <= 25: return 1, "10–25%"
        return -2, ">25%"
    if b < 8: return 2, "<8%"
    if 8 <= b <= 25: return 1, "8–25%"
    return -2, ">25%"

def score_stock_return(sr: Optional[float]) -> Tuple[int, str]:
    if sr is None: return 0, "NA"
    if sr > 0: return 1, ">0%"
    if -5 <= sr <= 0: return 0, "-5%–0%"
    return -1, "<-5%"

def rating_grade(total_score: int, tier: str) -> str:
    if tier in ("Large", "Mid"):
        if total_score >= 11: return "AAA"
        if total_score >= 9: return "AA"
        if total_score >= 7: return "A"
        if total_score >= 5: return "BBB"
        if total_score >= 3: return "BB"
        if total_score >= 1: return "B"
        if total_score >= -1: return "C"
        return "D"
    if total_score >= 12: return "AAA"
    if total_score >= 10: return "AA"
    if total_score >= 8: return "A"
    if total_score >= 6: return "BBB"
    if total_score >= 4: return "BB"
    if total_score >= 2: return "B"
    if total_score >= 0: return "C"
    return "D"

def analyze_single_stock(symbol: str, company_name: str = None) -> Dict:
    yf_ticker = format_ticker(symbol)
    clean_symbol = symbol.upper().replace('.NS', '')
    print(f"Fetching metrics for {clean_symbol} ({yf_ticker}) ...")
    if company_name is None: _, company_name = validate_nse_symbol(clean_symbol)
    feats = compute_features(yf_ticker)
    mc_crore, tier = get_market_cap_and_tier(yf_ticker)
    evt_s = news_event_signal_for_company(company_name, top_n=5)
    yoy_s, yoy_lbl = score_yoy_growth(feats["YoY_Growth"], tier)
    pat_s, pat_lbl = score_pat_margin(feats["PAT_Margin"], tier)
    cfo_s, cfo_lbl = score_cfo_pat(feats["CFO_PAT_Ratio"])
    cfi_s, cfi_lbl = score_cfi_rev(feats["CFI_Revenue"], tier)
    bor_s, bor_lbl = score_borrowing_growth(feats["Borrowing_Growth_%"], tier)
    stk_s, stk_lbl = score_stock_return(feats["Stock_Return_30D"])
    total = yoy_s + pat_s + cfo_s + cfi_s + bor_s + stk_s + evt_s
    grade = rating_grade(int(total), tier)
    return {"Symbol": clean_symbol, "CompanyName_ForNews": company_name, "Yahoo_Ticker": yf_ticker, "MarketCap_Crore": round(mc_crore, 2) if mc_crore is not None else None, "Tier": tier, **feats, "Event_Score": evt_s, "Score_YoY_Growth": yoy_s, "Score_PAT_Margin": pat_s, "Score_CFO_PAT": cfo_s, "Score_CFI_Revenue": cfi_s, "Score_Borrowing_Growth": bor_s, "Score_Stock_Return_30D": stk_s, "Total_Score": int(total), "Rating": grade, "YoY_Bucket": yoy_lbl, "PAT_Bucket": pat_lbl, "CFO_PAT_Bucket": cfo_lbl, "CFI_Bucket": cfi_lbl, "Borrowing_Bucket": bor_lbl, "Stock_Bucket": stk_lbl}


# --- New API Integration Code ---

# This defines the structure of the data your frontend will send to this API
class TickerRequest(BaseModel):
    symbols: List[str]

# This creates the API endpoint at http://localhost:8000/api/analyze
@app.post("/api/analyze")
async def analyze_stocks_endpoint(request: TickerRequest):
    results = []
    for symbol in request.symbols:
        try:
            # Re-use your existing analysis function for each symbol
            is_valid, company_name = validate_nse_symbol(symbol)
            if is_valid:
                result = analyze_single_stock(symbol, company_name)
                results.append(result)
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            # Add error information to the response for the frontend
            results.append({"Symbol": symbol, "Rating": "Error", "Error": str(e)})
            
    return {"analysis_results": results}

# The interactive command-line menu has been removed as it's not needed for the API server.
