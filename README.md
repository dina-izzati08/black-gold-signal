# Black Gold Signal 
### Brent Crude Oil Price Forecasting Dashboard

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![Prophet](https://img.shields.io/badge/Prophet-1.1-orange)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2-ee4c2c)

> 🔴 **[Live Dashboard → ]:(https://black-gold-signal-ds.streamlit.app/)**

---

## What is this?

A time series forecasting project that models and predicts Brent crude 
oil prices using three approaches — classical statistics (ARIMA), trend 
decomposition (Prophet), and deep learning (LSTM via PyTorch) — deployed 
as a live interactive dashboard with real-time price data.

Built during one of the most volatile oil markets in recent history: 
the 2026 Strait of Hormuz supply shock.

---

## Background

Brent crude and WTI are the world's two primary oil benchmarks — Brent 
serves as the global standard for international trade due to its North 
Sea origin and low transportation costs, while WTI benchmarks the US 
market. Both are classified as light sweet crude, making them the most 
refinery-efficient and commercially valued grades in the world.

OPEC+ is a 23-member alliance controlling over 80% of the world's proven 
oil reserves, deliberately limiting combined output to roughly 40% of 
global production to stabilise prices and prevent oversupply — including 
Malaysia as a member nation through Petronas.

By managing production quotas rather than producing at full capacity, 
OPEC+ maintains spare capacity as a buffer against sudden demand shocks 
and counters competition from US shale producers, who can rapidly scale 
output through hydraulic fracturing.

Oil prices are shaped by six key forces: global supply and demand 
balances, OPEC+ production decisions, geopolitical disruptions in major 
producing regions, US shale output, macroeconomic growth cycles, and 
the strength of the US dollar — since oil is priced in USD, a stronger 
dollar raises the effective cost of oil for the rest of the world.

Malaysia sits directly inside this system as both an OPEC+ member and 
a nation whose federal budget is materially sensitive to Brent price 
fluctuations — making accurate oil price forecasting a question of 
genuine national economic relevance, not just a modelling exercise.

---

## Data Sources

| Source | What it provides | Format |
|--------|-----------------|--------|
| EIA (US Energy Information Administration) | Daily Brent spot prices from 1987–present | CSV |
| Yahoo Finance (yfinance) | Live Brent futures (BZ=F) for real-time updates | API |
| Yahoo Finance (yfinance) | WTI crude (CL=F) for spread analysis | API |
| Yahoo Finance (yfinance) | USD Index (DX-Y.NYB) as external feature | API |

> All prices are in **USD per barrel (bbl)**. The dashboard pulls live 
> data on each page load.

---

## Models Used

| Model | Type | Strength |
|-------|------|----------|
| ARIMA | Classical statistical | Stable, low-volatility periods |
| Prophet | Trend + seasonality decomposition | Long-term trend with uncertainty bands |
| LSTM | Deep learning (PyTorch) | Non-linear patterns, high-volatility regimes |

---

## Key Findings

- LSTM achieved a RMSE of $2.71/bbl vs ARIMA's $10.18 and Prophet's 
  $10.65 — **3.8x more accurate** than classical methods on the test set
- ARIMA defaulted to a random walk (0,1,0) model, forecasting a flat 
  $70/bbl — unable to anticipate the 2026 Hormuz crisis price surge
- Prophet correctly tracked the downward trend through late 2025 but 
  its confidence intervals did not capture the $112/bbl spike in March 2026
- LSTM's 2.47% MAPE demonstrates that deep learning models can track 
  commodity price momentum significantly better than statistical baselines
- The Brent-WTI spread widened from a historical average of $6.10/bbl 
  to $11.90/bbl during the 2026 crisis — a quantifiable signal of 
  geopolitical risk premium in the market
- All three models failed to predict the magnitude of the Hormuz supply 
  shock, confirming that black swan geopolitical events remain beyond 
  the reach of data-driven forecasting

---

## Dashboard Features

- 🟢 Live Brent price updated on every page load
- 📈 Interactive historical chart (2010–present) with annotated events
- 🔮 Forecast view: select model + horizon (30 / 60 / 90 days)
- 📊 Model comparison table (MAE, RMSE, MAPE)
- 🌍 Market context panel explaining current price drivers

---

## Project Structure
```
black-gold-signal/
├── data/                  # Raw CSVs from EIA and yfinance
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_modelling.ipynb
│   └── 04_evaluation.ipynb
├── models/                # Saved model files
├── app.py                 # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## How to Run Locally
```bash
git clone https://github.com/YOURUSERNAME/black-gold-signal.git
cd black-gold-signal
pip install -r requirements.txt
streamlit run app.py
```

---

## What I Learned

Time series forecasting for commodity prices is fundamentally constrained 
by unpredictable geopolitical events — models capture trend and seasonality 
well, but black swan shocks like the 2026 Hormuz crisis expose the ceiling 
of data-driven prediction. LSTM outperformed classical methods during 
volatile periods but required significantly more tuning. The most important 
skill was learning to explain model limitations honestly, not just report 
the best accuracy metric.

---

## Author

**[Irdina Izzati]** 

BSc Computer Science (Data Science) — IIUM 

[GitHub](https://github.com/dina-izzati08)
