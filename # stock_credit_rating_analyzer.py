# stock_credit_rating_analyzer.py
# ------------------------------------------------------------
# Credit scoring WITHOUT promoter pledge, market-cap aware.
# Integrated with Google News event signals (no separate CSV needed).
#
# Enhanced version with comprehensive NSE stock list and auto .NS addition
# Features: User-friendly input, extensive NSE company database
# ------------------------------------------------------------

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple

import pandas as pd
import yfinance as yf
import feedparser


# ---------------- Config ----------------
OUTPUT_PATH = Path("data/credit_scores_no_pledge.csv")

# Comprehensive NSE Companies List (Major ones + Popular stocks)
NSE_COMPANIES: Dict[str, str] = {
    # Large Cap - Top companies by market cap
    "RELIANCE": "Reliance Industries Ltd",
    "TCS": "Tata Consultancy Services Ltd",
    "HDFCBANK": "HDFC Bank Ltd",
    "INFY": "Infosys Ltd",
    "HINDUNILVR": "Hindustan Unilever Ltd",
    "ITC": "ITC Ltd",
    "ICICIBANK": "ICICI Bank Ltd",
    "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel Ltd",
    "KOTAKBANK": "Kotak Mahindra Bank Ltd",
    
    # Technology
    "WIPRO": "Wipro Ltd",
    "HCLTECH": "HCL Technologies Ltd",
    "TECHM": "Tech Mahindra Ltd",
    "LTI": "Larsen & Toubro Infotech Ltd",
    "LTIM": "LTI Mindtree Ltd",
    "MPHASIS": "Mphasis Ltd",
    
    # Banking & Financial Services
    "AXISBANK": "Axis Bank Ltd",
    "BAJFINANCE": "Bajaj Finance Ltd",
    "BAJAJFINSV": "Bajaj Finserv Ltd",
    "INDUSINDBK": "IndusInd Bank Ltd",
    "HDFCLIFE": "HDFC Life Insurance Company Ltd",
    "SBILIFE": "SBI Life Insurance Company Ltd",
    "ICICIGI": "ICICI General Insurance Company Ltd",
    
    # Automobiles
    "MARUTI": "Maruti Suzuki India Ltd",
    "TATAMOTORS": "Tata Motors Ltd",
    "M&M": "Mahindra & Mahindra Ltd",
    "BAJAJ-AUTO": "Bajaj Auto Ltd",
    "HEROMOTOCO": "Hero MotoCorp Ltd",
    "EICHERMOT": "Eicher Motors Ltd",
    "ASHOKLEY": "Ashok Leyland Ltd",
    "TVSMOTORS": "TVS Motor Company Ltd",
    
    # Pharmaceuticals
    "SUNPHARMA": "Sun Pharmaceutical Industries Ltd",
    "DRREDDY": "Dr. Reddy's Laboratories Ltd",
    "CIPLA": "Cipla Ltd",
    "DIVISLAB": "Divi's Laboratories Ltd",
    "BIOCON": "Biocon Ltd",
    "LUPIN": "Lupin Ltd",
    "AUROPHARMA": "Aurobindo Pharma Ltd",
    "TORNTPHARM": "Torrent Pharmaceuticals Ltd",
    
    # Oil & Gas
    "ONGC": "Oil and Natural Gas Corporation Ltd",
    "IOC": "Indian Oil Corporation Ltd",
    "BPCL": "Bharat Petroleum Corporation Ltd",
    "HPCL": "Hindustan Petroleum Corporation Ltd",
    "GAIL": "GAIL (India) Ltd",
    "COALINDIA": "Coal India Ltd",
    
    # Metals & Mining
    "TATASTEEL": "Tata Steel Ltd",
    "JSWSTEEL": "JSW Steel Ltd",
    "HINDALCO": "Hindalco Industries Ltd",
    "VEDL": "Vedanta Ltd",
    "SAIL": "Steel Authority of India Ltd",
    "NMDC": "NMDC Ltd",
    "MOIL": "MOIL Ltd",
    
    # Infrastructure & Construction
    "LT": "Larsen & Toubro Ltd",
    "ULTRACEMCO": "UltraTech Cement Ltd",
    "SHREECEM": "Shree Cement Ltd",
    "ACC": "ACC Ltd",
    "AMBUJCEMENT": "Ambuja Cements Ltd",
    "JKCEMENT": "JK Cement Ltd",
    
    # Telecom
    "JIOFINANCE": "Jio Financial Services Ltd",
    "IDEA": "Vodafone Idea Ltd",
    
    # Consumer Goods
    "NESTLEIND": "Nestle India Ltd",
    "BRITANNIA": "Britannia Industries Ltd",
    "DABUR": "Dabur India Ltd",
    "MARICO": "Marico Ltd",
    "GODREJCP": "Godrej Consumer Products Ltd",
    "COLPAL": "Colgate Palmolive (India) Ltd",
    "PGHH": "Procter & Gamble Hygiene and Health Care Ltd",
    "EMAMILTD": "Emami Ltd",
    
    # Retail & E-commerce
    "AVENUE": "Avenue Supermarts Ltd (DMart)",
    "TRENTLTD": "Trent Ltd",
    "RELIANCE": "Reliance Retail",
    
    # Power & Utilities
    "NTPC": "NTPC Ltd",
    "POWERGRID": "Power Grid Corporation of India Ltd",
    "TATAPOWER": "Tata Power Company Ltd",
    "ADANIPOWER": "Adani Power Ltd",
    "ADANIGREEN": "Adani Green Energy Ltd",
    
    # Airlines & Travel
    "INDIGO": "InterGlobe Aviation Ltd",
    "SPICEJET": "SpiceJet Ltd",
    
    # Textiles
    "WELCORP": "Welspun Corp Ltd",
    "ARVIND": "Arvind Ltd",
    
    # Chemicals
    "UPL": "UPL Ltd",
    "PIDILITIND": "Pidilite Industries Ltd",
    "AAVAS": "Aavas Financiers Ltd",
    "TATACHEM": "Tata Chemicals Ltd",
    
    # Real Estate
    "DLF": "DLF Ltd",
    "GODREJPROP": "Godrej Properties Ltd",
    "OBEROIRLTY": "Oberoi Realty Ltd",
    "PRESTIGE": "Prestige Estates Projects Ltd",
    
    # Adani Group
    "ADANIPORTS": "Adani Ports and Special Economic Zone Ltd",
    "ADANIENT": "Adani Enterprises Ltd",
    "ADANIGAS": "Adani Total Gas Ltd",
    "ADANITRANS": "Adani Transmission Ltd",
    
    # Tata Group
    "TATACONSUM": "Tata Consumer Products Ltd",
    "TATACOFFEE": "Tata Coffee Ltd",
    "TATAELXSI": "Tata Elxsi Ltd",
    "TATACOMM": "Tata Communications Ltd",
    
    # Others
    "ZOMATO": "Zomato Ltd",
    "PAYTM": "One 97 Communications Ltd",
    "NYKAA": "FSN E-Commerce Ventures Ltd",
    "POLICYBZR": "PB Fintech Ltd",
    "IRCTC": "Indian Railway Catering and Tourism Corporation Ltd",
    "IRFC": "Indian Railway Finance Corporation Ltd",
    "HAL": "Hindustan Aeronautics Ltd",
    "BEL": "Bharat Electronics Ltd",
    "SJVN": "SJVN Ltd",
    "NHPC": "NHPC Ltd",
    "RECLTD": "REC Ltd",
    "PFC": "Power Finance Corporation Ltd",
    "HUDCO": "Housing and Urban Development Corporation Ltd",
    "NBCC": "NBCC (India) Ltd",
    "RITES": "RITES Ltd",
    "CONCOR": "Container Corporation of India Ltd",
    "SCI": "Shipping Corporation of India Ltd",
    "GMRINFRA": "GMR Infrastructure Ltd",
    "L&TFH": "L&T Finance Holdings Ltd",
    "MOTHERSON": "Motherson Sumi Systems Ltd",
    "APOLLOHOSP": "Apollo Hospitals Enterprise Ltd",
    "FORTIS": "Fortis Healthcare Ltd",
    "MAXHEALTH": "Max Healthcare Institute Ltd",
    "JUBLFOOD": "Jubilant FoodWorks Ltd",
    "PAGEIND": "Page Industries Ltd",
    "RELAXO": "Relaxo Footwears Ltd",
    "VBL": "Varun Beverages Ltd",
    "MCDOWELL-N": "United Spirits Ltd",
    "UBL": "United Breweries Ltd",
    "RADICO": "Radico Khaitan Ltd"
}

