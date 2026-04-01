import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Black Gold Signal",
    page_icon="🛢️",
    layout="wide"
)

# ── Colour palette ────────────────────────────────────────
C_GREEN  = '#1D9E75'
C_AMBER  = '#EF9F27'
C_CORAL  = '#D85A30'
C_BLUE   = '#378ADD'
C_PURPLE = '#7F77DD'

# ── Load historical data ──────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    import yfinance as yf
    start = "2010-01-01"
    end   = pd.Timestamp.today().strftime('%Y-%m-%d')

    def download_clean(ticker, col_name):
        df = yf.download(ticker, start=start, end=end,
                        auto_adjust=True, progress=False)
        df = df[['Close']].copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col_name]
        else:
            df.columns = [col_name]
        df.index.name = 'date'
        return df

    brent = download_clean("BZ=F", "brent_price")
    wti   = download_clean("CL=F", "wti_price")
    usd   = download_clean("DX-Y.NYB", "usd_index")

    master = brent.join(wti, how='left').join(usd, how='left')
    master['brent_wti_spread'] = (
        master['brent_price'] - master['wti_price']
    )
    return master.ffill()

# ── Fetch live price ──────────────────────────────────────
@st.cache_data(ttl=300)
def get_live_price():
    try:
        df = yf.download("BZ=F", period="5d", 
                         auto_adjust=True, progress=False)
        price_now  = float(df['Close'].iloc[-1])
        price_prev = float(df['Close'].iloc[-2])
        delta      = price_now - price_prev
        pct        = (delta / price_prev) * 100
        return round(price_now, 2), round(delta, 2), round(pct, 2)
    except:
        return None, None, None

# ── Load saved model forecasts ────────────────────────────
def load_forecasts():
    try:
        arima = pd.read_csv("data/forecast_arima.csv",
                            parse_dates=['date']).set_index('date')
        prophet = pd.read_csv("data/forecast_prophet.csv",
                              parse_dates=['ds']).set_index('ds')
        prophet.index.name = 'date'
        lstm = pd.read_csv("data/forecast_lstm.csv",
                           parse_dates=['date']).set_index('date')
        return arima, prophet, lstm
    except Exception as e:
        st.error(f"Failed to load forecasts: {e}")
        return None, None, None
    
master = load_data()
price_now, delta, pct = get_live_price()
arima_fc, prophet_fc, lstm_fc = load_forecasts()

# ── Header ────────────────────────────────────────────────
st.markdown("## 🛢️ Black Gold Signal")
st.markdown("*Brent Crude Oil Price Forecasting — ARIMA · Prophet · LSTM*")
st.divider()

# ── Live metrics row ──────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    if price_now:
        st.metric("Brent Crude (live)",
                  f"${price_now}/bbl",
                  f"{delta:+.2f} ({pct:+.2f}%)")
    else:
        st.metric("Brent Crude", "Unavailable", "")

with col2:
    pre_2026 = master[master.index.year < 2026]['brent_price']
    st.metric("Pre-2026 Average",
              f"${pre_2026.mean():.2f}/bbl",
              "16-year baseline")

with col3:
    spread = master['brent_wti_spread'].iloc[-1]
    avg_spread = master['brent_wti_spread'].mean()
    st.metric("Brent–WTI Spread",
              f"${spread:.2f}/bbl",
              f"{spread - avg_spread:+.2f} vs avg")

with col4:
    yr2026 = master[master.index.year == 2026]['brent_price']
    st.metric("2026 High",
              f"${yr2026.max():.2f}/bbl",
              "Hormuz crisis peak")

st.divider()

# ── Tab layout ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📈 Price History",
    "🔮 Model Forecasts",
    "📊 Model Comparison"
])

