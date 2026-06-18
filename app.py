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

# --- 2. CUSTOM CSS UTK TAMPILAN PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #F8FAFC; }
    .main-title { color: #38BDF8; font-weight: 800; padding-bottom: 5px; }
    .sub-text { color: #94A3B8; font-size: 14px; margin-bottom: 20px; }
    .card-dana { background-color: #1E293B; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .card-ihsg { background-color: #1E293B; padding: 20px; border-radius: 12px; border-left: 5px solid #38BDF8; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE & HELPER ---
@st.cache_data(ttl=604800)
def load_mega_market_tickers():
    saham_300_plus = ["AADI", "AALI", "ABBA", "ADRO", "AKRA", "AMRT", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", "BBTN", "BRMS", "BUVA", "CPIN", "DSSA", "ESIP", "ESSA", "FILM", "GGRM", "ICBP", "INDF", "INKP", "IRSX", "ITMG", "JPFA", "KAEF", "KLBF", "KLBV", "MDKA", "MYOR", "NCKL", "NZIA", "PTRO", "RMKE", "RMKO", "SGRO", "TLKM", "TMPO", "ULTJ", "UNTR", "WIFI"]
    return sorted(list(set([f"{t.strip().upper()}.JK" for t in saham_300_plus])))

master_tickers_jk = load_mega_market_tickers()
master_tickers_clean = [t.replace(".JK", "") for t in master_tickers_jk]

def get_dividend_data(ticker):
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        divs = stock.dividends
        if divs.empty: return "N/A"
        last_date = divs.index[-1].strftime('%d/%m/%y')
        last_val = divs.iloc[-1]
        return f"{last_val:,.0f} ({last_date})"
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
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last_price = float(df['Close'].iloc[-1])
        last_vol_ma = float(df['Volume'].rolling(20).mean().iloc[-1])
        change_pct = ((last_price - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100
        
        # Simulasi Bandarmologi
        net_foreign_b = (last_vol_ma * change_pct * 0.000001) 
        
        return {
            "Ticker": ticker,
            "Price": last_price,
            "Change %": round(change_pct, 2),
            "VWAP Baseline": round(float(df['VWAP'].iloc[-1]), 0),
            "RSI": round(float(df['RSI'].iloc[-1]), 2),
            "Net Foreign Avg": round(net_foreign_b, 2),
            "Dividen Terakhir": get_dividend_data(ticker),
            "Trend": "🟩 Up-Trend" if last_price > float(df['EMA20'].iloc[-1]) else "🟥 Down-Trend",
            "Actionable": "🔥 SUPER BUY" if change_pct > 2 else "⏳ Wait",
            "Dana Masuk %": 60.0, # Placeholder logika
            "Dana Keluar %": 40.0
        }
    except: return None

# --- 5. INTERFACE ---
st.markdown("<h1 class='main-title'>📈 Swing Trading & Scalper Radar Dashboard</h1>", unsafe_allow_html=True)

saham_pilihan = st.sidebar.multiselect("Pilih Saham:", options=master_tickers_clean, default=["ESIP","ESSA","TLKM","BBCA"])

if len(saham_pilihan) > 0:
    with st.spinner("Processing..."):
        data = [analyze_market_momentum(t) for t in saham_pilihan]
        df_radar = pd.DataFrame([d for d in data if d is not None])
    
    # Reorder Kolom supaya Dividen di sebelah Net Foreign Avg
    cols = list(df_radar.columns)
    # Pindahkan posisi kolom secara manual
    cols.insert(cols.index('Net Foreign Avg') + 1, cols.pop(cols.index('Dividen Terakhir')))
    df_radar = df_radar[cols]

    st.dataframe(df_radar.style.format({
        "Price": "Rp {:,.0f}",
        "Change %": "{:+.2f}%",
        "Net Foreign Avg": "{:.2f} B",
        "VWAP Baseline": "Rp {:,.0f}"
    }), use_container_width=True)

st.info("💡 Data Dividen menampilkan Nilai (Tanggal Ex-Date).")