# Market-cap tier cutoffs in INR crores
LARGE_CAP_CRORE = 100_000        # ≥ ₹1,00,000 Cr
MID_CAP_CRORE_LOW = 10_000       #  ₹10,000–₹1,00,000 Cr


# ---------------- Helpers ----------------
def ensure_dirs() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def safe_ratio(n: Optional[float], d: Optional[float]) -> Optional[float]:
    if n is None or d is None:
        return None
    try:
        d = float(d)
        if d == 0.0:
            return None
        return float(n) / d
    except Exception:
        return None


def pick_first(df: pd.DataFrame, keys: List[str]) -> Optional[str]:
    if df is None or df.empty:
        return None
    lower_map = {str(idx).strip().lower(): idx for idx in df.index}
    for k in keys:
        key = k.strip().lower()
        if key in lower_map:
            return lower_map[key]
    return None


def clamp_event_score(x: Optional[float]) -> int:
    if x is None:
        return 0
    try:
        xi = int(round(float(x)))
    except Exception:
        return 0
    return max(-5, min(3, xi))


def format_ticker(symbol: str) -> str:
    """Convert user input to proper Yahoo Finance ticker format"""
    symbol = symbol.strip().upper()
    # If already has .NS, return as is
    if symbol.endswith('.NS'):
        return symbol
    # Add .NS for NSE stocks
    return f"{symbol}.NS"


