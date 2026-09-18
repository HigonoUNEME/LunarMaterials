# tools/ — データ前処理スクリプト

`data/*.csv` は公開データを教材用に前処理した派生物です。ここに、生データ（PDS の IMG、
Zenodo の RAR、UCLA の xyz、USGS のシェープファイル等）から `data/` の CSV を作る手順を置きます。
取得元 URL・値の復元式・検証結果は [`../data/SOURCES.md`](../data/SOURCES.md) にまとめています。

| スクリプト | 生成物 | 状態 |
|---|---|---|
| `build_slope.py` | `lola_polar_illumination.csv` の `slope_deg` 列 | ✅ 動作確認済み（生データを自動DL。`--write` で反映。中央値 8.0°） |
| `build_diviner_curve.py` | `diviner_global.csv.gz` | ✅ 動作確認済み。**committed 版と全259,200点で 0.1 K 以内・平均 0.005 K の差**、Williams+2017 と赤道で 2% 以内。UCLA サーバは TLS が古く curl へ自動フォールバック |
| `build_diviner_nighttime.py` | `diviner_nighttime.csv.gz` | ✅ 動作確認済み（生データDL→整形）。Tycho 周辺の夜の異常が全球平均より明確に高い（+10.7 K）、古い海はほぼ 0 |
| `build_isochron.py` | `isochron_reference.csv` | ✅ 計算のみ（Neukum PF＋編年関数、DL 無し）。雨の海の一区画で年代 ~3.5 Ga を再現 |
| `build_site_environment.py` | `site_environment.csv`（`slope_deg` 以外） | ✅ **DL 無し**。既存の `moon_geology_grid` ＋ `diviner_global`／`diviner_nighttime` を 1°グリッドで結合し、正午の太陽高度・地球の仰角を幾何計算。Apollo 11 `earth_elev +66°`／Chang'e 4 `−44°`／Shackleton `+0°` を照合、物理チェックをアサート（要件 v3.2 R1）。`_cache/ldem_16.img` があれば末尾で `build_global_slope.py` を呼ぶ |
| `build_global_slope.py` | `site_environment.csv` の `slope_deg` 列 | ✅ 動作確認済み（要件 v3.3 I6）。LOLA GDR 全球標高 `ldem_16.img`（33MB、自動DL、curl フォールバック）から傾斜を計算し 1°セル平均。海 ≈ 1.0°／陸 ≈ 5.9°（「海は平ら」を数値化）、`\|lat\|≥85°` は NaN。**`build_site_environment.py --write` の後に実行** |
| `check_consistency.py` | （検査のみ） | 層をまたぐ不整合の検出（要件 v3.3 I7）。`--execute` で全ノートブックの nbconvert も。CI 前段・編集後に流す |
| `build_template.py` | （ひな形） | 新しいデータを足すときにコピーする骨格。`docs/customize_guide.md` 参照 |
| `build_geology_grid.py` | `moon_geology_grid.csv` | ✅ **committed 版と区分・相対年代が完全一致**（海 15.7%）。USGS 統合地質図 GIS zip（約214MB）の `GeoUnits.shp` を `--shp` で。geopandas 必要 |
| `build_lola_illum.py` | `lola_polar_illumination.csv` の日照 2 列 | ✅ **committed 版と日照率・永久影率が 100% 一致**（差の中央値 0）。IMG 4 枚（各51MB）を自動DL。傾斜 `slope_deg` は別工程（`build_slope.py`） |
| `build_crater_catalogs.py` | `craters_subset.csv` / `craters_3d.csv` / `deepcraters.csv` | ✅ **3つとも committed 版と一致**（Robbins は .shp のポイント座標＝円フィット中心を使う。件数 36,377 / 24,982 / 18,996）。生カタログを `--robbins`（Catalog_Moon_Release…zip の .shp）/ `--wangwu`（RAR 展開後の .txt）/ `--deep`（figshare CSV、committed とバイト一致）で渡す |

`data/landing_sites.csv`・`data/maria_boundaries.csv`・`data/candidate_regions.csv`・`data/lunar_pits.csv`
は手キュレーション（公表座標・文献値の書き写し）で、専用スクリプトはありません。出典は SOURCES.md を参照。

生データのキャッシュは `tools/_cache/`（gitignore）に置かれます。成果物の `data/*.csv` はコミットします。

## 依存

```
pip install numpy pandas          # build_slope.py, build_diviner_curve.py, build_crater_catalogs.py
pip install geopandas             # build_geology_grid.py
```

## 再現の考え方

**6本すべて、生データから committed の `data/*.csv` を再生成できることを確認済み**
（2026-09-04、`requirements_v3.1.md` N6 完了）。生データは大きい（合計 1.5 GB 超）ので
`tools/_cache/` は gitignore し、成果物の `data/*.csv` だけコミットする。
教材の主張（データを鵜呑みにしない）を、前処理の完全な可視化で裏づける。

| スクリプト | committed との一致 |
|---|---|
| build_slope.py | 検算（クレーター床4〜6°・縁17°）＋分布一致 |
| build_diviner_curve.py | 全259,200点で 0.1 K 以内・平均 0.005 K |
| build_diviner_nighttime.py | Tycho +10.7 K・静かの海 ~0（文献照合） |
| build_geology_grid.py | 区分・相対年代が 100% 一致 |
| build_lola_illum.py | 日照率・永久影率が 100% 一致（差の中央値 0） |
| build_crater_catalogs.py | 3カタログとも件数・属性が一致（位置は float 精度） |
