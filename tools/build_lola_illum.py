# -*- coding: utf-8 -*-
"""LOLA 極域の平均日照率・永久影マスクの PDS3 IMG を約1km ブロックに整理し、
data/lola_polar_illumination.csv の日照 2 列
（average_illumination_percent, permanent_shadow_fraction）を作る。
傾斜 slope_deg は別スクリプト tools/build_slope.py。

    pip install numpy pandas
    python tools/build_lola_illum.py --write

元データ（パブリックドメイン, NASA / LOLA チーム）:
  http://imbrium.mit.edu/EXTRAS/ILLUMINATION/IMG/
    AVGVISIB_85S_060M_201608.IMG / .LBL   平均日照率 60m/pix, 5058x5058, LSB int16
        AVERAGE_VISIBILITY = DN * 0.00004 + 0        （0〜1）
    LPSR_85S_060M_201608.IMG / .LBL       永久影マスク
        PERMANENT_SHADOW = DN * 0.000025 + 0.5       （DN=+20000→1, -20000→0）
    AVGVISIB_85N_060M / LPSR_85N_060M     北極
  手法: Mazarico, E. ほか (2011), Icarus 211, 1066–1081。
  投影: 極ステレオ, 球半径 1737.4 km, MAP_SCALE 60 m/pix, PROJECTION_OFFSET 2528.5,
        MAXIMUM_LATITUDE = ±82.9 度。

処理:
  1. 60m/pix の 16bit ラスタを 18x18 画素（約1.08km）でブロック平均
  2. ブロック中心の極ステレオ座標を緯度経度に逆変換（南: φ=2·atan(ρ/2R)-π/2）
  3. |緯度| >= 82.96 の点だけ残し、南北を結合。約 157,922 点。

注意: 日照率の絶対値は文献と乖離する（新しい高解像度 DTM 解析との手法差）。
  Shackleton・Shoemaker で illumination≈0 を再現できることは確認済み。順序のみ信頼。
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import urllib.request

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = pathlib.Path(__file__).resolve().parent / "_cache"
OUT = ROOT / "data" / "lola_polar_illumination.csv"
BASE = "http://imbrium.mit.edu/EXTRAS/ILLUMINATION/IMG/"
R = 1737400.0            # m
BLOCK = 18               # 60 m -> ~1.08 km
LAT_MIN = 82.96


def _fetch(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception:
        if shutil.which("curl") is None:
            raise
        subprocess.run(["curl", "-sS", "--max-time", "200", "-o", str(dest), url], check=True)


def _read(name):
    img, lbl = CACHE / f"{name}.IMG", CACHE / f"{name}.LBL"
    CACHE.mkdir(exist_ok=True)
    for p, e in ((img, "IMG"), (lbl, "LBL")):
        if not p.exists():
            print(f"download {BASE}{name}.{e}")
            _fetch(f"{BASE}{name}.{e}", p)
    txt = lbl.read_text(errors="ignore")

    def g(k, d=None):
        m = re.search(rf"\b{k}\s*=\s*([-\d.]+)", txt)
        return float(m.group(1)) if m else d
    n = int(g("LINES"))
    scale_m = g("MAP_SCALE", 60.0)
    off = g("LINE_PROJECTION_OFFSET", (n - 1) / 2)
    a = np.fromfile(img, dtype="<i2").reshape(n, n).astype(np.float64)
    a = a * g("SCALING_FACTOR", 1.0) + g("OFFSET", 0.0)
    return a, scale_m, off


def _blocks(a):
    n = (a.shape[0] // BLOCK) * BLOCK
    return a[:n, :n].reshape(n // BLOCK, BLOCK, n // BLOCK, BLOCK).mean(axis=(1, 3))


def _latlon(nb, scale_m, off, south):
    # ブロック中心の (line, sample) をフル解像度 pix に戻す
    idx = (np.arange(nb) * BLOCK + (BLOCK - 1) / 2.0)
    line = idx[:, None] + 0 * idx[None, :]
    samp = idx[None, :] + 0 * idx[:, None]
    x = (samp - off) * scale_m
    y = (off - line) * scale_m
    rho = np.hypot(x, y)
    if south:
        lat = np.degrees(2 * np.arctan(rho / (2 * R)) - np.pi / 2)   # -> -90 at rho=0
        lon = np.degrees(np.arctan2(x, y))
    else:
        lat = np.degrees(np.pi / 2 - 2 * np.arctan(rho / (2 * R)))
        lon = np.degrees(np.arctan2(x, -y))
    return lat, lon


def _pole(prefix, south):
    vis, sc, off = _read(f"AVGVISIB_{prefix}_060M_201608")
    psr, _, _ = _read(f"LPSR_{prefix}_060M_201608")
    illum = _blocks(vis) * 100.0                 # %
    shadow = _blocks(np.clip(psr, 0, 1))         # 0〜1
    lat, lon = _latlon(illum.shape[0], sc, off, south)
    keep = np.abs(lat) >= LAT_MIN
    return pd.DataFrame({
        "lat": lat[keep].round(4), "lon": (((lon[keep] + 180) % 360) - 180).round(4),
        "average_illumination_percent": illum[keep].round(2),
        "permanent_shadow_fraction": shadow[keep].round(3),
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    df = pd.concat([_pole("85S", True), _pole("85N", False)], ignore_index=True)
    print(f"rows {len(df)}  illum median {df.average_illumination_percent.median():.1f}%"
          f"  PSR frac {df.permanent_shadow_fraction.mean():.2f}")
    for nm, la, lo in [("Shackleton", -89.9, 0.0), ("Shoemaker", -88.1, 44.9)]:
        d = df[(df.lat.between(la - 0.3, la + 0.3))]
        d = d.iloc[(((d.lon - lo + 180) % 360 - 180)).abs().argsort()[:5]]
        print(f"  {nm}: illum {d.average_illumination_percent.mean():.1f}%  PSR {d.permanent_shadow_fraction.mean():.2f}")

    if args.write:
        if OUT.exists():
            old = pd.read_csv(OUT)
            if "slope_deg" in old.columns and len(old) == len(df):
                df["slope_deg"] = old["slope_deg"].to_numpy()   # slope 列を温存
        df.to_csv(OUT, index=False)
        print(f"wrote {OUT}  ※slope_deg が無ければ tools/build_slope.py --write で付け直す")


if __name__ == "__main__":
    main()
