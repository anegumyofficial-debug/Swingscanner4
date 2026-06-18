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

# --- 2. CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    .main-title { color: #38BDF8; font-weight: 800; }
    .card-dana { background-color: #1E293B; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .card-ihsg { background-color: #1E293B; padding: 20px; border-radius: 12px; border-left: 5px solid #38BDF8; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE & HELPER ---
@st.cache_data(ttl=604800)
def load_mega_market_tickers():
    saham_300_plus = ["AADI", "AALI", "ABBA", "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNVR", "ICBP", "INDF", "ESIP", "ESSA", "MDKA", "ANTM", "GOTO", "BRMS", "PTRO"]
    return sorted(list(set([f"{t.strip().upper()}.JK" for t in saham_300_plus])))

master_tickers_jk = load_mega_market_tickers()
master_tickers_clean = [t.replace(".JK", "") for t in master_tickers_jk]

def get_dividend_history(ticker):
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        divs = stock.dividends
        if divs.empty: return "N/A"
        last_div = divs.iloc[-1]
        return f"Rp {last_div:,.0f}"
    except: return "N/A"

def clean_yf_dataframe(df):
    if df is None or df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df

# --- 4. ENGINE ANALISIS ---
def analyze_market_momentum(ticker):
    try:
        df = yf.download(f"{ticker}.JK", period="3mo", interval="1d", progress=False)
        df = clean_yf_dataframe(df)
        if df is None or len(df) < 4: return None
        
        # Indikator
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        last_price = float(df['Close'].iloc[-1])
        
        # Kalkulasi Sederhana
        change_pct = ((last_price - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100
        net_foreign_avg = (last_price * 0.01) # Contoh logika dummy untuk demo
        
        return {
            "Ticker": ticker,
            "Price": last_price,
            "Change %": round(change_pct, 2),
            "VWAP Baseline": round(float(df['VWAP'].iloc[-1]), 0),
            "Net Foreign Avg": round(net_foreign_avg, 2),
            "Dividen Terakhir": get_dividend_history(ticker),
            "Actionable": "⏳ Wait / Neutral"
        }
    except: return None

# --- 5. INTERFACE ---
st.markdown("<h1 class='main-title'>📈 Swing Trading & Scalper Radar</h1>", unsafe_allow_html=True)
saham_pilihan = st.sidebar.multiselect("Pilih Saham:", options=master_tickers_clean, default=["BBCA", "BBRI", "ESIP", "ESSA"])

if saham_pilihan:
    results = [analyze_market_momentum(t) for t in saham_pilihan]
    df_radar = pd.DataFrame([r for r in results if r is not None])
    
    # Tampilkan Tabel
    st.dataframe(df_radar, use_container_width=True)
    
    # Detail Dividen
    with st.expander("🔍 Lihat Riwayat Dividen Lengkap"):
        pilih_div = st.selectbox("Pilih Saham untuk Detail:", saham_pilihan)
        stock = yf.Ticker(f"{pilih_div}.JK")
        st.write(stock.dividends.tail(5))

else:
    st.info("Pilih saham di sidebar.")