def validate_nse_symbol(symbol: str) -> Tuple[bool, str]:
    """Validate if symbol exists in NSE companies list"""
    symbol = symbol.strip().upper().replace('.NS', '')
    
    # Direct match
    if symbol in NSE_COMPANIES:
        return True, NSE_COMPANIES[symbol]
    
    # Fuzzy search for common variations
    for nse_symbol, company_name in NSE_COMPANIES.items():
        if symbol in nse_symbol or nse_symbol in symbol:
            return True, company_name
    
    # If not found in our list, still allow it (might be a valid stock not in our database)
    return True, symbol


# ---------------- News: Google News RSS → Event Signal ----------------
POSITIVE_KEYWORDS = [
    "profit", "growth", "expansion", "order win", "funding", "merger", "record high",
    "revenue up", "earnings beat", "strong performance", "dividend", "acquisition"
]
NEGATIVE_KEYWORDS = [
    "fraud", "default", "loss", "scam", "investigation", "penalty", "layoff", "lawsuit",
    "decline", "fall", "crash", "warning", "debt", "trouble", "crisis"
]


def news_event_signal_for_company(company_name: str, top_n: int = 5) -> int:
    """
    Fetch top N Google News headlines for the company and compute a simple
    keyword-based sentiment/event score.
    """
    try:
        query = company_name.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        headlines = [entry.title for entry in feed.entries[:top_n]]

        score = 0
        for h in headlines:
            text = (h or "").lower()
            # +1 per matched positive token
            for w in POSITIVE_KEYWORDS:
                if w in text:
                    score += 1
            # -1 per matched negative token
            for w in NEGATIVE_KEYWORDS:
                if w in text:
                    score -= 1
        # Clamp to your scoring range [-5, +3]
        return clamp_event_score(score)
    except Exception as e:
        print(f"Warning: Could not fetch news for {company_name}: {e}")
        return 0


