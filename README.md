# ADF Stationarity Test + OLS Regression — Bangladesh GDP

This repo runs an **Augmented Dickey-Fuller (ADF)** stationarity test on each variable,
makes any **Non-Stationary** series stationary via **First Difference**, then fits an
**OLS regression** with GDP as the dependent variable — for **two datasets** so the
results can be compared and the better dataset chosen.

## How to run

```bash
pip install pandas statsmodels openpyxl
python adf_regression.py
```

## Method

1. **ADF test** on every variable at level. H₀ = unit root (Non-Stationary); reject when **p < 0.05**.
2. If a series is **Non-Stationary**, take its **First Difference** and use that (re-tested).
3. **OLS regression**: `GDP = const + Σ(independent variables)` using the stationary version of each series.
4. Repeat for both datasets and compare fit.

## Datasets

| # | File | Unit | Dependent variable | Years | n |
|---|------|------|--------------------|-------|---|
| 1 | `data/Inflation-1.xlsx` | US$ Billion (levels) | GDP Current (US$ Billion) | 1999–2024 | 25 |
| 2 | `data/Bangladesh_GDPGrowth.xlsx` | % of GDP / growth | GDP Growth Annual (%) | 2000–2024 | 24 |

---

## Dataset 1 — Levels (US$ Billion)

### ADF results

| Variable | ADF p (level) | Decision | Used as | ADF p (after diff) |
|---|---|---|---|---|
| GDP Current (US$ Billion) | 0.9761 | Non-Stationary → diff | 1st Diff (I(1)) | 0.2230 — **still Non-Stationary** ⚠️ |
| Remittance Received (US$ Billion) | 0.9984 | Non-Stationary → diff | 1st Diff (I(1)) | 0.0216 — Stationary |
| Gross Capital Formation (US$ Billion) | 0.9590 | Non-Stationary → diff | 1st Diff (I(1)) | 0.6662 — **still Non-Stationary** ⚠️ |
| FDI Net Inflows (US$ Billion) | 0.4917 | Non-Stationary → diff | 1st Diff (I(1)) | 0.0000 — Stationary |
| Inflation Rate (%) | 0.0001 | Stationary | Level (I(0)) | — |

### OLS regression — Dependent: GDP Current (US$ Billion), n = 25

| Term | coef | std err | t | P>\|t\| |
|---|---|---|---|---|
| const | 0.4172 | 1.797 | 0.232 | 0.819 |
| Remittance Received | 0.6476 | 0.613 | 1.056 | 0.304 |
| **Gross Capital Formation** | **2.5011** | 0.140 | 17.870 | **0.000** ✅ |
| FDI Net Inflows | -1.1464 | 2.137 | -0.536 | 0.598 |
| Inflation Rate (%) | 0.3448 | 0.208 | 1.655 | 0.114 |

- **R² = 0.959 · Adj R² = 0.951 · F p-value = 1.30e-13**
- Only **Gross Capital Formation** is statistically significant.

---

## Dataset 2 — Ratios / Growth (% of GDP)

### ADF results

| Variable | ADF p (level) | Decision | Used as | ADF p (after diff) |
|---|---|---|---|---|
| GDP Growth Annual (%) | 0.0063 | Stationary | Level (I(0)) | — |
| Personal Remittances Received (% GDP) | 0.1211 | Non-Stationary → diff | 1st Diff (I(1)) | 0.0520 — borderline ⚠️ |
| Gross Capital Formation (% GDP) | 0.7972 | Non-Stationary → diff | 1st Diff (I(1)) | 0.0854 — **still Non-Stationary** ⚠️ |
| Inflation Rate (%) | 0.1278 | Non-Stationary → diff | 1st Diff (I(1)) | 0.0000 — Stationary |
| FDI Net Inflows (% GDP) | 0.3282 | Non-Stationary → diff | 1st Diff (I(1)) | 0.5110 — **still Non-Stationary** ⚠️ |

### OLS regression — Dependent: GDP Growth Annual (%), n = 24

| Term | coef | std err | t | P>\|t\| |
|---|---|---|---|---|
| const | 5.7772 | 0.256 | 22.588 | 0.000 |
| Personal Remittances Received (% GDP) | -0.2344 | 0.247 | -0.949 | 0.354 |
| **Gross Capital Formation (% GDP)** | **0.9038** | 0.398 | 2.269 | **0.035** ✅ |
| Inflation Rate (%) | -0.0554 | 0.123 | -0.450 | 0.658 |
| FDI Net Inflows (% GDP) | 0.2704 | 0.696 | 0.388 | 0.702 |

- **R² = 0.318 · Adj R² = 0.174 · F p-value = 0.107**
- Only **Gross Capital Formation** is statistically significant.

---

## Comparison

| Metric | Dataset 1 (Levels) | Dataset 2 (% of GDP) |
|---|---|---|
| Dependent | GDP Current (US$ Billion) | GDP Growth Annual (%) |
| n | 25 | 24 |
| R² | **0.959** | 0.318 |
| Adj R² | **0.951** | 0.174 |
| F p-value | **1.30e-13** | 0.107 |
| Significant vars | Gross Capital Formation | Gross Capital Formation |

## Recommendation

- **By raw fit, Dataset 1 wins by a large margin** (Adj R² 0.95 vs 0.17, and a highly
  significant overall model).

- ⚠️ **Caveat (read before choosing):** In Dataset 1, **GDP (p=0.22)** and
  **Gross Capital Formation (p=0.67)** remain **Non-Stationary even after first
  differencing**. A regression between two non-stationary series is the textbook setup
  for a **spurious regression** — the 0.96 R² is likely inflated, not a real relationship.

- In Dataset 2, the dependent variable **GDP Growth is stationary at level (I(0))**, which
  is econometrically cleaner and more defensible, even though the fit is weaker.

**Bottom line for the dev:**
- Want the strongest-looking fit for a report → **Dataset 1**.
- Want methodologically safe / defensible results → **Dataset 2**.

### Optional next steps
1. Take a **Second Difference** of GDP & Gross Capital Formation in Dataset 1 to remove the
   remaining unit root.
2. Run a **Cointegration test (Engle–Granger)** on the non-stationary pairs — if they are
   cointegrated, the level regression is actually valid (and not spurious).