# ── Tab 1: Price History ──────────────────────────────────
with tab1:
    st.subheader("Brent Crude Price History 2010–2026")

    # Date range filter
    col_a, col_b = st.columns(2)
    with col_a:
        start_yr = st.slider("Start year", 2010, 2025, 2010)
    with col_b:
        show_ma = st.checkbox("Show moving averages", value=True)

    filtered = master[master.index.year >= start_yr]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered.index, y=filtered['brent_price'],
        name='Brent price',
        line=dict(color=C_GREEN, width=1),
        hovertemplate='%{x}<br>$%{y:.2f}/bbl<extra></extra>'
    ))

    if show_ma:
        fig.add_trace(go.Scatter(
            x=filtered.index,
            y=filtered['brent_price'].rolling(30).mean(),
            name='30-day MA',
            line=dict(color=C_AMBER, width=1.5, dash='dot'),
            hovertemplate='30d MA: $%{y:.2f}<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=filtered.index,
            y=filtered['brent_price'].rolling(90).mean(),
            name='90-day MA',
            line=dict(color=C_BLUE, width=1.5, dash='dot'),
            hovertemplate='90d MA: $%{y:.2f}<extra></extra>'
        ))

    # Annotate key events
    events = {
        '2014-11-01': 'OPEC price war',
        '2020-04-01': 'COVID collapse',
        '2022-03-01': 'Russia-Ukraine',
        '2026-01-01': 'Hormuz crisis'
    }
    for date, label in events.items():
        ts = pd.Timestamp(date)
        if ts >= pd.Timestamp(f'{start_yr}-01-01'):
            fig.add_shape(
                type='line',
                x0=date, x1=date,
                y0=0, y1=1,
                xref='x', yref='paper',
                line=dict(color=C_CORAL, width=1,
                         dash='dash')
            )
            fig.add_annotation(
                x=date, y=1,
                xref='x', yref='paper',
                text=label,
                showarrow=False,
                font=dict(size=9, color=C_CORAL),
                textangle=-90,
                xanchor='left',
                yanchor='top'
            )

    fig.add_hrect(
        y0=70, y1=85,
        fillcolor=C_BLUE, opacity=0.05,
        annotation_text="Normal range $70–$85",
        annotation_font_size=10
    )

    fig.update_layout(
        height=450,
        xaxis_title='Date',
        yaxis_title='Price (USD/bbl)',
        hovermode='x unified',
        legend=dict(orientation='h', y=1.02),
        margin=dict(t=40, b=40)
    )
    st.plotly_chart(fig, width='stretch')

    # Spread chart
    st.subheader("Brent–WTI Spread")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=filtered.index,
        y=filtered['brent_wti_spread'],
        fill='tozeroy',
        name='Spread',
        line=dict(color=C_GREEN, width=1),
        fillcolor='rgba(29,158,117,0.2)'
    ))
    fig2.add_hline(
        y=master['brent_wti_spread'].mean(),
        line_dash='dash', line_color=C_AMBER,
        annotation_text=f"Avg ${master['brent_wti_spread'].mean():.2f}"
    )
    fig2.update_layout(
        height=250,
        xaxis_title='Date',
        yaxis_title='Spread (USD/bbl)',
        margin=dict(t=20, b=40)
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 2: Model Forecasts ────────────────────────────────
with tab2:
    st.subheader("Model Forecast vs Actual Price")

    if arima_fc is not None:
        model_choice = st.selectbox(
            "Select model",
            ["LSTM (best)", "Prophet", "ARIMA", "All models"]
        )

        # Test period actual
        test_start = '2025-09-27'
        actual_test = master['brent_price'][test_start:]

        fig3 = go.Figure()

        # Actual
        fig3.add_trace(go.Scatter(
            x=actual_test.index, y=actual_test.values,
            name='Actual price',
            line=dict(color=C_CORAL, width=1.5)
        ))

        if model_choice in ["LSTM (best)", "All models"]:
            fig3.add_trace(go.Scatter(
                x=lstm_fc.index, y=lstm_fc['forecast'],
                name='LSTM forecast',
                line=dict(color=C_AMBER, width=1.5, dash='dash')
            ))

        if model_choice in ["Prophet", "All models"]:
            fig3.add_trace(go.Scatter(
                x=prophet_fc.index, y=prophet_fc['yhat'],
                name='Prophet forecast',
                line=dict(color=C_PURPLE, width=1.5, dash='dash')
            ))
            fig3.add_trace(go.Scatter(
                x=prophet_fc.index,
                y=prophet_fc['yhat_upper'],
                fill=None, mode='lines',
                line=dict(color=C_PURPLE, width=0),
                showlegend=False
            ))
            fig3.add_trace(go.Scatter(
                x=prophet_fc.index,
                y=prophet_fc['yhat_lower'],
                fill='tonexty', mode='lines',
                line=dict(color=C_PURPLE, width=0),
                fillcolor='rgba(127,119,221,0.15)',
                name='Prophet 95% CI'
            ))

        if model_choice in ["ARIMA", "All models"]:
            fig3.add_trace(go.Scatter(
                x=arima_fc.index, y=arima_fc['forecast'],
                name='ARIMA forecast',
                line=dict(color=C_BLUE, width=1.5, dash='dash')
            ))

        fig3.update_layout(
            height=450,
            xaxis_title='Date',
            yaxis_title='Price (USD/bbl)',
            hovermode='x unified',
            legend=dict(orientation='h', y=1.02),
            margin=dict(t=40, b=40)
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Forecast data not found. Please run the modelling notebook first to generate forecast CSVs.")

# ── Tab 3: Model Comparison ───────────────────────────────
with tab3:
    st.subheader("Model Performance Comparison")

    results = {
        'ARIMA'  : {'MAE': 7.43,  'RMSE': 10.18, 'MAPE': 10.35},
        'Prophet': {'MAE': 5.43,  'RMSE': 10.65, 'MAPE': 6.72},
        'LSTM'   : {'MAE': 1.80,  'RMSE': 2.71,  'MAPE': 2.47},
    }

    results_df = pd.DataFrame(results).T.reset_index()
    results_df.columns = ['Model', 'MAE (USD/bbl)',
                          'RMSE (USD/bbl)', 'MAPE (%)']

    st.dataframe(
        results_df.style.highlight_min(
            subset=['MAE (USD/bbl)', 'RMSE (USD/bbl)', 'MAPE (%)'],
            color='#E1F5EE'
        ),
        use_container_width=True,
        hide_index=True
    )

    # Bar chart comparison
    fig4 = go.Figure()
    models = list(results.keys())
    colors = [C_BLUE, C_PURPLE, C_AMBER]

    for metric, col in zip(['MAE (USD/bbl)', 'RMSE (USD/bbl)', 'MAPE (%)'],
                           ['MAE', 'RMSE', 'MAPE']):
        fig4.add_trace(go.Bar(
            name=metric,
            x=models,
            y=[results[m][col] for m in models],
            marker_color=colors
        ))

    fig4.update_layout(
        barmode='group',
        height=350,
        xaxis_title='Model',
        yaxis_title='Error',
        title='Error metrics by model — lower is better',
        margin=dict(t=50, b=40)
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    st.subheader("Key findings")
    st.markdown(f"""
    - **LSTM achieved RMSE of 2.71 USD/bbl** — 3.8x better than ARIMA (10.18) and 3.9x better than Prophet (10.65)
    - **ARIMA** defaulted to a random walk, forecasting a flat $70/bbl — 
    unable to anticipate the 2026 Hormuz crisis surge
    - **Prophet** tracked the downward trend well through late 2025 but 
    confidence intervals did not capture the $112/bbl March 2026 spike
    - **All three models** confirmed that black swan geopolitical events 
    remain beyond the reach of purely data-driven forecasting
    - **Brent–WTI spread** widened from historical average of 6.10 to 11.90 
    during the crisis — a quantifiable signal of geopolitical risk premium
    """)

    st.divider()
    st.caption("Data: EIA & Yahoo Finance · Models: ARIMA, Prophet, LSTM (PyTorch) · Built by Dina Izzati")