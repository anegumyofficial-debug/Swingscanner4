import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime
import pytz  
import concurrent.futures

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Scalper Radar BEI - Full Edition", layout="wide", page_icon="⚡")

# Mengunci jam server ke zona waktu WIB (Asia/Jakarta)
wib_tz = pytz.timezone('Asia/Jakarta')
wib_now = datetime.now(wib_tz)

# --- 2. CUSTOM CSS SCALPER ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #F8FAFC; }
    .main-title { color: #38BDF8; font-weight: 800; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)


# --- 3. DATABASE MASTER EMITEN ---
@st.cache_data(ttl=604800)
def load_mega_market_tickers():
    saham_300_plus = [
        "AADI", "AALI", "ABBA", "ABDA", "ABMM", "ACES", "ACST", "ADCP", "ADHI", "ADME", "ADRO", "AGRO", "AGRS", "AHAP", "AISA",
        "AKRA", "AKSI", "ALDO", "ALKA", "ALMI", "AMAG", "AMAN", "AMAR", "AMMN", "AMOR", "AMRT", "ANDI", "ANER", "ANTM", "APEX",
        "APII", "APLN", "ARGO", "ARII", "ARKA", "ARNA", "ARTA", "ARTO", "ASBI", "ASGR", "ASII", "ASJT", "ASMI", "ASPI", "ASRI",
        "ASSA", "ATAP", "ATIC", "AUTO", "AVIA", "AWAN", "AYAM", "BADI", "BAJA", "BALI", "BANK", "BAPA", "BAPP", "BARA", "BATA",
        "BAUT", "BBCA", "BBHI", "BBIK", "BBLD", "BBMD", "BBNI", "BBRI", "BBRM", "BBTN", "BBUV", "BBYB", "BCIC", "BCIP", "BDMN",
        "BEEF", "BEKS", "BFIN", "BFTC", "BGTG", "BHAT", "BHIT", "BIMA", "BIPI", "BIPP", "BIRD", "BISI", "BKDP", "BKSL", "BKSW",
        "BMAS", "BMBL", "BMRI", "BMTR", "BNGA", "BNLI", "BNII", "BOBA", "BOLA", "BORO", "BPII", "BRMS", "BRIS", "BRNA", "BRPT",
        "BSDE", "BSIM", "BSSR", "BSWD", "BTEK", "BTPS", "BUKK", "BUVA", "BUMI", "BUTI", "BVIC", "BWPT", "BYAN", "CADI", "CAMP",
        "CANT", "CARE", "CARS", "CASA", "CASH", "CASS", "CATT", "CBDK", "CEKA", "CENT", "CESS", "CFIN", "CINT", "CITA", "CITY", 
        "CLAY", "CLEO", "CLPI", "CMNP", "CMRY", "CNMA", "CNTX", "COAL", "COCO", "CPIN", "CPRI", "CPRO", "CSAP", "CSIS", "CSRA", 
        "CTRA", "CTTH", "CUAN", "CYBER", "DAAZ", "DART", "DAYA", "DEAL", "DEFI", "DEWA", "DFAM", "DGIK", "DHCO", "DIGI", "DILD", 
        "DIVA", "DKFT", "DLTA", "DMAS", "DMED", "DMMX", "DNAR", "DOMI", "DOOH", "DPNS", "DPUM", "DRMA", "DSSA", "DSFI", "DSNG", 
        "DTAL", "DUTO", "DVLA", "DXJN", "DYAN", "EAST", "ECII", "EDII", "EKAD", "ELIT", "ELSA", "EMAL", "EMDE", "EMTK", "ENRG", 
        "EPAC", "EPMT", "ERAA", "ERTX", "ESIP", "ESSA", "ESTA", "ETWA", "EXCL", "FAPA", "FAST", "FASW", "FEST", "FIKA", "FILM", 
        "FINN", "FIRE", "FMII", "FPNI", "FORU", "FOTA", "FRAS", "FUJI", "GAMA", "GAMR", "GARA", "GCOAL", "GDST", "GDYR", "GEMS", 
        "GGRM", "GHEO", "GIAA", "GJTL", "GLOB", "GMCW", "GMTD", "GOLD", "GOTO", "GPRA", "GPSO", "GRHA", "GRIA", "GRPM", "GSMF", 
        "GSJA", "GTBO", "HAIS", "HAKA", "HAMP", "HDFA", "HDIT", "HEAL", "HELI", "HERO", "HEXA", "HIKAM", "HINT", "HISP", "HKMU", 
        "HLIT", "HMAI", "HMPA", "HMSP", "HOKI", "HOMI", "HOTL", "HRTA", "HRUM", "IATA", "IBOS", "IBST", "ICBP", "ICON", "IDPR", 
        "IKAN", "IKBI", "IKHA", "IMAS", "IMJS", "IMPC", "INAF", "INCF", "INDF", "INDO", "INDX", "INDY", "INKP", "INPC", "INPP", 
        "INPS", "INRU", "INTA", "INTD", "INTP", "IPAC", "IPCC", "IPCM", "IPOL", "IRRA", "ISAT", "ISSP", "ITMA", "ITMG", "JAWA", 
        "JECC", "JGLE", "JIHD", "JKON", "JKSW", "JMAS", "JPFA", "JRPT", "JSKY", "JSMR", "JSTB", "JTPE", "KAEF", "KICI", "KIJA", 
        "KKGI", "KLBF", "KLAS", "KMDS", "KOBX", "KOIN", "KOKA", "KOTA", "KPAL", "KPAS", "KPIG", "KREN", "KRNA", "KRAS", "KRAH", 
        "KREI", "LION", "LPCK", "LPKR", "LPLI", "LPPF", "LPPS", "LRN",  "LSIP", "LTLS", "LUCK", "LUMI", "MAIN", "MAMI", "MAPA", 
        "MAPI", "MARI", "MARK", "MASA", "MAYA", "MBAP", "MBSS", "MBTO", "MCOL", "MDIA", "MDKA", "MDKI", "MDLN", "MEDC", "MEGA", 
        "MERK", "META", "MFIN", "MGNA", "MHAX", "MICE", "MIDI", "MILA", "MINA", "MINK", "MIRA", "MITI", "MKNT", "MKPI", "MLBI", 
        "MLIA", "MLPL", "MLPT", "MMIX", "MNCN", "MPMX", "MPPA", "MRAT", "MRPK", "MSIN", "MSKY", "MTDL", "MTEL", "MTFN", "MTLA", 
        "MTMH", "MTPS", "MTRA", "MTSM", "MUTU", "MYOH", "MYOR", "MYTX", "NANO", "NASA", "NASI", "NATO", "NAIK", "NBHA", "NELY", 
        "NETV", "NFCX", "NICK", "NICL", "NIRO", "NISP", "NMSL", "NOBU", "NRCA", "NREI", "NTBK", "NUSA", "NVOM", "NZIA", "OASA", 
        "OBMD", "ODEC", "OILS", "OKAS", "OMRE", "OPMS", "PADI", "PALM", "PAMA", "PANB", "PANI", "PANR", "PANS", "PBID", "PBRX", 
        "PBSA", "PCAR", "PDES", "PEGE", "PEHA", "PGAS", "PGJO", "PGLI", "PICO", "PIHA", "PMMP", "PMJS", "PNBS", "PNIN", "PNLF", 
        "PNSE", "POLY", "POOL", "PORT", "POWR", "PPRI", "PPRE", "PPRO", "PRAS", "PRDA", "PRIM", "PRST", "PSAB", "PSDN", "PSGO", 
        "PSSI", "PTBA", "PTDU", "PTIS", "PUDP", "PURA", "PURE", "PURI", "PWON", "PYFA", "RAAM", "RACY", "RAFI", "RAJA", "RALS", 
        "RANC", "RBMS", "RCCC", "RELI", "REMD", "RICY", "RIGS", "RIMO", "RMKO", "ROCK", "RODA", "ROTI", "SAGE", "SAIP", "SAME", 
        "SAMF", "SATU", "SBAT", "SCCO", "SCMA", "SCNP", "SDMU", "SDPC", "SDRA", "SEMA", "SFAN", "SGER", "SGIK", "SGRO", "SHID", 
        "SIAP", "SICO", "SIDO", "SILO", "SIMA", "SIMP", "SINI", "SIPD", "SKBM", "SKLT", "SMAR", "SMBR", "SMCB", "SMDM", "SMDR", 
        "SMGR", "SMIL", "SMKM", "SMMA", "SMRA", "SMRU", "SMSM", "SNLK", "SOCI", "SOFE", "SOHO", "SONA", "SPMA", "SPTO", "SRSN", 
        "SRTG", "SSIA", "SSMS", "SSTM", "STAR", "STAA", "SUGI", "SULI", "SUPR", "SURE", "SURYA", "SUSU", "TAIS", "TAMU", "TAMP", 
        "TAPG", "TARA", "TAXI", "TBIG", "TBMS", "TCID", "TCPI", "TEBE", "TECH", "TELE", "TENI", "TFAS", "TFCO", "TGKA", "TGRA", 
        "TIFA", "TINS", "TIRA", "TIRT", "TKIM", "TLKM", "TLDN", "TMAS", "TMPO", "TOBA", "TOGA", "TONS", "TOTAL", "TOTO", "TOWR", 
        "TPIA", "TPMA", "TRAM", "TRIL", "TRIM", "TRIN", "TRIS", "TRJA", "TRJU", "TRST", "TRUE", "TRUK", "TSPC", "TUGU", "TURN", 
        "TYRE", "UCID", "UDNG", "UFOE", "UNGO", "UNIT", "UNTR", "UNVR", "URBN", "UTAA", "VINS", "VIVA", "VIVM", "VKTR", "VOKS", 
        "VONE", "VPAC", "WAPO", "WEGE", "WEHA", "WICO", "WIFI", "WIIM", "WIKA", "WINS", "WIRG", "WITA", "WMUU", "WOOD", "WOWS", 
        "WSBP", "WSKT", "WTG",  "WTIA", "YPAS", "YUASA", "YULE", "ZATA", "ZBRA", "ZINC", "ZONE", "PTRO", "BRAM", "IRSX", "WIFI", "KLBV","NCKL","BELI","ULTJ", "TMPO","DSSA","MDKA","RMKO","RMKE"
    ]
    return sorted(list(set([f"{t.strip().upper()}.JK" for t in saham_300_plus])))

master_tickers_jk = load_mega_market_tickers()
master_tickers_clean = [t.replace(".JK", "") for t in master_tickers_jk]

def clean_yf_dataframe(df):
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df

# --- 4. ENGINE ANALISIS INTERDAY SCALPING & VALIDASI FILTER ---
def analyze_scalping_momentum(ticker):
    try:
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
        df = yf.download(formatted_ticker, period="3d", interval="5m", progress=False)
        df = clean_yf_dataframe(df)
        is_fallback = False
        
        if df is None or len(df) < 15 or 'Close' not in df.columns:
            df = yf.download(formatted_ticker, period="3mo", interval="1d", progress=False)
            df = clean_yf_dataframe(df)
            is_fallback = True
            
        if df is None or len(df) < 15 or 'Close' not in df.columns: 
            return None
        
        if not is_fallback:
            cum_vol = df['Volume'].cumsum()
            cum_vol_price = (df['Close'] * df['Volume']).cumsum()
            df['VWAP'] = cum_vol_price / cum_vol
        else:
            df['VWAP'] = ta.ema(df['Close'], length=20)
        
        stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
        df['STOCHk'] = stoch['STOCHk_14_3_3']
        df['STOCHd'] = stoch['STOCHd_14_3_3']
        df['EMA9'] = ta.ema(df['Close'], length=9)
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        total_turnover_today = (df['Close'] * df['Volume']).sum()
        
        last_price = float(df['Close'].iloc[-1])
        last_vwap = float(df['VWAP'].iloc[-1]) if not pd.isna(df['VWAP'].iloc[-1]) else last_price
        last_k = float(df['STOCHk'].iloc[-1]) if not pd.isna(df['STOCHk'].iloc[-1]) else 50.0
        last_d = float(df['STOCHd'].iloc[-1]) if not pd.isna(df['STOCHd'].iloc[-1]) else 50.0
        last_ema = float(df['EMA9'].iloc[-1]) if not pd.isna(df['EMA9'].iloc[-1]) else last_price
        prev_price = float(df['Close'].iloc[-2])
        change_pct = ((last_price - prev_price) / prev_price) * 100
        
        # Logika Sinyal dan Momentum
        if last_price > last_vwap and last_k > last_d and last_k < 50:
            direction, status_sinyal = "🚀 STRONG UP (Siap Buy)", "BUY"
        elif last_price > last_vwap and last_k > last_d:
            direction, status_sinyal = "📈 UP MOMENTUM (Koleksi)", "HOLD"
        elif last_k < last_d and last_k > 65:
            direction, status_sinyal = "🚨 DUMP RISK", "SELL"
        else:
            direction, status_sinyal = "⏳ SIDEWAYS", "WAIT"

        if last_k > 80: momentum = "🔥 Overbought"
        elif last_k < 20: momentum = "🧊 Oversold"
        elif last_k > last_d: momentum = "📈 Bullish"
        else: momentum = "📉 Bearish"

        if is_fallback: direction += " [Hari Kemarin]"
            
        return {
            "Ticker": ticker.replace(".JK", ""),
            "Live Price": last_price,
            "Change %": round(change_pct, 2),
            "Momentum": momentum,
            "Status Sinyal": status_sinyal,
            "Turnover (B)": round(total_turnover_today / 1_000_000_000, 2),
            "VWAP/MA Baseline": round(last_vwap, 0),
            "Stoch %K": round(last_k, 2),
            "Stoch %D": round(last_d, 2),
            "Est. Arah": direction,
            "Proteksi Stop Loss": round(last_vwap * 0.98, 0),
            "Estimasi Take Profit": round(last_price * 1.03, 0)
        }
    except:
        return None

def run_scalper_scanner(ticker_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_ticker = {executor.submit(analyze_scalping_momentum, t): t for t in ticker_list}
        for future in concurrent.futures.as_completed(future_to_ticker):
            res = future.result()
            if res is not None:
                results.append(res)
    return pd.DataFrame(results)
    
st.write(f"⏰ Jam Sinkronisasi Terakhir: **{wib_now.strftime('%d-%m-%Y %H:%M:%S')} WIB**")
if st.button("🔄 Paksa Ambil Data Baru (Clear Cache)"):
    st.cache_data.clear()
    
# --- 5. INTERFACE PANEL KONTROL & SIDEBAR ---
st.markdown("<h1 class='main-title'>⚡ Scalper Radar Pro (Sinyal Siap Buy & Target TP/SL)</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Filter Validasi Pasar")
    only_ready_to_buy = st.checkbox("🎯 Hanya Tampilkan Sinyal SIAP BUY", value=False)
    saham_pilihan = st.multiselect("Pilih Emiten:", options=master_tickers_clean, default=["BBCA", "BBRI", "TLKM", "MDKA"])

if len(saham_pilihan) > 0:
    df_scalp = run_scalper_scanner(saham_pilihan)
    if not df_scalp.empty:
        if only_ready_to_buy:
            df_scalp = df_scalp[df_scalp["Est. Arah"].str.contains("STRONG UP|UP MOMENTUM")]
        
        df_scalp = df_scalp.sort_values(by="Change %", ascending=False)
        
        # Styling
        def style_scalper(row):
            styles = [''] * len(row)
            if "STRONG UP" in str(row['Est. Arah']):
                styles[row.index.get_loc('Est. Arah')] = 'background-color: #047857; color: white; font-weight: bold;'
            return styles

        st.dataframe(df_scalp.style.apply(style_scalper, axis=1), use_container_width=True)
