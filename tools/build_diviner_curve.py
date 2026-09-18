# -*- coding: utf-8 -*-
"""Diviner の瞬間温度マップ24枚を現地時間で位相整列し、
data/diviner_global.csv.gz（各点の現地時間0〜23時の温度カーブ）を作る。

    pip install numpy pandas
    python tools/build_diviner_curve.py --write

元データ（パブリックドメイン, NASA）:
  https://luna1.diviner.ucla.edu/~jpierre/diviner/level4_raster_data/
    diviner_tbol_snapshot_000E.xyz 〜 _345E.xyz  （subsolar 経度 15度刻み、24枚）
  各ファイル: ASCII, 「lon lat T_bol[K]」、0.5度グリッド（720x360）、約6.7MB。
  ※このサーバは TLS 設定が古く、新しめの OpenSSL では接続に失敗することがある。
    その場合はブラウザ等で 24 ファイルを tools/_cache/ に置いてから再実行する。

位相整列: 現地時間 LT = (12 + (lon - subsolar_lon)/15) mod 24。
  各点で 24 枚の (LT, T) を LT でソートし、整数時 0..23 に円環線形補間。
"""
import pathlib
import shutil
import subprocess
import sys
import urllib.request

import numpy as np
import pandas as pd


def _fetch(url: str, dest: pathlib.Path) -> None:
    """urllib で取り、TLS が古くて失敗したら curl にフォールバック。"""
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception:
        if shutil.which("curl") is None:
            raise
        subprocess.run(["curl", "-sS", "--max-time", "120", "-o", str(dest), url], check=True)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = pathlib.Path(__file__).resolve().parent / "_cache"
OUT = ROOT / "data" / "diviner_global.csv.gz"
BASE = "https://luna1.diviner.ucla.edu/~jpierre/diviner/level4_raster_data/"
SUBSOLAR = list(range(0, 360, 15))          # 24 枚
LT_COLS = [f"t_lt{h:02d}" for h in range(24)]


def _load_snapshot(sslon: int) -> pd.DataFrame:
    CACHE.mkdir(exist_ok=True)
    name = f"diviner_tbol_snapshot_{sslon:03d}E.xyz"
    p = CACHE / name
    if not p.exists():
        print(f"download {BASE}{name}")
        _fetch(f"{BASE}{name}", p)
    a = np.loadtxt(p)                        # lon lat T
    return pd.DataFrame({"lon": a[:, 0], "lat": a[:, 1], "T": a[:, 2]})


def main() -> None:
    base = _load_snapshot(SUBSOLAR[0])[["lon", "lat"]].reset_index(drop=True)
    n = len(base)
    lt_stack = np.empty((n, 24))             # 現地時間ごとの T（下で並べ替え）
    raw_lt = np.empty((n, 24))
    raw_T = np.empty((n, 24))
    for j, ss in enumerate(SUBSOLAR):
        d = _load_snapshot(ss)
        assert len(d) == n, f"格子が違う: {ss}"
        raw_T[:, j] = d["T"].to_numpy()
        raw_lt[:, j] = (12 + (base["lon"].to_numpy() - ss) / 15.0) % 24.0

    # 各点で LT 昇順に並べ、円環（0-24）で整数時に線形補間
    order = np.argsort(raw_lt, axis=1)
    lt_sorted = np.take_along_axis(raw_lt, order, axis=1)
    T_sorted = np.take_along_axis(raw_T, order, axis=1)
    lt_ext = np.concatenate([lt_sorted - 24, lt_sorted, lt_sorted + 24], axis=1)
    T_ext = np.concatenate([T_sorted, T_sorted, T_sorted], axis=1)
    hours = np.arange(24)
    for i in range(n):
        lt_stack[i] = np.interp(hours, lt_ext[i], T_ext[i])

    out = base.copy()
    for h in range(24):
        out[LT_COLS[h]] = lt_stack[:, h].round(1)
    out["temp_noon_K"] = out["t_lt12"]
    out["temp_midnight_K"] = out["t_lt00"]
    out["temp_diff_K"] = (out["temp_noon_K"] - out["temp_midnight_K"]).round(1)
    out = out[["lon", "lat", "temp_noon_K", "temp_midnight_K", "temp_diff_K", *LT_COLS]]

    eq = out[(out.lat >= -1) & (out.lat <= 1)][LT_COLS].to_numpy()
    print(f"rows {len(out)}  赤道 平均最高 {eq.max(1).mean():.1f}K "
          f"平均最低 {eq.min(1).mean():.1f}K （Williams+2017: 392.3 / 94.3）")

    if "--write" in sys.argv:
        out.to_csv(OUT, index=False, compression="gzip")
        print(f"wrote {OUT}")
    else:
        print("--write で data/diviner_global.csv.gz を更新")


if __name__ == "__main__":
    main()
