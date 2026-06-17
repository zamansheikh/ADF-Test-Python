"""
ADF Stationarity Test + OLS Regression
--------------------------------------
Workflow (per dataset):
 1. Run the Augmented Dickey-Fuller (ADF) test on every variable at LEVEL.
 2. If a series is Non-Stationary (ADF p-value >= 0.05) -> take the First Difference
    and re-test, so every series used in the model is Stationary.
 3. Run OLS regression with GDP as the Dependent Variable and the rest as
    Independent Variables (using the stationary version of each series).
 4. Do this for BOTH datasets and compare the results.
"""

import warnings
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm

warnings.filterwarnings("ignore")
SIG = 0.05  # significance level for stationarity decision


def adf_pvalue(series):
    """Return ADF p-value for a clean (NaN-dropped) series."""
    s = series.dropna()
    return adfuller(s, autolag="AIC")[1]


def make_stationary(df, cols):
    """
    For each column: ADF at level. If non-stationary, take 1st difference.
    Returns (stationary_df, report_rows).
    """
    out = {}
    report = []
    for c in cols:
        p_level = adf_pvalue(df[c])
        if p_level < SIG:
            out[c] = df[c]
            report.append([c, round(p_level, 4), "Stationary", "Level (I(0))", "-"])
        else:
            diff = df[c].diff()
            p_diff = adf_pvalue(diff)
            out[c] = diff
            status = "Stationary" if p_diff < SIG else "STILL Non-Stationary"
            report.append([c, round(p_level, 4),
                           "Non-Stationary -> diff", "1st Diff (I(1))",
                           f"{round(p_diff,4)} ({status})"])
    return pd.DataFrame(out), report


def analyse(path, dep_col, name):
    print("=" * 90)
    print(f"DATASET: {name}   ({path})")
    print("=" * 90)

    df = pd.read_excel(path).sort_values("Year").reset_index(drop=True)
    df = df.set_index("Year")
    vars_ = list(df.columns)

    # ---- Step 1 & 2: ADF + first difference where needed ----
    stat_df, report = make_stationary(df, vars_)
    rep = pd.DataFrame(report, columns=[
        "Variable", "ADF p (level)", "Decision", "Used as", "ADF p (after diff)"])
    print("\n[ ADF TEST RESULTS ]  (H0 = unit root / Non-Stationary; reject if p < 0.05)\n")
    print(rep.to_string(index=False))

    # ---- Step 3: OLS regression ----
    stat_df = stat_df.dropna()
    y = stat_df[dep_col]
    X = sm.add_constant(stat_df.drop(columns=[dep_col]))
    model = sm.OLS(y, X).fit()

    print(f"\n[ OLS REGRESSION ]  Dependent = '{dep_col}'  (n = {int(model.nobs)})\n")
    print(model.summary())
    print("\n")
    return {
        "name": name, "dep": dep_col, "n": int(model.nobs),
        "r2": model.rsquared, "adj_r2": model.rsquared_adj,
        "f_p": model.f_pvalue, "model": model,
    }


def main():
    r1 = analyse("data/Inflation-1.xlsx",
                 "GDP Current (US$ Billion)",
                 "1) Levels in US$ Billion (Inflation-1)")
    r2 = analyse("data/Bangladesh_GDPGrowth.xlsx",
                 "GDP Growth Annual (%)",
                 "2) Ratios / Growth in % of GDP (Bangladesh_GDPGrowth)")

    print("=" * 90)
    print("COMPARISON SUMMARY")
    print("=" * 90)
    comp = pd.DataFrame([
        [r["name"], r["dep"], r["n"], round(r["r2"], 4),
         round(r["adj_r2"], 4), f"{r['f_p']:.2e}"]
        for r in (r1, r2)
    ], columns=["Dataset", "Dependent", "n", "R2", "Adj R2", "F p-value"])
    print(comp.to_string(index=False))

    best = max((r1, r2), key=lambda r: r["adj_r2"])
    print(f"\n>> Better fit (by Adjusted R2): {best['name']}  "
          f"(Adj R2 = {best['adj_r2']:.4f}, model F p-value = {best['f_p']:.2e})")


if __name__ == "__main__":
    main()
