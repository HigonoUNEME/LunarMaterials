# -*- coding: utf-8 -*-
"""data/site_environment.csv を作る（要件 v3.2 R1）。

「月面基地の最適地」を **南極以外の場所でも同じ土俵で** 評価できるようにするための、
全球 1度グリッドの環境指標。**新規ダウンロードなし。** 既存データの結合と幾何計算だけ。

入力（すべて data/ にある既存ファイル）:
  moon_geology_grid.csv     … 1度グリッド。海/陸（区分）・相対年代（age_index）
  diviner_global.csv.gz     … 0.5度グリッド。地点ごとの現地時間 0〜23時の温度カーブ
  diviner_nighttime.csv.gz  … 0.5度グリッド。夜の最低温度

出力列:
  lat, lon                  … 1度グリッドの中心
  区分                       … 海 / 陸（USGS 統合地質図ベース。おおまかな「平ら/でこぼこ」の一次指標）
  age_index                 … 相対地質年代 1（古）〜5（新）
  relative_age              … 地質系統名
  temp_max_K, temp_min_K    … 1日の温度カーブの最大・最小（セル内の 0.5度点の平均）
  temp_amp_K                … その差（＝熱ストレス。赤道で大・極で小）
  night_min_K               … 夜の最低温度（セル平均）
  noon_sun_elev_deg         … 90 − |緯度|（正午の太陽高度の近似。発電量と熱負荷の代理）
  night_length_days         … 会合月の半分 ≒ 14.77 日（|lat|<=85）。極域は topography 依存なので NaN
  slope_deg                 … 全球の傾斜 [度]（LOLA LDEM_16、基線 ≒ 1.9km、|lat|<85）。
                              tools/build_global_slope.py が付与する（唯一のダウンロードあり。--write 後に実行）。
                              この列だけは新規 DL を伴うので、無くても他の列は成立する。
  earth_elev_deg            … 地球の仰角 ≒ 90 − 角距離(sub-Earth点)。正=表側、負=裏側（電波静穏）

注意（教材で必ず伝える）:
  - temp_* の曲線の形は |lat|>70° で退化するが、最大・最小の包絡は「昼どれだけ熱く・夜どれだけ
    冷えるか」の目安には使える。絶対値の文献比較はしない。
  - noon_sun_elev_deg / night_length_days は地形を無視した幾何近似。極の連続日照・永久影は
    lola_polar_illumination.csv（極域日照）を見る。
  - earth_elev_deg は秤動（±約7°）を無視した平均。|earth_elev_deg| < 10° は「地球が地平線近く」。

使い方:
    python tools/build_site_environment.py            # 検証だけ
    python tools/build_site_environment.py --write     # data/site_environment.csv を書き出す
"""
import argparse
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SYNODIC_MONTH_DAYS = 29.53
POLE_CUTOFF_DEG = 85.0  # これより極寄りは night_length の単純モデルが崩れる


def _cell_center(v: pd.Series) -> pd.Series:
    """0.5度グリッドの座標を、それを含む 1度セルの中心（*.5）に丸める。"""
    return np.floor(v) + 0.5


