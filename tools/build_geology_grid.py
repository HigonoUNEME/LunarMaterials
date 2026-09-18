# -*- coding: utf-8 -*-
"""USGS 統合地質図（ポリゴン）を格子グリッドに空間結合し、
data/moon_geology_grid.csv （既定は1度、64,800点）を作る。

    pip install geopandas
    python tools/build_geology_grid.py --shp <GeoUnits.shp のパス> --write
    python tools/build_geology_grid.py --shp <GeoUnits.shp のパス> --step 0.25 \
        --out webapp/react/scripts/_cache/moon_geology_grid_fine.csv --write
        （地質年代レイヤーの空間解像度を上げたいとき。--step で1度より細かいグリッドを作り、
         --out で別ファイルに出す＝既存の data/moon_geology_grid.csv（site_environment.csv が
         使う1度グリッド・教材として配布するCSV）はそのまま。細かいほうは表示用の中間生成物
         （64MB超と大きい・再現可能）なので data/ ではなく _cache/ に置き、コミットしない。
         gen_overlay_textures.py の age_index だけがこちらを読み、焼き上がった PNG だけを配布する）

元データ（パブリックドメイン, USGS 刊行物）:
  Fortezzo, C. M., Skinner, J. A., Jr., & Hunter, M. A. (2020),
  Unified Geologic Map of the Moon, USGS Scientific Investigations Map 3316, 1:5,000,000.
  GIS 一式（約224MB）を USGS からダウンロードし、`GeoUnits` レイヤ（12,247 ポリゴン、
  月固有の正距円筒図法）の .shp を --shp で渡す。
  ダウンロード先: https://asc-astropedia.s3.us-west-2.amazonaws.com/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2.zip
  （展開後 Lunar_GIS/Shapefiles/GeoUnits.shp）

処理:
  1. step度グリッド（既定1度=180×360）の各セル中心を作る
  2. ポリゴンの CRS に投影して point-in-polygon（sjoin）
  3. relative_age = 属性 FIRST_Un_1（地質系統名）、age_index = 1..5 に数値化、
     区分/terrain_type = FIRST_Un_2 に "Mare" を含むか

検証（2026-09-04 時点、1度グリッドでの出力）:
  面積重み（cos緯度）つきの海の割合 15.7%（文献値 約16%、表側 29%）。
  age_index 面積重み平均 海 3.16 / 陸 2.38（＝海のほうが若い）。
"""
import argparse
import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent

AGE_INDEX = {
    "Pre-Nectarian": 1, "Nectarian": 2, "Imbrian-Nectarian": 2.5, "Imbrian": 3,
    "Eratosthenian-Imbrian": 3.5, "Eratosthenian": 4, "Copernican": 5,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shp", required=True, help="GeoUnits.shp のパス")
    ap.add_argument("--step", type=float, default=1.0, help="グリッド間隔[度]（既定1.0）")
    ap.add_argument("--out", default=None, help="出力先（既定 data/moon_geology_grid.csv）")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    out_path = pathlib.Path(args.out) if args.out else ROOT / "data" / "moon_geology_grid.csv"

    import geopandas as gpd
    from shapely.geometry import Point

    units = gpd.read_file(args.shp)
    # CRS は Moon2000 正距円筒（メートル、球半径 1737400）。Earth と混ざるので pyproj 変換はせず、
    # 定義式 x = R·λ, y = R·φ（λ,φ ラジアン）で直接グリッド点を作る。
    R = 1737400.0
    step = args.step
    lat = np.arange(-90 + step / 2, 90, step)
    lon = np.arange(-180 + step / 2, 180, step)
    la, lo = np.meshgrid(lat, lon, indexing="ij")
    xm = np.deg2rad(lo.ravel()) * R
    ym = np.deg2rad(la.ravel()) * R
    grid = gpd.GeoDataFrame(
        {"lat": la.ravel(), "lon": lo.ravel()},
        geometry=[Point(x, y) for x, y in zip(xm, ym)],
        crs=units.crs,
    )

    keep_cols = [c for c in ("FIRST_Un_1", "FIRST_Un_2", "UnitName", "Age") if c in units.columns]
    joined = gpd.sjoin(grid, units[keep_cols + ["geometry"]],
                       how="left", predicate="within")
    joined = joined[~joined.index.duplicated(keep="first")].sort_index()
    out = pd.DataFrame({
        "lat": joined["lat"].to_numpy(),
        "lon": joined["lon"].to_numpy(),
        "relative_age": joined["FIRST_Un_1"].fillna("Unknown").to_numpy(),
        "unit_detail": joined["FIRST_Un_2"].fillna("").to_numpy(),
    })
    out["age_index"] = out["relative_age"].map(AGE_INDEX)
    out["terrain_type"] = np.where(
        joined["FIRST_Un_2"].fillna("").str.contains("Mare"), "Mare", "Highland")
    out["区分"] = np.where(out["terrain_type"] == "Mare", "海", "陸")
    out = out[["lat", "lon", "relative_age", "age_index", "terrain_type", "区分", "unit_detail"]]

    w = np.cos(np.radians(out["lat"]))
    print(f"rows {len(out)}  海の面積割合(面積重み) {w[out['区分'] == '海'].sum() / w.sum():.3f}"
          f"  （文献値 約0.16）")

    if args.write:
        out.to_csv(out_path, index=False)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
