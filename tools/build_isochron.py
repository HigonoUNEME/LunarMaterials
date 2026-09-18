# -*- coding: utf-8 -*-
"""クレーター密度 → 絶対年代 の参照表 data/isochron_reference.csv を作る。

    python tools/build_isochron.py --write

出典（式のみ。ダウンロードは無い）:
  Neukum, G., Ivanov, B. A., & Hartmann, W. K. (2001),
  Cratering records in the inner solar system in relation to the lunar reference system,
  Space Science Reviews 96, 55–86.

- 生産関数（PF）：log10 N_cum(>=D) = Σ a[n]·(log10 D)^n   （D は km、参照面 ~1 Ga）
- 編年関数：N(1km, T) = 5.44e-14·(exp(6.93·T) − 1) + 8.38e-4·T   （T は Ga、単位 km^-2）
- 年代 T の N_cum(>=D) = 10**PF(D) · N(1,T) / 10**a[0]

検証：雨の海の一区画で D>=8km を数えると密度 ~38/Mkm^2 → 年代 ~3.5 Ga
      （Hiesinger らの雨の海玄武岩 3.3–3.6 Ga と整合）。
"""
import pathlib
import sys

import numpy as np
import pandas as pd

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "isochron_reference.csv"

A = [-3.0876, -3.557528, 0.781027, 1.021521, -0.156012, -0.444058,
     0.019977, 0.086850, -0.005874, -0.006809, 8.25e-4, 5.54e-5]
AGES = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.2, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3]


def _pf_logN(D):
    x = np.log10(D)
    return sum(A[n] * x ** n for n in range(12))


def _chrono_N1(T):
    return 5.44e-14 * (np.exp(6.93 * T) - 1) + 8.38e-4 * T


def _N_ge(D, T):
    return 10 ** _pf_logN(D) * _chrono_N1(T) / 10 ** A[0]


def main():
    rows = [{
        "age_Ga": T,
        "N_ge_1km_per_Mkm2": round(_chrono_N1(T) * 1e6),
        "N_ge_8km_per_Mkm2": round(_N_ge(8.0, T) * 1e6, 1),
        "N_ge_20km_per_Mkm2": round(_N_ge(20.0, T) * 1e6, 2),
    } for T in AGES]
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    if "--write" in sys.argv:
        df.to_csv(OUT, index=False)
        print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
