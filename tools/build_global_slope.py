# -*- coding: utf-8 -*-
"""LOLA LDEM_16（全球 16 pix/度 の標高）から傾斜を計算し、
data/site_environment.csv に `slope_deg` 列（1度セルの平均）を足す。

    python tools/build_global_slope.py           # 検算のみ（CSV は書き換えない）
    python tools/build_global_slope.py --write    # data/site_environment.csv を更新

元データ（PDS Geosciences Node, パブリックドメイン。requirements_v3.3.md I6）:
  https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/ldem_16.img
  5760 x 2880, LSB int16, 等緯度経度（equirectangular）, 中心経度 180°。
  標高[m] = DN * 0.5（基準球 R=1737.4 km）。

既知の限界（教材に明記する）:
  - 基線 ≈ 1.9 km（16 pix/度・赤道）。極域の LOLA GDR 240m 版（lola_polar_illumination の
    slope_deg）より粗い。両者は基線が違うので数値は一致しない。
  - |lat| >= 85 は等緯度経度グリッドの東西画素が詰まって傾斜が発散するため NaN。
    極域の傾斜は lola_polar_illumination.csv の slope_deg（240m 基線・極ステレオ投影）を使う。
  - この列は「相対的な起伏の指標」。絶対値の工学判断には使わない（日照率・極域傾斜と同じ扱い）。
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
R_MOON_M = 1737400.0
DN_TO_M = 0.5
POLE_MASK_DEG = 85.0           # |lat| >= これは NaN（極域は lola_polar_illumination を使う）


def _load_dem() -> np.ndarray:
    if not IMG.exists():
        CACHE.mkdir(exist_ok=True)
        print(f"download {URL}")
        # PDS は環境によって urllib が弾かれるので curl にフォールバック
        try:
            import urllib.request
            urllib.request.urlretrieve(URL, IMG)
        except Exception:
            subprocess.run(["curl", "-sSL", "-o", str(IMG), URL], check=True)
    # 行 0 = 北緯 90 付近、列 0 = 経度 0、列は東回りで 0..360（中心経度 180°）。
    return np.fromfile(IMG, dtype="<i2").astype(np.float64).reshape(NLAT, NLON) * DN_TO_M


def _slope_deg(dem: np.ndarray) -> np.ndarray:
    """各画素の双方向傾斜 [度]。緯度で東西方向の実距離が縮むのを補正する。"""
    lat_deg = 90.0 - (np.arange(NLAT) + 0.5) / PPD
    dlat_m = R_MOON_M * np.radians(1.0 / PPD)
    dlon_m = dlat_m * np.cos(np.radians(lat_deg))[:, None]
    gz_lat = np.gradient(dem, axis=0) / dlat_m
    gz_lon = np.gradient(dem, axis=1) / np.clip(dlon_m, 1.0, None)
    return np.degrees(np.arctan(np.hypot(gz_lat, gz_lon)))


def _cell_mean(slope: np.ndarray) -> np.ndarray:
    """16x16 画素を 1 度セルに平均。返り値 shape (180, 360)、行 0 = 北緯 89.5。"""
    return slope.reshape(180, PPD, 360, PPD).mean(axis=(1, 3))


def main() -> None:
    dem = _load_dem()
    slope_px = _slope_deg(dem)
    grid = _cell_mean(slope_px)                    # (180,360) row0 = +89.5N

    # grid: row 0 = +89.5N, col 0 = 経度 0.5°（東回り 0..360）
    def at(lat_c, lon_c):
        r = int(round(89.5 - lat_c))
        c = int(round((lon_c % 360.0) - 0.5))
        return grid[np.clip(r, 0, 179), c % 360]

    print("検算（1度セルの平均傾斜, 度）:")
    for nm, la, lo in [("静かの海(赤道の海)", 8.5, 31.5), ("嵐の大洋", -20.5, -40.5),
                       ("雨の海", 35.5, -18.5), ("南の高地", -50.5, 10.5),
                       ("Tycho 周辺(高地)", -43.5, -11.5), ("SPA 内(裏側)", -40.5, 180.5)]:
        print(f"  {nm:20s} {at(la, lo):5.2f}")

    df = pd.read_csv(CSV)
    df["slope_deg"] = [round(float(at(r.lat, r.lon)), 2) for r in df.itertuples(index=False)]
    df.loc[df["lat"].abs() >= POLE_MASK_DEG, "slope_deg"] = np.nan

    sea = df["区分"] == "海"
    nan_n = int(df.slope_deg.isna().sum())
    print(f"\nslope_deg  NaN {nan_n} 行（|lat|>={POLE_MASK_DEG:.0f}）")
    print(f"           全体 平均 {df.slope_deg.mean():.2f}  中央 {df.slope_deg.median():.2f}")
    print(f"           海   平均 {df.loc[sea, 'slope_deg'].mean():.2f}")
    print(f"           陸   平均 {df.loc[~sea, 'slope_deg'].mean():.2f}")
    assert df.loc[sea, "slope_deg"].mean() < df.loc[~sea, "slope_deg"].mean(), "海が陸より急？"

    if "--write" in sys.argv:
        df.to_csv(CSV, index=False)
        print(f"\nwrote {CSV}  columns: {list(df.columns)}")
    else:
        print("\n（--write を付けると data/site_environment.csv を更新します）")


if __name__ == "__main__":
    main()
