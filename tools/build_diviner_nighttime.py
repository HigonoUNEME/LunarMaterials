# -*- coding: utf-8 -*-
"""Diviner の「夜の最低温度」と「その緯度平均からのずれ（異常）」を CSV にする。
data/diviner_nighttime.csv（岩の多さ＝熱物性の代理指標。クラスタリング探究で使う）。

    pip install numpy pandas
    python tools/build_diviner_nighttime.py --write

元データ（パブリックドメイン, NASA / UCLA Diviner チーム）:
  https://luna1.diviner.ucla.edu/~jpierre/diviner/level4_raster_data/
    diviner_tbol_min.xyz        夜の最低温度（0.5 ppd, lon lat T[K]）
    diviner_tbol_min_anom.xyz   その緯度平均を引いた異常（K）。熱物性に対応（Williams+2017）
  ※UCLA サーバは TLS が古く urllib は失敗しうる → curl フォールバック。

意味：夜、岩や岩塊が多い地形は熱をためて冷めにくい（熱慣性が大きい）＝周りより暖かい
  ＝ min_anomaly が正。若いクレーター（Tycho・Copernicus）の噴出物で顕著、古い平らな
  海ではほぼ 0。Bandfield et al. (2011) の岩石量マップと同じ原理。

検証（committed 版の出力）:
  Tycho の周囲（半径3度）の平均 min_anomaly は全球平均より明確に高い。海はほぼ 0。
"""
import pathlib
import shutil
import subprocess
import sys
import urllib.request

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = pathlib.Path(__file__).resolve().parent / "_cache"
OUT = ROOT / "data" / "diviner_nighttime.csv.gz"
BASE = "https://luna1.diviner.ucla.edu/~jpierre/diviner/level4_raster_data/"


def _fetch(url: str, dest: pathlib.Path) -> None:
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception:
        if shutil.which("curl") is None:
            raise
        subprocess.run(["curl", "-sS", "--max-time", "120", "-o", str(dest), url], check=True)


def _xyz(name: str) -> pd.DataFrame:
    CACHE.mkdir(exist_ok=True)
    p = CACHE / f"{name}.xyz"
    if not p.exists():
        print(f"download {BASE}{name}.xyz")
        _fetch(f"{BASE}{name}.xyz", p)
    a = np.loadtxt(p)
    return pd.DataFrame({"lon": a[:, 0].round(4), "lat": a[:, 1].round(4), "v": a[:, 2]})


def main() -> None:
    tmin = _xyz("diviner_tbol_min")
    anom = _xyz("diviner_tbol_min_anom")
    df = tmin.rename(columns={"v": "temp_min_K"})
    df = df.merge(anom.rename(columns={"v": "temp_min_anomaly_K"}), on=["lon", "lat"])
    df["temp_min_K"] = df["temp_min_K"].round(2)
    df["temp_min_anomaly_K"] = df["temp_min_anomaly_K"].round(3)
    df = df[["lon", "lat", "temp_min_K", "temp_min_anomaly_K"]]

    def near(lat0, lon0, deg=3.0):
        d = df[(df.lat.between(lat0 - deg, lat0 + deg)) & (df.lon.between(lon0 - deg, lon0 + deg))]
        return d.temp_min_anomaly_K.mean()

    print(f"rows {len(df)}")
    print(f"  全球 min_anomaly 平均 {df.temp_min_anomaly_K.mean():+.2f} K（定義上 ~0）")
    print(f"  Tycho (-43.3,-11.4) 周辺 {near(-43.3, -11.4):+.2f} K  ← 若い＝岩だらけ、正で大きいはず")
    print(f"  Copernicus (9.6,-20.1) 周辺 {near(9.6, -20.1):+.2f} K  ← 同上")
    print(f"  静かの海 (8.5,31.4) 周辺 {near(8.5, 31.4):+.2f} K  ← 古い平ら、~0 のはず")

    if "--write" in sys.argv:
        df.to_csv(OUT, index=False, compression="gzip")
        print(f"wrote {OUT}")
    else:
        print("--write で data/diviner_nighttime.csv.gz を作成")


if __name__ == "__main__":
    main()
