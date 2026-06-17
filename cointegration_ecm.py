"""
Proper econometric route for Non-Stationary data:
  log transform -> ADF -> Engle-Granger Cointegration test -> ECM

Why: In Dataset 1, GDP & Gross Capital Formation stay Non-Stationary even after
2nd difference. Differencing more (over-differencing) is wrong. The correct way is:
  1. log-transform the level (billion) series to tame the trend/variance.
  2. Confirm each log series is I(1) (stationary after ONE difference).
  3. Engle-Granger Cointegration test: if a long-run relationship exists, a
     levels regression is VALID (not spurious).
  4. Build an Error Correction Model (ECM) for the short-run + speed of adjustment.

Dataset 2 (GDP Growth %) is already I(0) stationary at level, so it needs only a
plain stationary OLS — shown for completeness.
"""
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint
import statsmodels.api as sm

warnings.filterwarnings("ignore")
SIG = 0.05


def adf_p(s):
    return adfuller(s.dropna(), autolag="AIC")[1]


def order_of_integration(s, maxd=2):
    """Smallest d in 0..maxd where the series becomes stationary."""
    x = s.copy()
    for d in range(maxd + 1):
        if adf_p(x) < SIG:
            return d, adf_p(x)
        x = x.diff()
    return None, adf_p(x)  # still non-stationary at maxd


# ===================================================================
# DATASET 1 : Engle-Granger Cointegration + ECM on log levels
# ===================================================================
def dataset1():
    print("=" * 80)
    print("DATASET 1 : log transform + Cointegration + ECM")
    print("=" * 80)
    df = pd.read_excel("data/Inflation-1.xlsx").sort_values("Year").set_index("Year")

    dep = "GDP Current (US$ Billion)"
    logcols = [dep,
               "Remittance Received (US$ Billion)",
               "Gross Capital Formation (US$ Billion)",
               "FDI Net Inflows (US$ Billion)"]
    L = pd.DataFrame({f"log_{c.split(' (')[0]}": np.log(df[c]) for c in logcols})
    L["Inflation"] = df["Inflation Rate (%)"]   # a rate: keep as level

    ylog = L.columns[0]                          # log_GDP Current
    xcols = list(L.columns[1:])

    # ---- Step 1: order of integration ----
    print("\n[1] ADF order of integration (on log levels)")
    print(f"{'Series':<40}{'I(d)':<8}{'final p':<10}")
    for c in L.columns:
        d, p = order_of_integration(L[c])
        tag = f"I({d})" if d is not None else "I(>2)"
        print(f"{c:<40}{tag:<8}{round(p,4):<10}")

    # ---- Step 2: cointegrating (long-run) regression ----
    Xl = sm.add_constant(L[xcols])
    long_run = sm.OLS(L[ylog], Xl).fit()
    resid = long_run.resid

    # ---- Step 3: Engle-Granger test ----
    # (a) ADF on the cointegrating residual
    p_resid = adf_p(resid)
    # (b) statsmodels coint() against the first regressor for a clean p-value
    eg_t, eg_p, eg_cv = coint(L[ylog], L[xcols[0]])

    print("\n[2] Long-run (cointegrating) regression  log_GDP ~ X")
    print(long_run.params.round(4).to_string())
    print(f"    R-squared = {long_run.rsquared:.4f}")
    print("\n[3] Engle-Granger Cointegration test")
    print(f"    ADF p-value on residuals : {p_resid:.4f}  "
          f"-> {'COINTEGRATED (residual stationary)' if p_resid < SIG else 'NOT cointegrated'}")
    print(f"    coint() EG t-stat={eg_t:.3f}, p-value={eg_p:.4f}")

    # ---- Step 4: Error Correction Model ----
    d = L.diff()
    d["ECT_lag"] = resid.shift(1)           # error-correction term, lagged 1
    d = d.dropna()
    yecm = d[ylog]
    Xecm = sm.add_constant(d[xcols + ["ECT_lag"]])
    ecm = sm.OLS(yecm, Xecm).fit()

    print("\n[4] Error Correction Model (ECM)   d(log_GDP) ~ d(X) + ECT_lag")
    print(ecm.summary().tables[1])
    g = ecm.params["ECT_lag"]
    gp = ecm.pvalues["ECT_lag"]
    print(f"\n    Speed of adjustment (ECT coef) = {g:.4f}  (p={gp:.4f})")
    print(f"    {'OK: negative & significant -> valid error correction' if (g < 0 and gp < SIG) else 'Note: check sign/significance'}")
    print(f"    ECM R-squared = {ecm.rsquared:.4f}")
    return dict(long_run=long_run, p_resid=p_resid, eg_p=eg_p, ecm=ecm)


# ===================================================================
# DATASET 2 : already stationary GDP Growth -> plain stationary OLS
# ===================================================================
def dataset2():
    print("\n" + "=" * 80)
    print("DATASET 2 : GDP Growth is I(0) -> stationary OLS (no cointegration needed)")
    print("=" * 80)
    df = pd.read_excel("data/Bangladesh_GDPGrowth.xlsx").sort_values("Year").set_index("Year")
    dep = "GDP Growth Annual (%)"

    use = {}
    print(f"\n[1] ADF order of integration")
    print(f"{'Series':<48}{'I(d)':<8}{'final p':<10}")
    for c in df.columns:
        d, p = order_of_integration(df[c])
        tag = f"I({d})" if d is not None else "I(>2)"
        print(f"{c:<48}{tag:<8}{round(p,4):<10}")
        # use stationary version: difference d times
        s = df[c]
        for _ in range(d or 0):
            s = s.diff()
        use[c] = s

    S = pd.DataFrame(use).dropna()
    y = S[dep]
    X = sm.add_constant(S.drop(columns=[dep]))
    ols = sm.OLS(y, X).fit()
    print(f"\n[2] Stationary OLS  (n={int(ols.nobs)})")
    print(ols.summary().tables[1])
    print(f"    R-squared={ols.rsquared:.4f}  Adj R-squared={ols.rsquared_adj:.4f}  "
          f"F p-value={ols.f_pvalue:.4f}")
    return dict(ols=ols)


if __name__ == "__main__":
    dataset1()
    dataset2()
