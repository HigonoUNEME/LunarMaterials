# -*- coding: utf-8 -*-
"""LOLA GDR の傾斜マップ（LDSM, 240 m 基線）を data/lola_polar_illumination.csv の
各地点に `slope_deg` 列として付与する前処理スクリプト。

    pip install numpy pandas
    python tools/build_slope.py            # 検算のみ（CSV は書き換えない）
    python tools/build_slope.py --write     # data/lola_polar_illumination.csv を更新

元データ（PDS Geosciences Node, パブリックドメイン）:
  https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/
    ldsm_75s_240m.img / .lbl   （南極 75-90S, 極ステレオ投影, 3812x3812, LSB int16）
    ldsm_75n_240m.img / .lbl   （北極 75-90N）
値の復元: slope_deg = DN * 0.0015 + 45   （DN==0 は no-data）
投影: 極ステレオ（球体 R=1737.4km）, MAP_SCALE 240 m/pix, 投影中心 = 極,
      LINE/SAMPLE_PROJECTION_OFFSET = 1905.60874416666667, ISIS PolarStereographic 準拠。

既知の限界（教材に明記する）:
  - 基線 240 m の双方向傾斜。1 km ブロック平均をとって配置している。
  - LOLA の軌道トラックに沿った縞状アーティファクトが残る（GDR 由来）。
  - 極点から 0.7 度以内（|lat|>89.3）はトラック収束のノイズが大きいため NaN。
  - 南極域は South Pole-Aitken 盆地の縁で本来起伏が大きく、値は文献の地域平均より
    やや高めに出る。日照率と同じく「相対的な起伏の指標」として使う（絶対値の工学判断には使わない）。
"""
import pathlib
import sys
import urllib.request

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "lola_polar_illumination.csv"
CACHE = pathlib.Path(__file__).resolve().parent / "_cache"
BASE = ("https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/"
        "lrolol_1xxx/data/lola_gdr/polar/img/")

R = 1737400.0          # m, spherical (label A_AXIS_RADIUS)
SCALE = 240.0          # m/pix (label MAP_SCALE)
OFF = 1905.60874416666667   # label LINE/SAMPLE_PROJECTION_OFFSET
N = 3812
POLE_MASK_DEG = 89.3   # |lat| を超えたら slope=NaN


def _img(name: str) -> np.ndarray:
    CACHE.mkdir(exist_ok=True)
    p = CACHE / f"{name}.img"
    if not p.exists():
        print(f"download {BASE}{name}.img")
        urllib.request.urlretrieve(f"{BASE}{name}.img", p)
    raw = np.fromfile(p, dtype="<i2").reshape(N, N)
    sl = raw.astype(np.float64) * 0.0015 + 45.0
    sl[raw == 0] = np.nan
    return sl


def _sample(sub: pd.DataFrame, img: np.ndarray, south: bool, hp: int = 2) -> np.ndarray:
    lat = np.deg2rad(sub.lat.to_numpy())
    lon = np.deg2rad(sub.lon.to_numpy())
    if south:
        rho = 2 * R * np.tan(np.pi / 4 + lat / 2)
        y = rho * np.cos(lon)
    else:
        rho = 2 * R * np.tan(np.pi / 4 - lat / 2)
        y = -rho * np.cos(lon)
    line = OFF - y / SCALE
    samp = OFF + (rho * np.sin(lon)) / SCALE
    r = np.round(line).astype(int)
    c = np.round(samp).astype(int)
    out = np.full(len(sub), np.nan)
    ok = (r >= hp) & (r < N - hp) & (c >= hp) & (c < N - hp)
    for i in np.where(ok)[0]:
        w = img[r[i] - hp:r[i] + hp + 1, c[i] - hp:c[i] + hp + 1]
        if np.isfinite(w).any():
            out[i] = np.nanmean(w)
    return out


def main() -> None:
    simg, nimg = _img("ldsm_75s_240m"), _img("ldsm_75n_240m")

    # 検算：南極の既知クレーター（床は平ら・縁や山塊は急）
    def at(la, lo):
        s = pd.DataFrame({"lat": [la], "lon": [lo]})
        return float(_sample(s, simg, True, hp=1)[0])
    print("検算（南極, 度）:")
    for nm, la, lo in [("Shoemaker 床", -88.13, 44.9), ("de Gerlache 床", -88.5, 273.0),
                       ("Haworth 床", -87.45, 4.4), ("Malapert 山塊", -85.98, 2.93),
                       ("Amundsen 縁", -84.35, 85.6)]:
        print(f"  {nm:16s} {at(la, lo):5.1f}")

    df = pd.read_csv(CSV)
    sm = df.lat < 0
    df.loc[sm, "slope_deg"] = _sample(df[sm], simg, True)
    df.loc[~sm, "slope_deg"] = _sample(df[~sm], nimg, False)
    df.loc[df.lat.abs() > POLE_MASK_DEG, "slope_deg"] = np.nan
    df["slope_deg"] = df["slope_deg"].round(2)

    print(f"\nslope_deg: NaN {df.slope_deg.isna().sum()} / {len(df)} "
          f"({100 * df.slope_deg.isna().mean():.1f}%)")
    print(df.slope_deg.describe().round(2).to_string())

    if "--write" in sys.argv:
        df.to_csv(CSV, index=False)
        print(f"\nwrote {CSV}  columns: {list(df.columns)}")
    else:
        print("\n（--write を付けると data/lola_polar_illumination.csv を更新します）")


if __name__ == "__main__":
    main()