# ---------------- Data fetch (Yahoo Finance) ----------------
def get_market_cap_and_tier(yf_ticker: str) -> Tuple[Optional[float], str]:
    """
    Returns (market_cap_crore, tier) where tier in {"Large","Mid","Small"}.
    If marketCap missing, default to 'Mid' (neutral).
    """
    try:
        info = yf.Ticker(yf_ticker).info or {}
        mc = info.get("marketCap")
        if mc is None:
            return (None, "Mid")
        # Yahoo .NS is INR; convert to crores
        mc_crore = float(mc) / 1e7
        if mc_crore >= LARGE_CAP_CRORE:
            tier = "Large"
        elif mc_crore >= MID_CAP_CRORE_LOW:
            tier = "Mid"
        else:
            tier = "Small"
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

        # Income Statement
        rev_key = pick_first(fin, ["Total Revenue", "TotalRevenue", "Revenue"])
        ni_key = pick_first(fin, ["Net Income", "NetIncome", "Net income applicable to common shares"])

        revenue_now = fin.loc[rev_key].iloc[0] if rev_key is not None else None
        revenue_prev = fin.loc[rev_key].iloc[1] if (rev_key is not None and fin.shape[1] > 1) else None
        net_profit_now = fin.loc[ni_key].iloc[0] if ni_key is not None else None

        # Cash Flow
        cfo_key = pick_first(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"])
        cfi_key = pick_first(cf, ["Investing Cash Flow", "Total Cashflows From Investing Activities"])

        cfo_now = cf.loc[cfo_key].iloc[0] if cfo_key is not None else None
        cfi_now = cf.loc[cfi_key].iloc[0] if cfi_key is not None else None

        # Balance Sheet (debt)
        debt_key = pick_first(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation", "Long-term debt"])
        debt_now = bs.loc[debt_key].iloc[0] if debt_key is not None else None
        debt_prev = bs.loc[debt_key].iloc[1] if (debt_key is not None and bs.shape[1] > 1) else None

        # Derived features
        yoy_growth = None
        if revenue_now is not None and revenue_prev not in (None, 0):
            yoy_growth = ((float(revenue_now) - float(revenue_prev)) / abs(float(revenue_prev))) * 100.0

        pat_margin = None
        if revenue_now not in (None, 0) and net_profit_now is not None:
            pat_margin = (float(net_profit_now) / float(revenue_now)) * 100.0

        cfo_pat_ratio = safe_ratio(cfo_now, net_profit_now)
        cfi_rev_ratio = safe_ratio(cfi_now, revenue_now)

        borrowing_growth = None
        if debt_now is not None and debt_prev not in (None, 0):
            borrowing_growth = ((float(debt_now) - float(debt_prev)) / abs(float(debt_prev))) * 100.0

        # 30D Stock Return
        end_date = datetime.now()
        start_date = end_date - timedelta(days=35)  # Get a bit more data to ensure 30 days
        hist = t.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        stock_return = None
        if not hist.empty and len(hist["Close"]) > 1:
            stock_return = ((float(hist["Close"].iloc[-1]) - float(hist["Close"].iloc[0])) / float(hist["Close"].iloc[0])) * 100.0

        return {
            "YoY_Growth": round(yoy_growth, 2) if yoy_growth is not None else None,
            "PAT_Margin": round(pat_margin, 2) if pat_margin is not None else None,
            "CFO_PAT_Ratio": round(cfo_pat_ratio, 2) if cfo_pat_ratio is not None else None,
            "CFI_Revenue": round(cfi_rev_ratio, 4) if cfi_rev_ratio is not None else None,
            "Borrowing_Growth_%": round(borrowing_growth, 2) if borrowing_growth is not None else None,
            "Stock_Return_30D": round(stock_return, 2) if stock_return is not None else None,
        }
    except Exception as e:
        print(f"Warning: Could not compute features for {yf_ticker}: {e}")
        return {
            "YoY_Growth": None,
            "PAT_Margin": None,
            "CFO_PAT_Ratio": None,
            "CFI_Revenue": None,
            "Borrowing_Growth_%": None,
            "Stock_Return_30D": None,
        }


# ---------------- Scoring (Collapsed Tiers) - SAME AS ORIGINAL ----------------
def score_yoy_growth(y: Optional[float], tier: str) -> Tuple[int, str]:
    if y is None:
        return 0, "NA"
    if tier in ("Large", "Mid"):
        if y > 2:        return 2,  ">2%"
        if 0 <= y <= 2:  return 0,  "0–2%"
        return -1, "<0%"
    # Small -> Mid rules
    if y > 5:           return 2,  ">5%"
    if 2 <= y <= 5:     return 0,  "2–5%"
    return -1, "<2%"


def score_pat_margin(p: Optional[float], tier: str) -> Tuple[int, str]:
    if p is None:
        return 0, "NA"
    if tier in ("Large", "Mid"):
        if p > 8:            return 2, ">8%"
        if 2.5 <= p <= 8:    return 1, "2.5–8%"
        return -2, "<2.5%"
    # Small -> Mid rules
    if p > 9:                return 2, ">9%"
    if 2.5 <= p <= 9:        return 1, "2.5–9%"
    return -2, "<2.5%"


def score_cfo_pat(r: Optional[float]) -> Tuple[int, str]:
    if r is None:
        return 0, "NA"
    if r > 1.0:             return 2,  ">1.0x"
    if 0.7 <= r <= 1.0:     return 1,  "0.7–1.0x"
    return -1, "<0.7x"


def score_cfi_rev(r: Optional[float], tier: str) -> Tuple[int, str]:
    # buffed rewards, softened worst penalty (−1)
    if r is None:
        return 0, "NA"
    # Convert to percentage for easier comparison
    r_pct = r * 100
    if tier in ("Large", "Mid"):
        if r_pct > -10:             return 2, ">-10%"
        if -20 <= r_pct <= -10:     return 1, "-20% to -10%"
        return -1, "<-20%"
    # Small -> Mid rules
    if r_pct > -10:                 return 2, ">-10%"
    if -15 <= r_pct <= -10:         return 1, "-15% to -10%"
    return -1, "<-15%"


def score_borrowing_growth(b: Optional[float], tier: str) -> Tuple[int, str]:
    # buffed: +2/+1/−2
    if b is None:
        return 0, "NA"
    if tier in ("Large", "Mid"):
        if b < 10:               return 2, "<10%"
        if 10 <= b <= 25:        return 1, "10–25%"
        return -2, ">25%"
    # Small -> Mid rules
    if b < 8:                    return 2, "<8%"
    if 8 <= b <= 25:             return 1, "8–25%"
    return -2, ">25%"


def score_stock_return(sr: Optional[float]) -> Tuple[int, str]:
    if sr is None:
        return 0, "NA"
    if sr > 0:               return 1, ">0%"
    if -5 <= sr <= 0:        return 0, "-5%–0%"
    return -1, "<-5%"


# ---------------- Ratings (AAA … D) - SAME AS ORIGINAL ----------------
def rating_grade(total_score: int, tier: str) -> str:
    if tier in ("Large", "Mid"):
        if total_score >= 11:  return "AAA"
        if total_score >= 9:   return "AA"
        if total_score >= 7:   return "A"
        if total_score >= 5:   return "BBB"
        if total_score >= 3:   return "BB"
        if total_score >= 1:   return "B"
        if total_score >= -1:  return "C"
        return "D"
    # Small (stricter)
    if total_score >= 12:  return "AAA"
    if total_score >= 10:  return "AA"
    if total_score >= 8:   return "A"
    if total_score >= 6:   return "BBB"
    if total_score >= 4:   return "BB"
    if total_score >= 2:   return "B"
    if total_score >= 0:   return "C"
    return "D"


def analyze_single_stock(symbol: str, company_name: str = None) -> Dict:
    """Analyze a single stock and return its rating data"""
    yf_ticker = format_ticker(symbol)
    clean_symbol = symbol.upper().replace('.NS', '')
    
    print(f"Fetching metrics for {clean_symbol} ({yf_ticker}) ...")
    
    if company_name is None:
        # Try to get company name from our database
        _, company_name = validate_nse_symbol(clean_symbol)
    
    # Core features & tier
    feats = compute_features(yf_ticker)
    mc_crore, tier = get_market_cap_and_tier(yf_ticker)

    # News-based event score (from Google News RSS)
    evt_s = news_event_signal_for_company(company_name, top_n=5)

    # Component scores + labels
    yoy_s, yoy_lbl = score_yoy_growth(feats["YoY_Growth"], tier)
    pat_s, pat_lbl = score_pat_margin(feats["PAT_Margin"], tier)
    cfo_s, cfo_lbl = score_cfo_pat(feats["CFO_PAT_Ratio"])
    cfi_s, cfi_lbl = score_cfi_rev(feats["CFI_Revenue"], tier)
    bor_s, bor_lbl = score_borrowing_growth(feats["Borrowing_Growth_%"], tier)
    stk_s, stk_lbl = score_stock_return(feats["Stock_Return_30D"])

    total = yoy_s + pat_s + cfo_s + cfi_s + bor_s + stk_s + evt_s
    grade = rating_grade(int(total), tier)

    return {
        "Symbol": clean_symbol,
        "CompanyName_ForNews": company_name,
        "Yahoo_Ticker": yf_ticker,
        "MarketCap_Crore": round(mc_crore, 2) if mc_crore is not None else None,
        "Tier": tier,
        **feats,
        "Event_Score": evt_s,
        "Score_YoY_Growth": yoy_s,
        "Score_PAT_Margin": pat_s,
        "Score_CFO_PAT": cfo_s,
        "Score_CFI_Revenue": cfi_s,
        "Score_Borrowing_Growth": bor_s,
        "Score_Stock_Return_30D": stk_s,
        "Total_Score": int(total),
        "Rating": grade,
        # Explanations
        "YoY_Bucket": yoy_lbl,
        "PAT_Bucket": pat_lbl,
        "CFO_PAT_Bucket": cfo_lbl,
        "CFI_Bucket": cfi_lbl,
        "Borrowing_Bucket": bor_lbl,
        "Stock_Bucket": stk_lbl,
    }


def display_results(result: Dict):
    """Display results in a formatted way"""
    print("\n" + "="*80)
    print(f"CREDIT RATING ANALYSIS FOR {result['Symbol']}")
    print("="*80)
    print(f"Company: {result['CompanyName_ForNews']}")
    print(f"Yahoo Ticker: {result['Yahoo_Ticker']}")
    print(f"Market Cap: ₹{result['MarketCap_Crore']:,.2f} Crores" if result['MarketCap_Crore'] else "Market Cap: N/A")
    print(f"Tier: {result['Tier']}")
    
    print(f"\n🏆 FINAL RATING: {result['Rating']} (Score: {result['Total_Score']})")
    
    print("\n📊 KEY METRICS:")
    print(f"  • YoY Growth: {result['YoY_Growth']}% [{result['YoY_Bucket']}] → Score: {result['Score_YoY_Growth']}")
    print(f"  • PAT Margin: {result['PAT_Margin']}% [{result['PAT_Bucket']}] → Score: {result['Score_PAT_Margin']}")
    print(f"  • CFO/PAT Ratio: {result['CFO_PAT_Ratio']}x [{result['CFO_PAT_Bucket']}] → Score: {result['Score_CFO_PAT']}")
    print(f"  • CFI/Revenue: {result['CFI_Revenue']} [{result['CFI_Bucket']}] → Score: {result['Score_CFI_Revenue']}")
    print(f"  • Borrowing Growth: {result['Borrowing_Growth_%']}% [{result['Borrowing_Bucket']}] → Score: {result['Score_Borrowing_Growth']}")
    print(f"  • Stock Return (30D): {result['Stock_Return_30D']}% [{result['Stock_Bucket']}] → Score: {result['Score_Stock_Return_30D']}")
    print(f"  • News Sentiment: {result['Event_Score']}")
    
    print("\n💡 RATING SCALE:")
    print("  AAA (Excellent) > AA (Very Good) > A (Good) > BBB (Satisfactory)")
    print("  BB (Adequate) > B (Below Average) > C (Poor) > D (Very Poor)")


def show_popular_stocks():
    """Display popular NSE stocks by category"""
    categories = {
        "🏦 BANKING & FINANCE": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "BAJFINANCE", "INDUSINDBK"],
        "💻 TECHNOLOGY": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "MPHASIS"],
        "🚗 AUTOMOBILES": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "HEROMOTOCO", "EICHERMOT"],
        "💊 PHARMACEUTICALS": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "BIOCON", "LUPIN"],
        "⛽ OIL & GAS": ["RELIANCE", "ONGC", "IOC", "BPCL", "HPCL", "GAIL"],
        "🏭 INDUSTRIAL": ["LT", "TATASTEEL", "JSWSTEEL", "HINDALCO", "ULTRACEMCO", "NTPC"],
        "🛍 CONSUMER GOODS": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO"],
        "📱 NEW AGE": ["ZOMATO", "PAYTM", "NYKAA", "POLICYBZR", "IRCTC"]
    }
    
    print("\n🌟 POPULAR NSE STOCKS BY CATEGORY:")
    print("="*60)
    
    for category, stocks in categories.items():
        print(f"\n{category}:")
        for i, stock in enumerate(stocks, 1):
            company_name = NSE_COMPANIES.get(stock, stock)
            print(f"  {i}. {stock} - {company_name}")