def build() -> pd.DataFrame:
    geo = pd.read_csv(DATA / "moon_geology_grid.csv")
    div = pd.read_csv(DATA / "diviner_global.csv.gz")
    night = pd.read_csv(DATA / "diviner_nighttime.csv.gz")

    lt_cols = [f"t_lt{h:02d}" for h in range(24)]
    div["_tmax"] = div[lt_cols].max(axis=1)
    div["_tmin"] = div[lt_cols].min(axis=1)
    div["clat"] = _cell_center(div["lat"])
    div["clon"] = _cell_center(div["lon"])
    dagg = (div.groupby(["clat", "clon"])[["_tmax", "_tmin"]]
            .mean().reset_index()
            .rename(columns={"clat": "lat", "clon": "lon",
                             "_tmax": "temp_max_K", "_tmin": "temp_min_K"}))
    dagg["temp_amp_K"] = dagg["temp_max_K"] - dagg["temp_min_K"]

    night["clat"] = _cell_center(night["lat"])
    night["clon"] = _cell_center(night["lon"])
    nagg = (night.groupby(["clat", "clon"])["temp_min_K"]
            .mean().reset_index()
            .rename(columns={"clat": "lat", "clon": "lon", "temp_min_K": "night_min_K"}))

    out = geo[["lat", "lon", "区分", "age_index", "relative_age"]].copy()
    out = out.merge(dagg, on=["lat", "lon"], how="left")
    out = out.merge(nagg, on=["lat", "lon"], how="left")

    # --- 幾何計算 ---
    lat_r = np.radians(out["lat"].to_numpy())
    lon_r = np.radians(out["lon"].to_numpy())
    out["noon_sun_elev_deg"] = (90.0 - out["lat"].abs()).round(2)

    out["night_length_days"] = np.where(
        out["lat"].abs() <= POLE_CUTOFF_DEG, round(SYNODIC_MONTH_DAYS / 2, 2), np.nan)

    # sub-Earth 点を (0,0) とみなす。ある地点から見た地球の仰角 ≒ 90° − 角距離
    ang = np.degrees(np.arccos(np.clip(np.cos(lat_r) * np.cos(lon_r), -1.0, 1.0)))
    out["earth_elev_deg"] = (90.0 - ang).round(2)

    for c in ("temp_max_K", "temp_min_K", "temp_amp_K", "night_min_K"):
        out[c] = out[c].round(1)

    out = out.sort_values(["lat", "lon"]).reset_index(drop=True)
    return out


def _nearest(df, lat, lon):
    d = (df["lat"] - lat) ** 2 + (((df["lon"] - lon + 180) % 360 - 180)
                                  * np.cos(np.radians(lat))) ** 2
    return df.iloc[int(d.values.argmin())]


def verify(df: pd.DataFrame) -> None:
    print(f"行数: {len(df)}  列: {list(df.columns)}")
    print(f"欠測: temp_amp_K {df['temp_amp_K'].isna().sum()}  "
          f"night_min_K {df['night_min_K'].isna().sum()}  "
          f"night_length_days {df['night_length_days'].isna().sum()}（|lat|>85 のセル）")
    print()
    checks = [
        ("Apollo 11 (赤道・表側)", 0.674, 23.473),
        ("Chang'e 4 (裏側)", -45.44, 177.60),
        ("Shackleton (南極点)", -89.67, 0.0),
        ("Aristarchus 高原 (中緯度・表側)", 24.5, -48.0),
        ("静かの海 (赤道の海)", 8.5, 31.4),
    ]
    for name, la, lo in checks:
        r = _nearest(df, la, lo)
        print(f"{name:28s} 区分={r['区分']}  temp_amp={r['temp_amp_K']:.0f}K  "
              f"night_min={r['night_min_K']:.0f}K  noon_sun={r['noon_sun_elev_deg']:.0f}°  "
              f"earth_elev={r['earth_elev_deg']:+.0f}°")
    print()
    print("期待: Apollo11 earth_elev ~ +66°／Chang'e4 earth_elev 負（裏側）／"
          "Shackleton earth_elev ~ 0°・temp_amp 小／赤道 temp_amp ~ 290K")

    # 物理チェック
    eq = df[df["lat"].abs() <= 5]
    pole = df[df["lat"] <= -85]
    assert eq["temp_amp_K"].mean() > 250, eq["temp_amp_K"].mean()
    assert pole["temp_amp_K"].mean() < eq["temp_amp_K"].mean()
    assert (df[df["lon"].abs() < 60]["earth_elev_deg"] > 0).mean() > 0.9
    assert (df[df["lon"].abs() > 120]["earth_elev_deg"] < 0).mean() > 0.9
    print("\n物理チェック OK（赤道で日較差大／裏側で earth_elev 負／表側で正）")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    df = build()
    verify(df)

    if args.write:
        path = DATA / "site_environment.csv"
        df.to_csv(path, index=False, encoding="utf-8")
        print(f"\nwrote {path}  ({path.stat().st_size:,} B)")
        # 全球傾斜列（LDEM_16 が tools/_cache にあれば付け直す。無ければスキップ）
        import subprocess
        slope_script = pathlib.Path(__file__).resolve().parent / "build_global_slope.py"
        if (slope_script.parent / "_cache" / "ldem_16.img").exists():
            subprocess.run([sys.executable, str(slope_script), "--write"], check=True)
        else:
            print("（slope_deg 列は未付与。tools/build_global_slope.py --write で足せます）")


if __name__ == "__main__":
    main()
