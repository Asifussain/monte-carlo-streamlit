import streamlit as st
import numpy as np
from scipy.stats import norm
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="QuantEdge — Risk Engine",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── FONTS ────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ─── GLOBAL CSS  (flex/grid defined as CSS classes, NOT inline styles) ────────
st.markdown("""
<style>
/* ── Tokens ─────────────────────────────────────────── */
:root{
  --bg:#080c10; --bg2:#0d1117; --card:#0f1923;
  --green:#00ff87; --red:#ff3b5c; --blue:#00b4d8;
  --gold:#f0b429; --purple:#a855f7;
  --t1:#e8f4f8; --t2:#7a9ab0; --t3:#3d5c70;
  --bdr:#1a2e3d; --bdr2:#1e3a4d;
  --mono:'Space Mono','Courier New',monospace;
  --data:'DM Mono','Courier New',monospace;
  --display:'Syne','Trebuchet MS',Arial,sans-serif;
}
/* ── Base ─────────────────────────────────────────────── */
html,body,.stApp{background-color:var(--bg)!important;font-family:var(--data)!important;color:var(--t1)!important;}
.stApp::before{content:'';position:fixed;inset:0;
  background-image:linear-gradient(rgba(0,180,216,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,180,216,.04) 1px,transparent 1px);
  background-size:40px 40px;pointer-events:none;z-index:0;}
/* ── Sidebar ──────────────────────────────────────────── */
section[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--bdr)!important;}
section[data-testid="stSidebar"] *{font-family:var(--data)!important;}
section[data-testid="stSidebar"] label{color:var(--t2)!important;font-size:11px!important;letter-spacing:.08em!important;text-transform:uppercase!important;}
/* ── Inputs ───────────────────────────────────────────── */
input[type="text"],input[type="number"]{background:var(--card)!important;border:1px solid var(--bdr2)!important;border-radius:4px!important;color:var(--green)!important;font-family:var(--mono)!important;font-size:13px!important;}
input:focus{border-color:var(--blue)!important;box-shadow:0 0 0 2px rgba(0,180,216,.15)!important;}
/* ── Select ───────────────────────────────────────────── */
div[data-baseweb="select"],div[data-baseweb="select"] *{background:var(--card)!important;color:var(--t1)!important;font-family:var(--data)!important;}
/* ── Buttons ──────────────────────────────────────────── */
.stButton>button{background:transparent!important;border:1px solid var(--green)!important;color:var(--green)!important;font-family:var(--mono)!important;font-size:12px!important;letter-spacing:.1em!important;text-transform:uppercase!important;border-radius:3px!important;padding:10px 20px!important;transition:all .2s!important;}
.stButton>button:hover{background:rgba(0,255,135,.08)!important;box-shadow:0 0 20px rgba(0,255,135,.2)!important;transform:translateY(-1px)!important;}
.stDownloadButton>button{background:transparent!important;border:1px solid var(--blue)!important;color:var(--blue)!important;font-family:var(--mono)!important;font-size:11px!important;letter-spacing:.1em!important;text-transform:uppercase!important;border-radius:3px!important;}
.stDownloadButton>button:hover{background:rgba(0,180,216,.08)!important;}
/* ── Metrics ──────────────────────────────────────────── */
div[data-testid="stMetricValue"]{font-family:var(--mono)!important;font-size:22px!important;font-weight:700!important;color:var(--green)!important;}
div[data-testid="stMetricLabel"]{font-family:var(--data)!important;font-size:10px!important;color:var(--t2)!important;letter-spacing:.1em!important;text-transform:uppercase!important;}
div[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--bdr)!important;border-radius:6px!important;padding:16px!important;}
/* ── Alerts ───────────────────────────────────────────── */
div[data-testid="stInfo"]{background:rgba(0,180,216,.05)!important;border:1px solid rgba(0,180,216,.2)!important;border-radius:4px!important;}
div[data-testid="stSuccess"]{background:rgba(0,255,135,.05)!important;border:1px solid rgba(0,255,135,.2)!important;}
div[data-testid="stError"]{background:rgba(255,59,92,.05)!important;border:1px solid rgba(255,59,92,.2)!important;}
/* ── Headings ─────────────────────────────────────────── */
h1,h2,h3{font-family:var(--display)!important;}
/* ── Animations ───────────────────────────────────────── */
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
/* ─────────────────────────────────────────────────────── */
/* ALL layout classes (flex/grid) defined here so Streamlit */
/* does NOT strip them from inline styles                   */
/* ─────────────────────────────────────────────────────── */
.qe-header{padding:32px 0 24px;border-bottom:1px solid var(--bdr);margin-bottom:32px;}
.qe-logo-row{display:flex;align-items:center;gap:16px;margin-bottom:12px;}
.qe-title{font-family:var(--display);font-size:32px;font-weight:800;color:var(--t1);letter-spacing:-.02em;line-height:1;}
.qe-sub{font-family:var(--mono);font-size:10px;color:var(--t3);letter-spacing:.25em;text-transform:uppercase;margin-top:2px;}
.qe-live{margin-left:auto;display:flex;align-items:center;gap:8px;}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green);animation:pulse 2s infinite;display:inline-block;}
.qe-live-label{font-family:var(--mono);font-size:10px;color:var(--green);letter-spacing:.1em;}
.qe-stats-bar{display:flex;gap:32px;margin-top:16px;}
.qe-stats-bar span{font-family:var(--mono);font-size:10px;color:var(--t3);letter-spacing:.1em;}
.qe-stats-bar b{color:var(--t2);}
.sb-header{padding:16px 0 20px;border-bottom:1px solid var(--bdr);margin-bottom:20px;}
.sb-title-row{display:flex;align-items:center;gap:10px;margin-bottom:4px;}
.sb-section{display:flex;align-items:center;gap:8px;margin:16px 0 12px;padding-top:12px;border-top:1px solid var(--bdr);}
.sb-section span{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;}
.section-header{display:flex;align-items:center;gap:10px;margin:32px 0 16px;}
.section-header span{font-family:var(--mono);font-size:11px;letter-spacing:.15em;text-transform:uppercase;}
.stat-card{background:var(--card);border:1px solid var(--bdr);border-radius:6px;padding:18px;height:100%;}
.stat-label{font-family:var(--mono);font-size:9px;color:var(--t3);letter-spacing:.15em;text-transform:uppercase;margin-bottom:8px;}
.stat-value{font-family:var(--mono);font-size:24px;font-weight:700;margin-bottom:6px;}
.stat-sub{font-family:var(--mono);font-size:9px;color:var(--t3);}
.sum-table{background:var(--card);border:1px solid var(--bdr);border-radius:6px;padding:20px;}
.sum-table table{width:100%;font-family:var(--mono);font-size:11px;border-collapse:collapse;}
.sum-table td{padding:5px 0;}
.sum-head{font-family:var(--mono);font-size:9px;color:var(--t3);letter-spacing:.15em;text-transform:uppercase;margin-bottom:14px;border-bottom:1px solid var(--bdr);padding-bottom:8px;}
.qe-footer{display:flex;justify-content:space-between;align-items:center;margin-top:60px;padding:24px 0;border-top:1px solid var(--bdr);}
.qe-footer-l{display:flex;align-items:center;gap:12px;font-family:var(--mono);font-size:10px;color:var(--t3);letter-spacing:.1em;}
.qe-footer-r{font-family:var(--mono);font-size:10px;color:var(--bdr);}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="qe-header">
  <div class="qe-logo-row">
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
      <polygon points="24,3 43,13.5 43,34.5 24,45 5,34.5 5,13.5" fill="none" stroke="#00ff87" stroke-width="1.5"/>
      <polygon points="24,9 38,17 38,33 24,41 10,33 10,17" fill="none" stroke="#00ff87" stroke-width="0.5" opacity="0.4"/>
      <line x1="18" y1="20" x2="18" y2="32" stroke="#00ff87" stroke-width="1.5"/>
      <rect x="15.5" y="22" width="5" height="7" fill="#00ff87" rx="0.5"/>
      <line x1="24" y1="16" x2="24" y2="30" stroke="#ff3b5c" stroke-width="1.5"/>
      <rect x="21.5" y="19" width="5" height="8" fill="#ff3b5c" rx="0.5"/>
      <line x1="30" y1="18" x2="30" y2="29" stroke="#00ff87" stroke-width="1.5"/>
      <rect x="27.5" y="21" width="5" height="6" fill="#00ff87" rx="0.5"/>
    </svg>
    <div>
      <div class="qe-title">QUANT<span style="color:#00ff87">EDGE</span></div>
      <div class="qe-sub">Monte Carlo Risk Engine // v2.4.1</div>
    </div>
    <div class="qe-live">
      <div class="live-dot"></div>
      <span class="qe-live-label">LIVE FEED</span>
      <svg width="120" height="24" viewBox="0 0 120 24" fill="none" style="margin-left:20px;opacity:.5;">
        <polyline points="0,18 15,14 25,16 35,10 48,12 58,6 70,9 80,4 95,7 110,3 120,5" fill="none" stroke="#00ff87" stroke-width="1.5"/>
        <circle cx="120" cy="5" r="2" fill="#00ff87"/>
      </svg>
    </div>
  </div>
  <div class="qe-stats-bar">
    <span><b>ENGINE</b>&nbsp;&nbsp;Black-Scholes GBM</span>
    <span><b>METHOD</b>&nbsp;&nbsp;Naive MC + Importance Sampling</span>
    <span><b>RISK</b>&nbsp;&nbsp;VaR / CVaR / Black Swan</span>
    <span><b>DATA</b>&nbsp;&nbsp;Yahoo Finance Real-Time</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-header">
      <div class="sb-title-row">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <rect x="1" y="2" width="14" height="12" rx="2" stroke="#00b4d8" stroke-width="1.2"/>
          <polyline points="4,6 7,8 4,10" stroke="#00ff87" stroke-width="1.2" stroke-linecap="round"/>
          <line x1="8.5" y1="10" x2="12" y2="10" stroke="#00ff87" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        <span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:#e8f4f8;letter-spacing:.1em;text-transform:uppercase;">Control Panel</span>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:9px;color:#3d5c70;letter-spacing:.15em;">CONFIGURE SIMULATION PARAMETERS</div>
    </div>
    <div class="sb-section">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <polyline points="1,10 4,6 7,8 10,3 13,5" stroke="#f0b429" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="13" cy="5" r="1.5" fill="#f0b429"/>
      </svg>
      <span style="color:#f0b429;">Asset Selection</span>
    </div>
    """, unsafe_allow_html=True)

    ticker      = st.text_input("Ticker Symbol", value="AAPL", placeholder="AAPL / TSLA / SPY")
    data_period = st.selectbox("Data Window", ["1mo","3mo","6mo","1y","2y","5y"], index=3)

    if st.button("⬡  FETCH MARKET DATA", use_container_width=True):
        with st.spinner("Connecting to market feed..."):
            try:
                stock = yf.Ticker(ticker)
                hist  = stock.history(period=data_period)
                hist["Log Returns"] = np.log(hist["Close"] / hist["Close"].shift(1))
                dr = hist["Log Returns"].dropna()
                st.session_state.update({
                    "sigma": dr.std()*np.sqrt(252),
                    "S0": hist["Close"].iloc[-1],
                    "hist": hist, "ticker": ticker,
                    "skewness": dr.skew(), "kurtosis": dr.kurtosis(),
                    "data_fetched": True
                })
                st.success(f"✓ {ticker} data loaded")
            except Exception as e:
                st.error(f"Feed error: {e}")

    if "sigma" not in st.session_state:
        st.session_state.update({"sigma": 0.2, "S0": 100.0})

    st.markdown("""
    <div class="sb-section">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <circle cx="7" cy="7" r="5.5" stroke="#00b4d8" stroke-width="1.2"/>
        <circle cx="7" cy="7" r="2" fill="#00b4d8"/>
        <line x1="7" y1="1" x2="7" y2="2.5" stroke="#00b4d8" stroke-width="1.2"/>
        <line x1="7" y1="11.5" x2="7" y2="13" stroke="#00b4d8" stroke-width="1.2"/>
        <line x1="1" y1="7" x2="2.5" y2="7" stroke="#00b4d8" stroke-width="1.2"/>
        <line x1="11.5" y1="7" x2="13" y2="7" stroke="#00b4d8" stroke-width="1.2"/>
      </svg>
      <span style="color:#00b4d8;">Sim Parameters</span>
    </div>
    """, unsafe_allow_html=True)

    S0        = st.number_input("Spot Price ($)",    value=float(st.session_state["S0"]),    format="%.2f")
    sigma     = st.number_input("Annual Volatility σ", value=float(st.session_state["sigma"]), format="%.4f")
    crash_pct = st.slider("Crash Threshold (%)", 50, 95, 70)
    K         = S0 * (crash_pct / 100)
    T         = st.slider("Time Horizon (Years)", 0.25, 5.0, 1.0, 0.25)
    r         = st.number_input("Risk-Free Rate",  value=0.05, format="%.4f")
    N_sims    = st.select_slider("Simulations (N)", options=[500,1000,2000,5000,10000,20000], value=5000)

    st.markdown("""
    <div class="sb-section">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <rect x="1" y="3" width="12" height="9" rx="1.5" stroke="#a855f7" stroke-width="1.2"/>
        <line x1="4" y1="6" x2="4" y2="9" stroke="#a855f7" stroke-width="1.2" stroke-linecap="round"/>
        <line x1="7" y1="5" x2="7" y2="9" stroke="#a855f7" stroke-width="1.2" stroke-linecap="round"/>
        <line x1="10" y1="7" x2="10" y2="9" stroke="#a855f7" stroke-width="1.2" stroke-linecap="round"/>
      </svg>
      <span style="color:#a855f7;">Display Options</span>
    </div>
    """, unsafe_allow_html=True)

    show_confidence = st.checkbox("95% Confidence Bands", value=True)
    path_count      = st.slider("Path Count", 10, 200, 50)

    if st.session_state.get("data_fetched"):
        sk       = st.session_state.get("skewness", 0)
        sk_color = "#ff3b5c" if sk < 0 else "#00ff87"
        st.markdown(f"""
        <div style="margin-top:20px;padding:14px;background:#0f1923;border:1px solid #1a2e3d;border-radius:6px;border-left:2px solid #f0b429;">
          <div style="font-family:'Space Mono',monospace;font-size:9px;color:#f0b429;letter-spacing:.15em;text-transform:uppercase;margin-bottom:10px;">
            ◈ {st.session_state.get('ticker', ticker)} — Live Stats
          </div>
          <table style="width:100%;font-family:'Space Mono',monospace;font-size:11px;color:#7a9ab0;border-collapse:collapse;">
            <tr><td>Volatility</td><td style="text-align:right;color:#e8f4f8;">{sigma*100:.2f}%</td></tr>
            <tr><td>Skewness</td> <td style="text-align:right;color:{sk_color};">{sk:.3f}</td></tr>
            <tr><td>Kurtosis</td> <td style="text-align:right;color:#00b4d8;">{st.session_state.get('kurtosis',0):.3f}</td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

# ─── FUNCTIONS ────────────────────────────────────────────────────────────────
def naive_mc(S0, K, T, r, sigma, N):
    Z  = np.random.normal(0, 1, N)
    ST = S0 * np.exp((r-.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    p  = (ST < K).astype(float)
    return np.mean(p), np.std(p)/np.sqrt(N), ST, p

def is_mc(S0, K, T, r, sigma, N):
    sb = (np.log(K/S0)-(r-.5*sigma**2)*T)/(sigma*np.sqrt(T))
    mu = sb-.5
    Z  = np.random.normal(mu, 1, N)
    ST = S0*np.exp((r-.5*sigma**2)*T+sigma*np.sqrt(T)*Z)
    w  = np.exp(-mu*Z+.5*mu**2)
    wp = (ST<K).astype(float)*w
    return np.mean(wp), np.std(wp)/np.sqrt(N), ST, wp

def var_cvar(ret, c=.95):
    v = np.percentile(ret,(1-c)*100)
    return v, ret[ret<=v].mean()

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────
PT = dict(
    template="plotly_dark",
    paper_bgcolor="#0f1923", plot_bgcolor="#080c10",
    font=dict(family="Space Mono,monospace", color="#7a9ab0", size=11),
    xaxis=dict(gridcolor="#1a2e3d", linecolor="#1a2e3d", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1a2e3d", linecolor="#1a2e3d", tickfont=dict(size=10)),
    title_font=dict(family="Syne,sans-serif", size=14, color="#e8f4f8"),
    legend=dict(bgcolor="rgba(13,17,23,.8)", bordercolor="#1a2e3d", borderwidth=1)
)

# ─── RUN BUTTON ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:8px;">
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="vertical-align:middle;margin-right:8px;">
    <polygon points="4,2 16,9 4,16" fill="#00ff87"/>
  </svg>
  <span style="font-family:'Space Mono',monospace;font-size:11px;color:#3d5c70;letter-spacing:.1em;">EXECUTE SIMULATION ENGINE</span>
</div>
""", unsafe_allow_html=True)

