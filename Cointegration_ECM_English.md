# Cointegration + ECM — Simple Explanation (English)

> **The problem:** In Dataset 1, GDP and Gross Capital Formation were Non-Stationary
> not only at the first difference but **even after the second difference**. Taking more
> differences (over-differencing) damages the data and worsens the results. So we used
> the correct approach: **log transform → Cointegration test → ECM**.

Code to run: `cointegration_ecm.py` — command: `python cointegration_ecm.py`

---

## Why this method? (one line)

Two series can each be Non-Stationary on their own, but if they **move together** (share
a long-run relationship), then a regression between them is **not spurious — it is valid**.
The test for this is the **Cointegration test**. The short-run + long-run dynamics together
are captured by the **ECM (Error Correction Model)**.

---

## Step 1 — Order of integration on logs (ADF)

We took logs of the billion-dollar series (this calms the trend and variance):

| Series | Result | Meaning |
|---|---|---|
| log_GDP Current | **I(1)** | stationary after one difference |
| log_Gross Capital Formation | **I(1)** | stationary after one difference |
| Inflation Rate | I(0) | stationary at level |

➡️ **Key point:** After taking logs, both GDP and Gross Capital Formation became clean
**I(1)** — exactly what the cointegration test needs. (Earlier, even a 2nd difference of
the levels would not make them stationary — the log transform fixed that problem.)

---

## Step 2 — Long-run relationship

`log_GDP = 1.66 + 0.895 × log_GCF + 0.0013 × log_Remittance − 0.014 × log_FDI + 0.0001 × Inflation`

- **R² = 0.9994**
- **Interpretation:** a 1% rise in Gross Capital Formation raises GDP by about **0.90%**
  in the long run. This is the strongest driver.

---

## Step 3 — Cointegration test (the most important step)

We checked whether the residuals of the relationship above are stationary:

| Test | Value | Decision |
|---|---|---|
| ADF p-value on residuals | **0.0346** (< 0.05) | ✅ Residuals stationary |
| Engle-Granger p-value | **0.0162** (< 0.05) | ✅ **COINTEGRATED** |

➡️ **Key point:** there **is a genuine long-run relationship** between GDP and its drivers —
this regression is **valid, not spurious**. (The earlier spurious-regression concern is
resolved here ✅)

---

## Step 4 — ECM (Error Correction Model)

Short-run changes + the speed of returning to equilibrium, together:

| Term | coef | p-value | Meaning |
|---|---|---|---|
| d(log_GCF) | **0.8145** | **0.000** ✅ | GCF is the strongest driver in the short run too |
| d(log_Remittance) | −0.040 | 0.259 | not significant |
| d(log_FDI) | −0.003 | 0.626 | not significant |
| Inflation | 0.0005 | 0.380 | not significant |
| **ECT_lag (adjustment speed)** | **−0.5245** | **0.006** ✅ | negative and significant |

- **ECM R² = 0.957**
- **ECT = −0.52 means:** whenever the system drifts away from equilibrium, about **52% of
  that gap is automatically corrected each year**. A negative and significant ECT means the
  model is **correct and stable**.

---

## About Dataset 2

In Dataset 2, **GDP Growth is stationary at level (I(0))**, so no cointegration is needed —
a plain stationary OLS is enough. But that model is weak:
**R² = 0.14, Adj R² = −0.06**, with no significant variable.

---

## Final decision — which dataset to use?

| | Dataset 1 (log + Cointegration + ECM) | Dataset 2 (stationary OLS) |
|---|---|---|
| Long-run R² | **0.9994** | — |
| Cointegrated? | ✅ Yes (p=0.016) | Not applicable |
| ECM adjustment speed | **−0.52 (p=0.006)** ✅ | — |
| Significant driver | Gross Capital Formation | None |
| Spurious result? | ❌ No (proven valid) | — |

### 👉 Recommendation: **Use Dataset 1.**
It is no longer just a "good fit" — **cointegration proves the relationship is genuine**, and
the ECM shows that in both the short and long run **Gross Capital Formation is the main driver
of GDP**, with the system returning to equilibrium each year. This is the methodologically
correct and defensible result.

---

### Quick summary (one paragraph)
GDP was Non-Stationary and differencing did not fix it. So we took logs and found that GDP and
Gross Capital Formation are both I(1). The cointegration test confirmed a genuine long-run
relationship between them (not spurious). The ECM showed the system corrects 52% of any
deviation per year, with Gross Capital Formation as the primary determinant of GDP.
**Therefore, Dataset 1 is the best choice.**