def save_to_csv(results: List[Dict]):
    """Save results to CSV file"""
    if not results:
        print("No results to save.")
        return
    
    ensure_dirs()
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ Results saved to: {OUTPUT_PATH}")


def interactive_menu():
    """Interactive menu for user input"""
    print("\n" + "="*80)
    print("🏦 STOCK CREDIT RATING ANALYZER")
    print("="*80)
    print("Analyze NSE stocks with comprehensive credit scoring")
    print("Features: Financial metrics + Market cap tiers + News sentiment")
    
    while True:
        print("\n📋 MAIN MENU:")
        print("1. Analyze single stock")
        print("2. Analyze multiple stocks (batch)")
        print("3. Show popular NSE stocks")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            analyze_single_interactive()
        elif choice == "2":
            analyze_batch_interactive()
        elif choice == "3":
            show_popular_stocks()
            input("\nPress Enter to continue...")
        elif choice == "4":
            print("\nThank you for using Stock Credit Rating Analyzer! 👋")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")


def analyze_single_interactive():
    """Interactive single stock analysis"""
    print("\n" + "-"*50)
    print("📊 SINGLE STOCK ANALYSIS")
    print("-"*50)
    
    while True:
        symbol = input("\nEnter NSE stock symbol (e.g., RELIANCE, TCS): ").strip()
        if not symbol:
            print("❌ Please enter a valid symbol.")
            continue
            
        # Validate symbol
        is_valid, company_name = validate_nse_symbol(symbol)
        if not is_valid:
            print(f"⚠️  Symbol '{symbol}' not found in our database. Continue anyway? (y/n): ", end="")
            if input().lower() != 'y':
                continue
        
        try:
            result = analyze_single_stock(symbol, company_name)
            display_results(result)
            
            # Ask if user wants to save
            save_choice = input("\n💾 Save results to CSV? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_to_csv([result])
            
            break
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            retry = input("Retry with different symbol? (y/n): ").strip().lower()
            if retry != 'y':
                break


def analyze_batch_interactive():
    """Interactive batch analysis"""
    print("\n" + "-"*50)
    print("📊 BATCH STOCK ANALYSIS")
    print("-"*50)
    
    print("\nEnter stock symbols separated by commas")
    print("Example: RELIANCE, TCS, HDFCBANK, INFY")
    
    symbols_input = input("\nStock symbols: ").strip()
    if not symbols_input:
        print("❌ No symbols entered.")
        return
    
    # Parse symbols
    symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
    if not symbols:
        print("❌ No valid symbols found.")
        return
    
    print(f"\n🔄 Analyzing {len(symbols)} stocks...")
    results = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        try:
            _, company_name = validate_nse_symbol(symbol)
            result = analyze_single_stock(symbol, company_name)
            results.append(result)
            print(f"✅ {symbol}: {result['Rating']} (Score: {result['Total_Score']})")
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            continue
    
    if results:
        print(f"\n🎉 Successfully analyzed {len(results)} stocks!")
        
        # Display summary
        print("\n📋 BATCH RESULTS SUMMARY:")
        print("-" * 60)
        print(f"{'Symbol':<12} {'Rating':<8} {'Score':<6} {'Tier':<8} {'Company'}")
        print("-" * 60)
        
        # Sort by rating (AAA to D) then by score
        rating_order = {"AAA": 0, "AA": 1, "A": 2, "BBB": 3, "BB": 4, "B": 5, "C": 6, "D": 7}
        results.sort(key=lambda x: (rating_order.get(x['Rating'], 8), -x['Total_Score']))
        
        for result in results:
            company_short = result['CompanyName_ForNews'][:25] + "..." if len(result['CompanyName_ForNews']) > 28 else result['CompanyName_ForNews']
            print(f"{result['Symbol']:<12} {result['Rating']:<8} {result['Total_Score']:<6} {result['Tier']:<8} {company_short}")
        
        # Save results
        save_choice = input(f"\n💾 Save all {len(results)} results to CSV? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_to_csv(results)
    else:
        print("\n❌ No stocks were successfully analyzed.")


def show_help():
    """Show help information"""
    print("\n" + "="*80)
    print("📚 HELP & SCORING METHODOLOGY")
    print("="*80)
    
    print("\n🎯 SCORING COMPONENTS:")
    print("1. YoY Growth (Revenue year-over-year growth)")
    print("2. PAT Margin (Profit After Tax margin)")
    print("3. CFO/PAT Ratio (Cash Flow from Operations to PAT)")
    print("4. CFI/Revenue (Capital Investment to Revenue ratio)")
    print("5. Borrowing Growth (Debt growth rate)")
    print("6. Stock Return (30-day stock performance)")
    print("7. News Sentiment (Based on recent news headlines)")
    
    print("\n🏢 MARKET CAP TIERS:")
    print("• Large Cap: ≥ ₹1,00,000 Crores")
    print("• Mid Cap: ₹10,000 - ₹1,00,000 Crores")
    print("• Small Cap: < ₹10,000 Crores")
    
    print("\n⭐ RATING SCALE:")
    print("AAA: Excellent (Score ≥ 11/12)")
    print("AA:  Very Good (Score ≥ 9/10)")
    print("A:   Good (Score ≥ 7/8)")
    print("BBB: Satisfactory (Score ≥ 5/6)")
    print("BB:  Adequate (Score ≥ 3/4)")
    print("B:   Below Average (Score ≥ 1/2)")
    print("C:   Poor (Score ≥ -1/0)")
    print("D:   Very Poor (Score < -1/0)")
    
    print("\n💡 USAGE TIPS:")
    print("• Enter symbols without .NS (automatically added)")
    print("• Use comma-separated list for batch analysis")
    print("• Higher scores indicate better creditworthiness")
    print("• News sentiment adds ±5 to ±3 points based on headlines")


# ---------------- Main Execution ----------------
def main():
    """Main function to run the analyzer"""
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Thank you for using Stock Credit Rating Analyzer!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue if it persists.")


if __name__ == "__main__":
    main()