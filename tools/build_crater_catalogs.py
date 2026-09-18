# -*- coding: utf-8 -*-
"""3つのクレーターカタログを教材用 CSV に整形する。

    pip install numpy pandas geopandas
    python tools/build_crater_catalogs.py --robbins <path> --wangwu <path> --deep <path> --write

元データ:
  craters_subset.csv  ← Robbins, S. J. (2018), JGR Planets 123（パブリックドメイン、NASA PDS / USGS）。
     Catalog_Moon_Release_20180815_shapefile180.zip の .shp を --robbins に渡す。
     https://asc-astropedia.s3.us-west-2.amazonaws.com/Moon/Research/Craters/Ancillary/
     フィールド：DIAM_C_IM（円直径 km）, D_E_MA_IM/D_E_MI_IM（楕円長短径 km）,
     D_E_EC_IM（離心率）, D_E_ELP_IM（扁平率）, ARC_IMG（リム弧率）, LAT_EL_IM/LON_EL_IM。
  craters_3d.csv      ← Wang, Y., Wu, B. ほか (2021), JGR Planets 126（CC BY 4.0）。
     Zenodo 10.5281/zenodo.4983248 の LU1319373_Wang&Wu_2021.rar を展開した
     「LU1319373_Wang & Wu_2021.txt」（16行ヘッダ＋タブ区切り）を --wangwu に渡す。
  deepcraters.csv     ← Yang, C., Zhao, H. ほか (2020), Nature Communications 11（CC BY 4.0）。
     figshare 10.6084/m9.figshare.12768539 の Aged_Lunar_Crater_Database_DeepCraters_2020(1).csv を --deep に。
     （committed 版は raw とバイト一致：列 Flags_data,ID,Lat,Lon,Diam_km,Age、18,996 行）

整形:
  craters_subset : DIAM_C_IM >= 8km、列を lat/lon/diam_km/… にリネーム、lon を -180..180 に
  craters_3d     : Diameter(m) >= 10000、m→km、depth_diameter_ratio 列を追加、lon を -180..180 に
  deepcraters    : Age 列つきの行をそのまま（Lon は raw が -180..180 なので触らない）

検証（committed 版と一致）: 36,377 / 24,982 / 18,996 行。
  craters_3d の d/D 中央値は 0.077（＝劣化後の"今の深さ"。教科書の 0.2 とは別物）。
"""
import argparse
import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"


def _wrap(lon):
    return ((np.asarray(lon, float) + 180) % 360) - 180


def robbins(src: str) -> pd.DataFrame:
    import geopandas as gpd
    g = gpd.read_file(src)   # 180° 版。位置はポイントの座標（円フィット中心）を使う
    out = pd.DataFrame({
        "crater_id": g["CRATER_ID"].astype(str),
        "lat": g.geometry.y, "lon": g.geometry.x,
        "diam_km": g["DIAM_C_IM"],
        "diam_major_km": g["D_E_MA_IM"], "diam_minor_km": g["D_E_MI_IM"],
        "eccentricity": g["D_E_EC_IM"], "ellipticity": g["D_E_ELP_IM"],
        "rim_arc_fraction": g["ARC_IMG"],
    })
    return out[out["diam_km"] >= 8].reset_index(drop=True)


def wangwu(src: str) -> pd.DataFrame:
    with open(src, encoding="utf-8", errors="ignore") as f:
        skip = next(i for i, ln in enumerate(f) if ln.startswith("ID\t"))
    w = pd.read_csv(src, sep="\t", skiprows=skip)
    w.columns = [c.strip() for c in w.columns]
    lonc = next(c for c in w.columns if c.lower().startswith("lon"))
    latc = next(c for c in w.columns if c.lower().startswith("lat"))
    dic = next(c for c in w.columns if c.lower().startswith("diam"))
    dec = next(c for c in w.columns if c.lower().startswith("depth"))
    out = pd.DataFrame({
        "crater_id": w["ID"].astype(int),
        "lat": w[latc].astype(float), "lon": _wrap(w[lonc].astype(float)),
        "diameter_km": w[dic].astype(float) / 1000.0,
        "depth_km": w[dec].astype(float) / 1000.0,
    })
    out["depth_diameter_ratio"] = (out["depth_km"] / out["diameter_km"]).round(4)
    return out[out["diameter_km"] >= 10].reset_index(drop=True)


def deep(src: str) -> pd.DataFrame:
    d = pd.read_csv(src)
    keep = [c for c in ("Flags_data", "ID", "Lat", "Lon", "Diam_km", "Age") if c in d.columns]
    return d[keep].dropna(subset=["Age"]).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--robbins")
    ap.add_argument("--wangwu")
    ap.add_argument("--deep")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    jobs = [("craters_subset.csv", robbins, a.robbins, 36377),
            ("craters_3d.csv", wangwu, a.wangwu, 24982),
            ("deepcraters.csv", deep, a.deep, 18996)]
    for name, fn, src, expect in jobs:
        if not src:
            continue
        df = fn(src)
        ok = "OK" if len(df) == expect else f"!! expected {expect}"
        print(f"{name}: {len(df):,} 行  {ok}")
        if name == "craters_3d.csv":
            bin1 = df[(df.diameter_km >= 10) & (df.diameter_km < 15)].depth_diameter_ratio.median()
            print(f"   d/D 中央値 全体 {df.depth_diameter_ratio.median():.3f} / 10-15km帯 {bin1:.3f}"
                  f"（どちらも劣化後の現在値。教科書の単純クレーター 0.2 とは別物）")
        if a.write:
            df.to_csv(D / name, index=False)
            print(f"   wrote {D / name}")


if __name__ == "__main__":
    main()
