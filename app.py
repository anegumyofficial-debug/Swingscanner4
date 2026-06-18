import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import pytz  
import concurrent.futures

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Swing & Scalper Dashboard BEI", layout="wide", page_icon="📈")

wib_tz = pytz.timezone('Asia/Jakarta')
wib_now = datetime.now(wib_tz)

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    .main-title { color: #38BDF8; font-weight: 800; }
    .card-dana { background-color: #1E293B; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .card-ihsg { background-color: #1E293B; padding: 20px; border-radius: 12px; border-left: 5px solid #38BDF8; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE MASTER & FUNGSI DIVIDEN ---
@st.cache_data(ttl=604800)
def load_mega_market_tickers():
    saham_300_plus = ["AADI", "AALI", "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "GGRM", "ITMG", "INDF", "ICBP", "KLBF", "ESIP", "ESSA", "MDKA", "RMKO", "RMKE", "DSSA"]
    return sorted(list(set([f"{t.strip().upper()}.JK" for t in saham_300_plus])))

def get_latest_dividend(ticker):
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        divs = stock.dividends
        if divs is not None and not divs.empty:
            last_div = divs.iloc[-1]
            last_date = divs.index[-1].strftime('%d-%m')
            return f"Rp{int(last_div)} ({last_date})"
        return "-"
    except:
        return "-"

master_tickers_jk = load_mega_market_tickers()
master_tickers_clean = [t.replace(".JK", "") for t in master_tickers_jk]

def clean_yf_dataframe(df):
    if df is None or df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df

# --- 4. ENGINE ANALISIS ---
def analyze_market_momentum(ticker):
    try:
        ticker_name = ticker.replace(".JK", "")
        df = yf.download(f"{ticker_name}.JK", period="3mo", interval="1d", progress=False)
        df = clean_yf_dataframe(df)
        if df is None or len(df) < 4: return None
        
        # Indikator
        df['EMA20'] = ta.ema(df['Close'], length=20)
        last_price = float(df['Close'].iloc[-1])
        
        # Logika Sederhana untuk Simulasi
        change_pct = ((last_price - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100
        
        return {
            "Ticker": ticker_name,
            "Price": last_price,
            "Change %": round(change_pct, 2),
            "Net Foreign Avg": 0.0, # Placeholder
            "Dividen Terakhir": get_latest_dividend(ticker_name),
            "Actionable": "⏳ Wait / Neutral"
        }
    except: return None

def run_mega_scanner(ticker_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(analyze_market_momentum, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res: results.append(res)
    return pd.DataFrame(results)

# --- 5. INTERFACE ---
st.markdown("<h1 class='main-title'>📈 Swing Trading Radar</h1>", unsafe_allow_html=True)

saham_pilihan = st.multiselect("Pilih Saham:", options=master_tickers_clean, default=["BBCA", "BBRI", "ESIP", "ESSA"])

if len(saham_pilihan) > 0:
    df_radar = run_mega_scanner(saham_pilihan)
    
    if not df_radar.empty:
        # Reorder kolom agar Dividen di sebelah Net Foreign Avg
        cols = df_radar.columns.tolist()
        if "Net Foreign Avg" in cols and "Dividen Terakhir" in cols:
            idx = cols.index("Net Foreign Avg")
            cols.insert(idx + 1, cols.pop(cols.index("Dividen Terakhir")))
            df_radar = df_radar[cols]
        
        st.dataframe(df_radar, use_container_width=True)
