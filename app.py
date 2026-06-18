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
        "WSBP", "WSKT", "WTG",  "WTIA", "YPAS", "YUASA", "YULE", "ZATA", "ZBRA", "ZINC", "ZONE", "PTRO", "BRAM", "IRSX", "WIFI", "KLBV","NCKL","BELI","ULTJ","TMPO", "DSSA","MDKA","RMKO","RMKE"
    ]
    return sorted(list(set([f"{t.strip().upper()}.JK" for t in saham_300_plus])))

# --- 5. FUNGSI DIVIDEN ---
@st.cache_data(ttl=86400)
def get_dividend_data(ticker):
    try:
        formatted_ticker = f"{ticker.upper()}.JK"
        stock = yf.Ticker(formatted_ticker)
        divs = stock.dividends
        if divs.empty:
            return None
        div_df = divs.tail(5).reset_index()
        div_df.columns = ['Tanggal', 'Dividen (Rp)']
        div_df['Tanggal'] = div_df['Tanggal'].dt.strftime('%d-%m-%Y')
        return div_df
    except:
        return None

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

# --- 6. ENGINE ANALISIS ---
def analyze_market_momentum(ticker):
    try:
        formatted_ticker = ticker if ticker.endswith(".JK") else f"{ticker}.JK"
        df = yf.download(formatted_ticker, period="3mo", interval="1d", progress=False)
        df = clean_yf_dataframe(df)
        if df is None or len(df) < 4 or 'Close' not in df.columns: return None
        
        df['EMA9'] = ta.ema(df['Close'], length=9)
        df['EMA20'] = ta.ema(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
        df['STOCHk'] = stoch['STOCHk_14_3_3'] if 'STOCHk_14_3_3' in stoch.columns else 50.0
        df['STOCHd'] = stoch['STOCHd_14_3_3'] if 'STOCHd_14_3_3' in stoch.columns else 50.0
        
        last_price = float(df['Close'].iloc[-1])
        change_pct = ((last_price - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100
        
        p_masuk = max(5.0, min(95.0, 50 + (change_pct * 5) if change_pct >= 0 else 50 - (abs(change_pct) * 5)))
        net_foreign_b = ((last_price * float(df['Volume'].iloc[-1])) / 1_000_000_000) * ((p_masuk - (100-p_masuk))/100) * 0.25
        
        return {
            "Ticker": ticker.replace(".JK", ""),
            "Price": last_price,
            "Net Foreign Avg": round(net_foreign_b / 2, 2),
            "Actionable": "🔥 SUPER BUY" if last_price > df['EMA9'].iloc[-1] else "⏳ Neutral"
        }
    except: return None

def run_mega_scanner(ticker_list):
    results = [analyze_market_momentum(t) for t in ticker_list]
    return pd.DataFrame([r for r in results if r is not None])

# --- 7. UI ---
st.markdown("<h1 class='main-title'>📈 Swing Trading & Scalper Radar</h1>", unsafe_allow_html=True)
saham_pilihan = st.sidebar.multiselect("Pilih Saham:", options=master_tickers_clean, default=["ESIP","ESSA"])

if len(saham_pilihan) > 0:
    df_radar = run_mega_scanner(saham_pilihan)
    st.dataframe(df_radar, use_container_width=True)
    
    # DIVIDEN SECTION
    st.markdown("### 💰 Riwayat Dividen")
    saham_div = st.selectbox("Pilih Saham untuk Cek Dividen:", options=saham_pilihan)
    with st.expander(f"Lihat Data Dividen {saham_div}"):
        div_data = get_dividend_data(saham_div)
        if div_data is not None:
            st.table(div_data)
        else:
            st.write("Data dividen tidak ditemukan.")
