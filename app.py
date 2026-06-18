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
    .card-ihsg { background-color: #1E293B; padding: 20px; border-radius: 12px; border-left: 5px solid #38BDF8; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE MASTER ---
@st.cache_data(ttl=604800)
def load_mega_market_tickers():
    # Daftar emiten Anda... (Tetap sama)
    saham_300_plus = ["AADI", "AALI", "ABBA", "ADRO", "ANTM", "BBCA", "BBRI", "BBNI", "BBTN", "DSSA", "ESIP", "ESSA", "MDKA", "RMKO", "RMKE", "TLKM", "NZIA"]
    return sorted(list(set([f"{t.strip().upper()}.JK" for t in saham_300_plus])))

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
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
        stock = yf.Ticker(formatted_ticker)
        df = stock.history(period="3mo")
        df = clean_yf_dataframe(df)
        
        # Ambil data dividen terakhir
        divs = stock.dividends
        last_div = float(divs.iloc[-1]) if not divs.empty else 0.0
        div_date = divs.index[-1].strftime('%d-%m-%Y') if not divs.empty else "-"

        df['EMA9'] = ta.ema(df['Close'], length=9)
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        
        last_price = float(df['Close'].iloc[-1])
        # ... (Logika perhitungan lainnya sama)
        
        return {
            "Ticker": ticker.replace(".JK", ""),
            "Price": last_price,
            "Net Foreign Avg": round(( ( ( (df['Volume'].iloc[-1] * last_price) / 1_000_000_000 ) * 0.5) / 2), 2),
            "Dividen Terakhir": f"Rp {last_div:,.0f} ({div_date})",
            "Actionable": "⏳ Wait / Neutral", # Placeholder
            # ... tambahkan sisa field agar sesuai
        }
    except: return None

# --- 5. INTERFACE PANEL UTAMA ---
st.markdown("<h1 class='main-title'>📈 Swing Trading & Scalper Radar</h1>", unsafe_allow_html=True)

# ... (Kode chart IHSG sama)

if st.button("🔄 Paksa Ambil Data Baru (Clear Cache)"): st.cache_data.clear()

saham_pilihan = st.sidebar.multiselect("Pilih Saham:", options=master_tickers_clean, default=["ESIP","ESSA","TLKM"])

if len(saham_pilihan) > 0:
    df_radar = run_mega_scanner(saham_pilihan)
    
    if not df_radar.empty:
        # Konfigurasi format tampilan tabel
        column_order = ["Ticker", "Price", "Net Foreign Avg", "Dividen Terakhir"] # Pastikan urutan ini
        st.dataframe(df_radar[column_order], use_container_width=True)
