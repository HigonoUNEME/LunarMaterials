# -*- coding: utf-8 -*-
"""月の「海」の正確な輪郭（mare_outline.npz）を1回だけ作る前処理スクリプト。

NASA SVS「CGI Moon Kit」の LROC カラーモザイク（実写・測光補正済み）4k をダウンロードし、
アルベド（明るさ）でしきい値をかけて暗い＝玄武岩の海の領域を取り出す。個別の暗いクレーターや
南極エイトケン盆地の暗い床などを除くため、USGS 地名辞典の23の海の中心を含む連結成分だけを残す。
結果の輪郭を緯度経度のポリラインとして `docs/mare_outline.npz` に保存する（約50KB）。

    pip install scikit-image
    python docs/build_mare_outline.py

以後、build_seminar_figs.py はこの npz を読むだけ（4k 画像の再取得は不要）。
"""
import pathlib
import urllib.request

import numpy as np
import pandas as pd
from scipy import ndimage as ndi
from skimage import measure
from skimage.filters import threshold_otsu
from skimage.morphology import closing, disk, opening, remove_small_holes, remove_small_objects

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
MOSAIC_URL = "https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_poles_4k.tif"
CACHE = HERE / "_lroc_color_4k.tif"


def main() -> None:
    if not CACHE.exists():
        print(f"ダウンロード: {MOSAIC_URL}")
        urllib.request.urlretrieve(MOSAIC_URL, CACHE)
    import matplotlib.pyplot as plt
    im = plt.imread(str(CACHE))
    g = im[..., :3].mean(axis=2).astype(float)
    H, W = g.shape
    print(f"モザイク {W}x{H}")

    # 行ごとの中央値でゆるやかな緯度方向の明るさ勾配を除去
    g_flat = g - ndi.gaussian_filter1d(np.median(g, axis=1), 60)[:, None] + np.median(g)
    gg = ndi.gaussian_filter(g_flat, 3)
    thr = threshold_otsu(gg) - 4
    m = gg < thr
    m = opening(m, disk(3))
    m = closing(m, disk(6))
    m = remove_small_holes(m, area_threshold=3000)
    m = remove_small_objects(m, min_size=400)

    # 23の海の中心を含む連結成分だけ残す
    maria = pd.read_csv(ROOT / "data" / "maria_boundaries.csv")
    lab, n = ndi.label(m)
    keep = set()
    for _, mm in maria.iterrows():
        r = int((90 - mm.center_lat) / 180 * (H - 1))
        c = int((mm.center_lon + 180) / 360 * (W - 1))
        win = lab[max(0, r - 8):r + 8, max(0, c - 8):c + 8]
        keep.update(v for v in np.unique(win) if v > 0)
    mask = closing(np.isin(lab, list(keep)), disk(3))
    print(f"連結成分 {n} → 海の中心を含む {len(keep)} 個  面積割合 {mask.mean() * 100:.1f}%")

    # 輪郭をポリラインに
    sm = ndi.gaussian_filter(mask.astype(float), 2.0)
    polys = []
    for ct in measure.find_contours(sm, 0.5):
        if len(ct) < 40:
            continue
        ct = ct[::3]
        lat = 90 - ct[:, 0] / (H - 1) * 180
        lon = -180 + ct[:, 1] / (W - 1) * 360
        polys.append(np.column_stack([lon, lat]).astype(np.float32))
    out = HERE / "mare_outline.npz"
    np.savez_compressed(out, **{f"p{i}": p for i, p in enumerate(polys)})
    print(f"wrote {out}  ({out.stat().st_size:,} B, {len(polys)} 本, "
          f"{sum(len(p) for p in polys)} 点)")


if __name__ == "__main__":
    main()
