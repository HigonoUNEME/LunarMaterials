# -*- coding: utf-8 -*-
"""新しいデータを教材に足すときの前処理スクリプトのひな形。
これをコピーして tools/build_<name>.py を作る。docs/customize_guide.md 参照。

    1. 取得元 URL と値の復元式を docstring に書く（ライセンスも）
    2. fetch → 整形 → 検証（文献値や既知の地点と照合）→ --write
    3. data/<name>.csv を作ったら moonkit.DATASETS に1行足す

    python tools/build_template.py            # 検証のみ
    python tools/build_template.py --write     # data/<name>.csv を作る
"""
import argparse
import pathlib
import shutil
import subprocess
import urllib.request

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = pathlib.Path(__file__).resolve().parent / "_cache"
OUT = ROOT / "data" / "CHANGE_ME.csv"          # ← 出力名
SRC_URL = "https://example.org/CHANGE_ME"       # ← 取得元


def fetch(url: str, dest: pathlib.Path) -> None:
    """urllib で取り、失敗したら curl にフォールバック（古い TLS 対策）。"""
    dest.parent.mkdir(exist_ok=True)
    if dest.exists():
        return
    print(f"download {url}")
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception:
        if shutil.which("curl") is None:
            raise
        subprocess.run(["curl", "-sS", "--max-time", "180", "-o", str(dest), url], check=True)


def load_raw() -> pd.DataFrame:
    raw = CACHE / "CHANGE_ME.raw"
    fetch(SRC_URL, raw)
    # 例：ASCII の「lon lat value」なら
    a = np.loadtxt(raw)
    return pd.DataFrame({"lon": a[:, 0], "lat": a[:, 1], "value": a[:, 2]})


def shape(df: pd.DataFrame) -> pd.DataFrame:
    """列名を教材の約束に合わせる：緯度経度は 'lat' / 'lon'、経度は -180..180。
    値は必要なら丸める。座標は丸めない（結合が壊れる）。"""
    df = df.copy()
    df["lon"] = ((df["lon"] + 180) % 360) - 180
    df["value"] = df["value"].round(3)
    return df[["lat", "lon", "value"]]


def verify(df: pd.DataFrame) -> None:
    """既知の地点・文献値と照合する（ここを必ず書く）。"""
    print(f"rows {len(df)}  value 中央値 {df['value'].median():.3g}")
    # 例：near = df[(df.lat.between(-45,-41)) & (df.lon.between(-13,-9))]  # Tycho
    #     print("Tycho 付近の平均:", near['value'].mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    df = shape(load_raw())
    verify(df)
    if args.write:
        df.to_csv(OUT, index=False)
        print(f"wrote {OUT}")
    else:
        print("--write で data/ に書き出す")


if __name__ == "__main__":
    main()