if st.button("▶  RUN ADVANCED SIMULATION", use_container_width=True):
    with st.spinner("Executing Monte Carlo paths..."):
        np_p,np_se,np_ST,np_tr = naive_mc(S0,K,T,r,sigma,N_sims)
        is_p,is_se,is_ST,is_tr = is_mc(S0,K,T,r,sigma,N_sims)
        d2        = (np.log(S0/K)+(r-.5*sigma**2)*T)/(sigma*np.sqrt(T))
        true_prob = norm.cdf(-d2)
        np_ret    = (np_ST-S0)/S0
        is_ret    = (is_ST-S0)/S0
        v95,cv95  = var_cvar(np_ret,.95)
        v99,cv99  = var_cvar(np_ret,.99)
        vr        = (np_se**2/is_se**2) if is_se>0 else 0
        err_n     = abs(np_p-true_prob)/true_prob*100 if true_prob else 0
        err_i     = abs(is_p-true_prob)/true_prob*100 if true_prob else 0

    # helper: section header label
    def section(svg, label, color):
        st.markdown(f'<div class="section-header">{svg}<span style="color:{color};">{label}</span></div>',
                    unsafe_allow_html=True)

    # ═══ RISK OVERVIEW ═══════════════════════════════════════════════════════
    section("""<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M8 1L15 13H1L8 1Z" stroke="#f0b429" stroke-width="1.2" fill="none"/>
      <line x1="8" y1="6" x2="8" y2="9" stroke="#f0b429" stroke-width="1.2" stroke-linecap="round"/>
      <circle cx="8" cy="11" r=".6" fill="#f0b429"/>
    </svg>""", "Risk Overview", "#f0b429")

    # 4 stat cards — each in its own st.column
    c1,c2,c3,c4 = st.columns(4)
    def card(col, label, value, sub, clr):
        col.markdown(f"""
        <div class="stat-card" style="border-top:2px solid {clr};">
          <div class="stat-label">{label}</div>
          <div class="stat-value" style="color:{clr};">{value}</div>
          <div class="stat-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    card(c1,"Analytical P(crash)",f"{true_prob:.6f}","Black-Scholes Closed Form","#00ff87")
    card(c2,"Naive MC Estimate",  f"{np_p:.6f}",    f"±{np_se:.6f} | err {err_n:.2f}%","#f0b429")
    card(c3,"Importance Sampling",f"{is_p:.6f}",    f"±{is_se:.6f} | err {err_i:.2f}%","#00b4d8")
    card(c4,"Variance Reduction", f"{vr:.2f}×",     "IS Efficiency Gain","#a855f7")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # VaR / CVaR native Streamlit metrics
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("VaR 95%",  f"{v95*100:.2f}%",  delta=f"${v95*S0:.2f}",  delta_color="inverse")
    m2.metric("CVaR 95%", f"{cv95*100:.2f}%", delta=f"${cv95*S0:.2f}", delta_color="inverse")
    m3.metric("VaR 99%",  f"{v99*100:.2f}%",  delta=f"${v99*S0:.2f}",  delta_color="inverse")
    m4.metric("CVaR 99%", f"{cv99*100:.2f}%", delta=f"${cv99*S0:.2f}", delta_color="inverse")

    # ═══ CONVERGENCE ══════════════════════════════════════════════════════════
    section("""<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <polyline points="1,13 4,8 7,10 10,4 13,6 15,3" stroke="#00b4d8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>""", "Convergence Analysis", "#00b4d8")

    nc = np.cumsum(np_tr)/np.arange(1,N_sims+1)
    ic = np.cumsum(is_tr)/np.arange(1,N_sims+1)
    fc = go.Figure()
    fc.add_trace(go.Scatter(y=nc, mode="lines", name="Naive MC",          line=dict(color="#f0b429",width=1.5)))
    fc.add_trace(go.Scatter(y=ic, mode="lines", name="Importance Sampling",line=dict(color="#00b4d8",width=1.5)))
    fc.add_trace(go.Scatter(y=[true_prob]*N_sims, mode="lines", name="Analytical Truth",line=dict(color="#00ff87",width=2,dash="dot")))
    if show_confidence:
        ns = np.array([np.std(np_tr[:i+1])/np.sqrt(i+1) for i in range(N_sims)])
        fc.add_trace(go.Scatter(y=nc+1.96*ns, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fc.add_trace(go.Scatter(y=nc-1.96*ns, mode="lines", line=dict(width=0),
            fillcolor="rgba(240,180,41,.08)", fill="tonexty", name="95% CI (Naive)", hoverinfo="skip"))
    fc.update_layout(height=420, title="Probability Estimate Convergence",
        xaxis_title="Iterations", yaxis_title="P(crash)", hovermode="x unified", **PT)
    st.plotly_chart(fc, use_container_width=True)

    # ═══ DISTRIBUTIONS ════════════════════════════════════════════════════════
    section("""<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M1 13 Q4 2,8 2 Q12 2,15 13" stroke="#a855f7" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      <line x1="8" y1="2" x2="8" y2="13" stroke="#a855f7" stroke-width=".8" stroke-dasharray="2,2"/>
    </svg>""", "Distribution Analysis", "#a855f7")

    dc1,dc2 = st.columns(2)
    with dc1:
        fd = go.Figure()
        fd.add_trace(go.Histogram(x=np_ST, name="Naive MC", opacity=.6,
            marker_color="#f0b429", nbinsx=60, histnorm="probability density"))
        fd.add_trace(go.Histogram(x=is_ST, name="Importance Sampling", opacity=.6,
            marker_color="#00b4d8", nbinsx=60, histnorm="probability density"))
        fd.add_vline(x=K, line_dash="dash", line_color="#ff3b5c",
            annotation_text=f"K={K:.0f}", annotation_font_color="#ff3b5c", annotation_position="top right")
        fd.update_layout(height=380, title="Terminal Price Distributions",
            xaxis_title="Price ($)", yaxis_title="Density", barmode="overlay", **PT)
        st.plotly_chart(fd, use_container_width=True)
    with dc2:
        fr = go.Figure()
        fr.add_trace(go.Histogram(x=np_ret*100, name="Returns", opacity=.8,
            marker_color="#00ff87", nbinsx=60, histnorm="probability density"))
        fr.add_vline(x=v95*100, line_dash="dash", line_color="#f0b429",
            annotation_text="VaR95", annotation_font_color="#f0b429")
        fr.add_vline(x=v99*100, line_dash="dash", line_color="#ff3b5c",
            annotation_text="VaR99", annotation_font_color="#ff3b5c")
        fr.update_layout(height=380, title="Returns Distribution + VaR Thresholds",
            xaxis_title="Return (%)", yaxis_title="Density", **PT)
        st.plotly_chart(fr, use_container_width=True)

    # ═══ PATH SIMULATION ══════════════════════════════════════════════════════
    section("""<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M1 12 C3 8,5 10,7 7 C9 4,11 9,15 5" stroke="#00ff87" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      <path d="M1 12 C4 9,6 11,8 8 C10 5,12 10,15 8" stroke="#f0b429" stroke-width="1" fill="none" stroke-linecap="round" opacity=".6"/>
    </svg>""", "Stochastic Path Simulation", "#00ff87")

    steps = int(252*T);  tg = np.linspace(0,T,steps+1)
    Zp    = np.random.normal(0,1,(path_count,steps))
    Wt    = np.cumsum(np.hstack([np.zeros((path_count,1)),Zp]),axis=1)*np.sqrt(T/252)
    Sn    = S0*np.exp((r-.5*sigma**2)*tg+sigma*Wt)
    mu_is = (np.log(K/S0)-(r-.5*sigma**2)*T)/(sigma*np.sqrt(T))-.5
    Zpb   = np.random.normal(0,1,(path_count,steps))+mu_is/np.sqrt(T)*np.sqrt(T/252)
    Wtb   = np.cumsum(np.hstack([np.zeros((path_count,1)),Zpb]),axis=1)*np.sqrt(T/252)
    Sb    = S0*np.exp((r-.5*sigma**2)*tg+sigma*Wtb)

    fp = go.Figure()
    for i in range(path_count):
        fp.add_trace(go.Scatter(x=tg,y=Sn[i],mode="lines",
            line=dict(color="rgba(0,180,216,.18)",width=1),showlegend=False,hoverinfo="skip"))
    for i in range(path_count):
        fp.add_trace(go.Scatter(x=tg,y=Sb[i],mode="lines",
            line=dict(color="rgba(240,180,41,.18)",width=1),showlegend=False,hoverinfo="skip"))
    fp.add_trace(go.Scatter(x=tg,y=[K]*len(tg),mode="lines",
        name=f"Crash Level ${K:.0f}",line=dict(color="#ff3b5c",width=2,dash="dash")))
    fp.add_trace(go.Scatter(x=[None],y=[None],mode="lines",
        line=dict(color="rgba(0,180,216,.7)",width=2),name="Naive Paths (GBM)"))
    fp.add_trace(go.Scatter(x=[None],y=[None],mode="lines",
        line=dict(color="rgba(240,180,41,.7)",width=2),name="IS Paths (Stress-Biased)"))
    fp.update_layout(height=550,title=f"GBM Price Paths — N={path_count} simulations",
        xaxis_title="Time (Years)",yaxis_title="Price ($)",**PT)
    st.plotly_chart(fp, use_container_width=True)

    # ═══ HISTORICAL DATA ══════════════════════════════════════════════════════
    if "hist" in st.session_state:
        section("""<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <rect x="2" y="4" width="3" height="9" fill="#00ff87" rx=".5"/>
          <rect x="6.5" y="2" width="3" height="11" fill="#ff3b5c" rx=".5"/>
          <rect x="11" y="5" width="3" height="8" fill="#00ff87" rx=".5"/>
          <line x1="3.5" y1="2" x2="3.5" y2="4" stroke="#00ff87" stroke-width="1"/>
          <line x1="3.5" y1="13" x2="3.5" y2="15" stroke="#00ff87" stroke-width="1"/>
          <line x1="8" y1="1" x2="8" y2="2" stroke="#ff3b5c" stroke-width="1"/>
          <line x1="8" y1="13" x2="8" y2="15" stroke="#ff3b5c" stroke-width="1"/>
        </svg>""", "Historical Market Data", "#e8f4f8")

        hc1,hc2 = st.columns(2)
        hd = st.session_state["hist"]
        with hc1:
            fh = go.Figure()
            fh.add_trace(go.Candlestick(
                x=hd.index,open=hd["Open"],high=hd["High"],low=hd["Low"],close=hd["Close"],name="OHLC",
                increasing_line_color="#00ff87",decreasing_line_color="#ff3b5c",
                increasing_fillcolor="rgba(0,255,135,.3)",decreasing_fillcolor="rgba(255,59,92,.3)"
            ))
            fh.update_layout(height=400,title=f"{ticker} — OHLC Candlestick",xaxis_rangeslider_visible=False,**PT)
            st.plotly_chart(fh, use_container_width=True)
        with hc2:
            rv = hd["Log Returns"].rolling(30).std()*np.sqrt(252)*100
            fv = go.Figure()
            fv.add_trace(go.Scatter(x=hd.index,y=rv,mode="lines",fill="tozeroy",
                line=dict(color="#00b4d8",width=1.5),fillcolor="rgba(0,180,216,.06)",name="30D Rolling Vol"))
            fv.add_hline(y=sigma*100,line_dash="dot",line_color="#f0b429",
                annotation_text=f"σ={sigma*100:.1f}%",annotation_font_color="#f0b429")
            fv.update_layout(height=400,title="Realized Volatility (30D Rolling, Annualized)",
                xaxis_title="Date",yaxis_title="Volatility (%)",**PT)
            st.plotly_chart(fv, use_container_width=True)

    # ═══ SUMMARY ══════════════════════════════════════════════════════════════
    section("""<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="1" y="1" width="14" height="14" rx="2" stroke="#3d5c70" stroke-width="1"/>
      <line x1="1" y1="5" x2="15" y2="5" stroke="#1a2e3d" stroke-width="1"/>
      <line x1="1" y1="9" x2="15" y2="9" stroke="#1a2e3d" stroke-width="1"/>
      <line x1="6" y1="5" x2="6" y2="15" stroke="#1a2e3d" stroke-width="1"/>
    </svg>""", "Simulation Summary", "#7a9ab0")

    rc   = "#ff3b5c" if true_prob>.20 else ("#f0b429" if true_prob>.10 else "#00ff87")
    rl   = "HIGH" if true_prob>.20 else ("MODERATE" if true_prob>.10 else "LOW")
    rgba = "255,59,92" if true_prob>.20 else ("240,180,41" if true_prob>.10 else "0,255,135")

    sc1,sc2 = st.columns(2)
    with sc1:
        st.markdown(f"""
        <div class="sum-table">
          <div class="sum-head">Probability Results</div>
          <table>
            <tr><td style="color:#7a9ab0;">Ticker</td>     <td style="color:#e8f4f8;text-align:right;">{ticker if 'ticker' in st.session_state else '—'}</td></tr>
            <tr><td style="color:#7a9ab0;">Spot Price</td> <td style="color:#e8f4f8;text-align:right;">${S0:.2f}</td></tr>
            <tr><td style="color:#7a9ab0;">Crash Level</td><td style="color:#ff3b5c;text-align:right;">${K:.2f} ({crash_pct}%)</td></tr>
            <tr><td style="color:#7a9ab0;">Horizon</td>    <td style="color:#e8f4f8;text-align:right;">{T}Y</td></tr>
            <tr><td style="color:#7a9ab0;">Simulations</td><td style="color:#e8f4f8;text-align:right;">{N_sims:,}</td></tr>
            <tr><td style="color:#7a9ab0;padding-top:8px;border-top:1px solid #1a2e3d;">Analytical P</td>
                <td style="color:#00ff87;text-align:right;font-weight:700;padding-top:8px;border-top:1px solid #1a2e3d;">{true_prob:.6f}</td></tr>
            <tr><td style="color:#7a9ab0;">Naive MC</td>   <td style="color:#f0b429;text-align:right;">{np_p:.6f} ±{np_se:.6f}</td></tr>
            <tr><td style="color:#7a9ab0;">IS Estimate</td><td style="color:#00b4d8;text-align:right;">{is_p:.6f} ±{is_se:.6f}</td></tr>
            <tr><td style="color:#7a9ab0;">Var Reduction</td><td style="color:#a855f7;text-align:right;">{vr:.2f}×</td></tr>
          </table>
        </div>""", unsafe_allow_html=True)

    with sc2:
        skew_row = ""
        kurt_row = ""
        if "skewness" in st.session_state:
            sk2 = st.session_state["skewness"]
            sc2_color = "#ff3b5c" if sk2<0 else "#00ff87"
            skew_row = f'<tr><td style="color:#7a9ab0;">Skewness</td><td style="color:{sc2_color};text-align:right;">{sk2:.3f}</td></tr>'
            kurt_row = f'<tr><td style="color:#7a9ab0;">Kurtosis</td><td style="color:#00b4d8;text-align:right;">{st.session_state.get("kurtosis",0):.3f}</td></tr>'

        st.markdown(f"""
        <div class="sum-table">
          <div class="sum-head">Risk Metrics</div>
          <table>
            <tr><td style="color:#7a9ab0;">VaR (95%)</td> <td style="color:#f0b429;text-align:right;">{v95*100:.2f}% / ${abs(v95*S0):.2f}</td></tr>
            <tr><td style="color:#7a9ab0;">CVaR (95%)</td><td style="color:#ff3b5c;text-align:right;">{cv95*100:.2f}% / ${abs(cv95*S0):.2f}</td></tr>
            <tr><td style="color:#7a9ab0;">VaR (99%)</td> <td style="color:#f0b429;text-align:right;">{v99*100:.2f}% / ${abs(v99*S0):.2f}</td></tr>
            <tr><td style="color:#7a9ab0;">CVaR (99%)</td><td style="color:#ff3b5c;text-align:right;">{cv99*100:.2f}% / ${abs(cv99*S0):.2f}</td></tr>
            <tr><td style="color:#7a9ab0;padding-top:8px;border-top:1px solid #1a2e3d;">Volatility σ</td>
                <td style="color:#e8f4f8;text-align:right;padding-top:8px;border-top:1px solid #1a2e3d;">{sigma*100:.2f}%</td></tr>
            <tr><td style="color:#7a9ab0;">Risk-Free r</td><td style="color:#e8f4f8;text-align:right;">{r*100:.2f}%</td></tr>
            {skew_row}{kurt_row}
            <tr><td style="color:#7a9ab0;padding-top:8px;border-top:1px solid #1a2e3d;">Risk Level</td>
                <td style="color:{rc};text-align:right;font-weight:700;padding-top:8px;border-top:1px solid #1a2e3d;">{rl}</td></tr>
          </table>
          <div style="margin-top:14px;padding:10px;background:rgba({rgba},.06);border:1px solid rgba({rgba},.2);border-radius:4px;">
            <span style="font-family:'Space Mono',monospace;font-size:10px;color:{rc};">
              P(crash {crash_pct}% | {T}Y) = {true_prob*100:.3f}%
            </span>
          </div>
        </div>""", unsafe_allow_html=True)

    # ═══ EXPORT ═══════════════════════════════════════════════════════════════
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    df_out = pd.DataFrame({
        "Simulation":range(1,N_sims+1),
        "Naive_Price":np_ST,"IS_Price":is_ST,
        "Naive_Returns":np_ret,"IS_Returns":is_ret,
        "Naive_Crash":np_tr,"IS_Crash":is_tr
    })
    st.download_button(
        label="↓  EXPORT SIMULATION DATA  (.CSV)",
        data=df_out.to_csv(index=False),
        file_name=f"quantedge_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="qe-footer">
  <div class="qe-footer-l">
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <polygon points="10,1.5 18,6 18,14 10,18.5 2,14 2,6" fill="none" stroke="#3d5c70" stroke-width="1"/>
      <polygon points="10,5 15,7.5 15,12.5 10,15 5,12.5 5,7.5" fill="none" stroke="#3d5c70" stroke-width=".5"/>
    </svg>
    QUANTEDGE RISK ENGINE // FOR EDUCATIONAL USE ONLY
  </div>
  <div class="qe-footer-r">NOT FINANCIAL ADVICE · POWERED BY STREAMLIT &amp; PLOTLY</div>
</div>
""", unsafe_allow_html=True)