# -*- coding: utf-8 -*-
"""月球儀に重ねる「1日の温度アニメーション」フレームを作る（地球の風 Phase3）。

data/diviner_global.csv.gz（0.5度グリッド・地点ごとの現地時間0〜23時カーブ）から、
「太陽直下点の経度」を24通りにスイープしたときの全球温度マップを24枚焼く。
入口ページの「太陽光照射角」スライダーと同じ角度規約（sunAngle）で、
どのフレームを表示すればよいかを JS 側で計算できるよう、各フレームの
太陽直下点経度もメタデータに書き出す。作り方は notebooks 側の
paper_figs.py / make_figures.py の diurnal GIF と同じ考え方（このスクリプトはその3D版）。

    python webapp/react/scripts/gen_diurnal_frames.py

出力：webapp/react/public/textures/diurnal/frame_00.png 〜 frame_23.png
      webapp/react/src/data/diurnalFrames.generated.json
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(ROOT, "data")
REACT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_OUT = os.path.join(REACT, "public", "textures", "diurnal")
JSON_OUT = os.path.join(REACT, "src", "data", "diurnalFrames.generated.json")
os.makedirs(TEX_OUT, exist_ok=True)

N_FRAMES = 24     # 15度刻み（t_lt00〜23 の分解能に合わせる）
CMAP = "coolwarm"  # 「熱い=赤、冷たい=青」の直感に合わせる（overlay の温度系レイヤーと統一）
VMIN, VMAX = 25.0, 400.0   # 全フレーム共通の範囲（フレームごとに正規化すると温度差の比較ができなくなる）


def _gradient_css(cmap_name: str, n: int = 8) -> str:
    """凡例バー用の CSS linear-gradient を、実際に使うカラーマップから生成する
    （gen_overlay_textures.py と同じ考え方。値がずれないよう画像と同じ計算式で作る）。"""
    cmap = matplotlib.colormaps[cmap_name]
    stops = []
    for i in range(n):
        r, g, b, _ = cmap(i / (n - 1))
        stops.append(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
    return "linear-gradient(to right, " + ", ".join(stops) + ")"


def _temp_cube():
    """(lat, lon, 24) の立方体を作る。webapp/react/scripts 版（make_figures.py と同じロジック）。"""
    df = pd.read_csv(os.path.join(DATA, "diviner_global.csv.gz"))
    lt_cols = [f"t_lt{h:02d}" for h in range(24)]
    lons = np.sort(df["lon"].unique())
    lats = np.sort(df["lat"].unique())[::-1]     # 北→南
    cube = np.full((len(lats), len(lons), 24), np.nan)
    li = {v: i for i, v in enumerate(lons)}
    la = {v: i for i, v in enumerate(lats)}
    ix = df["lon"].map(li).to_numpy()
    iy = df["lat"].map(la).to_numpy()
    for k, c in enumerate(lt_cols):
        cube[iy, ix, k] = df[c].to_numpy()
    return lats, lons, cube


def main() -> None:
    lats, lons, cube = _temp_cube()
    LON, _LAT = np.meshgrid(lons, lats)
    n_lat, n_lon = len(lats), len(lons)

    meta = {
        "nFrames": N_FRAMES, "cmap": CMAP, "min": VMIN, "max": VMAX,
        "unit": "K", "label": "1日の温度（アニメーション）",
        "desc": "太陽直下点の動きに合わせて温度分布が変わる。「月の自転」スライダーか自動回転で進める。",
        "source": "data/diviner_global.csv.gz",
        "gradientCss": _gradient_css(CMAP),
        "frames": [],
    }

    for f in range(N_FRAMES):
        sub_lon = -180.0 + 360.0 * f / N_FRAMES        # 太陽直下点の経度
        loc = (12.0 + (LON - sub_lon) / 15.0) % 24.0    # 各画素の現地時間
        lo = np.floor(loc).astype(int) % 24
        frac = loc - np.floor(loc)
        rows = np.arange(n_lat)[:, None]
        cols = np.arange(n_lon)[None, :]
        T = (1 - frac) * cube[rows, cols, lo] + frac * cube[rows, cols, (lo + 1) % 24]

        norm = np.clip((T - VMIN) / (VMAX - VMIN), 0, 1)
        rgba = (matplotlib.colormaps[CMAP](norm) * 255).astype(np.uint8)

        from PIL import Image
        path = os.path.join(TEX_OUT, f"frame_{f:02d}.png")
        Image.fromarray(rgba, mode="RGBA").save(path)
        meta["frames"].append({
            "index": f, "subsolarLon": round(sub_lon, 1),
            "texture": f"textures/diurnal/frame_{f:02d}.png",
        })
        print(f"wrote {path}  ({os.path.getsize(path)/1024:.0f} KB)  subsolarLon={sub_lon:+.1f}")

    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    total_kb = sum(os.path.getsize(os.path.join(TEX_OUT, m["texture"].split("/")[-1]))
                   for m in meta["frames"]) / 1024
    print(f"wrote {JSON_OUT}  (frames total {total_kb:.0f} KB)")


if __name__ == "__main__":
    main()
