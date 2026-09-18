# -*- coding: utf-8 -*-
"""LOLA LDEM_16（全球 16 pix/度 の標高）から、data/site_environment.csv に
`elev_m` 列（1度セルの平均標高、基準球 R=1737.4km からの高さ[m]）を足す。
tools/build_global_slope.py と同じ元データ（1回ダウンロードすれば tools/_cache/ を共有）。

    python tools/build_global_elevation.py           # 検算のみ（CSV は書き換えない）
    python tools/build_global_elevation.py --write    # data/site_environment.csv を更新

元データ（PDS Geosciences Node, パブリックドメイン。requirements_v3.3.md I6）:
  https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/ldem_16.img
  5760 x 2880, LSB int16, 等緯度経度（equirectangular）, 中心経度 180°。
  標高[m] = DN * 0.5（基準球 R=1737.4 km）。

既知の限界（教材に明記する）:
  - 傾斜（slope_deg）と違い、標高そのものは緯度で微分しないので極域も NaN にしない
    （画素の面積は緯度で歪むが、値自体は各画素の実測標高のまま）。
  - 基線 ≈ 1.9 km（16 pix/度・赤道）。全球の大づかみな起伏（海の凹み・高地の隆起）を
    見るための指標で、クレーター1つ1つの深さのような細かい地形には使わない。
"""
import pathlib
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "site_environment.csv"
CACHE = pathlib.Path(__file__).resolve().parent / "_cache"
IMG = CACHE / "ldem_16.img"
URL = ("https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/"
       "lrolol_1xxx/data/lola_gdr/cylindrical/img/ldem_16.img")

PPD = 16                       # pixel / degree
NLAT, NLON = 180 * PPD, 360 * PPD
DN_TO_M = 0.5


def _load_dem() -> np.ndarray:
    if not IMG.exists():
        CACHE.mkdir(exist_ok=True)
        print(f"download {URL}")
        try:
            import urllib.request
            urllib.request.urlretrieve(URL, IMG)
        except Exception:
            subprocess.run(["curl", "-sSL", "-o", str(IMG), URL], check=True)
    # 行 0 = 北緯 90 付近、列 0 = 経度 0、列は東回りで 0..360（中心経度 180°）。
    return np.fromfile(IMG, dtype="<i2").astype(np.float64).reshape(NLAT, NLON) * DN_TO_M


def _cell_mean(dem: np.ndarray) -> np.ndarray:
    """16x16 画素を 1 度セルに平均。返り値 shape (180, 360)、行 0 = 北緯 89.5。"""
    return dem.reshape(180, PPD, 360, PPD).mean(axis=(1, 3))


def main() -> None:
    dem = _load_dem()
    grid = _cell_mean(dem)   # (180,360) row0 = +89.5N, col0 = 経度0.5°（東回り 0..360）

    def at(lat_c, lon_c):
        r = int(round(89.5 - lat_c))
        c = int(round((lon_c % 360.0) - 0.5))
        return grid[np.clip(r, 0, 179), c % 360]

    print("検算（1度セルの平均標高, m。基準球 R=1737.4km からの高さ）:")
    for nm, la, lo in [("静かの海(赤道の海)", 8.5, 31.5), ("嵐の大洋", -20.5, -40.5),
                       ("雨の海", 35.5, -18.5), ("南の高地", -50.5, 10.5),
                       ("Tycho 周辺(高地)", -43.5, -11.5), ("SPA 内(裏側・全月で最も低い)", -40.5, 180.5)]:
        print(f"  {nm:28s} {at(la, lo):8.0f}")

    df = pd.read_csv(CSV)
    df["elev_m"] = [round(float(at(r.lat, r.lon)), 1) for r in df.itertuples(index=False)]

    sea = df["区分"] == "海"
    print(f"\nelev_m  全体 平均 {df.elev_m.mean():.0f}  最小 {df.elev_m.min():.0f}  最大 {df.elev_m.max():.0f}")
    print(f"        海   平均 {df.loc[sea, 'elev_m'].mean():.0f}")
    print(f"        陸   平均 {df.loc[~sea, 'elev_m'].mean():.0f}")
    assert df.loc[sea, "elev_m"].mean() < df.loc[~sea, "elev_m"].mean(), "海が陸より高い？"

    if "--write" in sys.argv:
        df.to_csv(CSV, index=False)
        print(f"\nwrote {CSV}  columns: {list(df.columns)}")
    else:
        print("\n（--write を付けると data/site_environment.csv を更新します）")


if __name__ == "__main__":
    main()
