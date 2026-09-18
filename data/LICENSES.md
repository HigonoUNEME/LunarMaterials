# データセットのライセンスと出典

このフォルダの CSV は、公開されている月の観測データを**教材用に前処理した派生物**です。
リポジトリのコードは Apache-2.0 ですが、データにはそれぞれ元データのライセンスが適用されます。
取得元 URL と前処理の手順は [SOURCES.md](SOURCES.md) にまとめています。

## 教材が使う10ファイル

| ファイル | ライセンス | 出典・帰属 |
|---|---|---|
| `craters_subset.csv` | パブリックドメイン（NASA PDS ＝ CC0 相当／USGS ＝ 米政府著作物） | Robbins, S. J. (2018), *A New Global Database of Lunar Impact Craters >1–2 km: 1. Crater Locations and Sizes…*, JGR Planets 123, 871–892. NASA PDS Cartography and Imaging Sciences Node Annex / USGS Astrogeology 経由で配布 |
| `craters_3d.csv` | **CC BY 4.0**（https://creativecommons.org/licenses/by/4.0/ ） | Wang, Y., Wu, B., Xue, H., Li, X., & Ma, J. (2021), *An improved global catalog of lunar impact craters (≥1 km) with 3D morphometric information and updates on global crater analysis*, JGR Planets 126, e2020JE006728. データ：Zenodo https://doi.org/10.5281/zenodo.4983248 |
| `deepcraters.csv` | **CC BY 4.0**（https://creativecommons.org/licenses/by/4.0/ ） | Yang, C., Zhao, H., Bruzzone, L., Benediktsson, J. A., Liang, Y., Liu, B., Zeng, X., Guan, R., Li, C., & Ouyang, Z. (2020), *Lunar impact crater identification and age estimation with Chang'E data by deep and transfer learning*, Nature Communications 11, 6358. データ：figshare https://doi.org/10.6084/m9.figshare.12768539 （ファイル `Aged_Lunar_Crater_Database_DeepCraters_2020(1).csv`） |
| `diviner_global.csv.gz` | パブリックドメイン（NASA ミッションデータ ＝ 既定 CC0） | LRO Diviner チーム（UCLA）の level-4 ラスタ製品 `diviner_tbol_snapshot_{000..345}E.xyz`。科学的背景：Williams, J.-P., Paige, D. A., Greenhagen, B. T., & Sefton-Nash, E. (2017), *The global surface temperatures of the Moon…*, Icarus 283, 300–325 |
| `diviner_nighttime.csv.gz` | パブリックドメイン（NASA ミッションデータ ＝ 既定 CC0） | LRO Diviner チーム（UCLA）の level-4 製品 `diviner_tbol_min.xyz` ／ `diviner_tbol_min_anom.xyz`。科学的背景：Williams ほか (2017) ／ 原理は Bandfield et al. (2011), *Lunar surface rock abundance and regolith fines temperatures…*, JGR 116 |
| `isochron_reference.csv` | 計算値（式の出典を明記） | Neukum, G., Ivanov, B. A., & Hartmann, W. K. (2001), *Cratering records in the inner solar system…*, Space Science Reviews 96, 55–86。生産関数＋編年関数から教材側で計算（`tools/build_isochron.py`）。ダウンロードは無い |
| `lola_polar_illumination.csv` | パブリックドメイン（NASA ミッションデータ ＝ 既定 CC0） | LRO LOLA チーム（NASA GSFC / MIT）。日照率：Mazarico, E. ほか (2011), *Illumination conditions of the lunar polar regions using LOLA topography*, Icarus 211, 1066–1081（`imbrium.mit.edu`）。傾斜 `slope_deg`：LOLA GDR bidirectional slope（LDSM, 240 m 基線, PDS Geosciences Node） |
| `moon_geology_grid.csv` | パブリックドメイン（USGS 刊行物） | Fortezzo, C. M., Skinner, J. A., Jr., & Hunter, M. A. (2020), *Unified Geologic Map of the Moon*, USGS Scientific Investigations Map 3316（1:5,000,000） |
| `landing_sites.csv` | パブリックドメイン（NASA / USGS 座標） | Wagner, R. V. ほか (2017), *Coordinates of anthropogenic features on the Moon*, Icarus 283（Apollo/Luna/Surveyor）／各ミッション公表値（Chang'e 4–6, Chandrayaan-3）／NASA Artemis III candidate regions (2024)／USGS Gazetteer（参照地形）。手キュレーション |
| `maria_boundaries.csv` | パブリックドメイン（米政府著作物＋IAU 公式命名） | USGS / IAU Gazetteer of Planetary Nomenclature（planetarynames.wr.usgs.gov） |

## この教材で加えた改変（CC BY 4.0 の「改変の表示」要件のため）

- **`craters_3d.csv`**：元データ（LU1319373、約132万件）から **直径10 km 以上に絞り込み**、列名を
  日本語教材向けに変更（`Longitude→lon` 等）、`depth/diameter` 比の列を追加、CSV 化。値そのものは未加工。
- **`deepcraters.csv`**：元データの Aged サブセット（`Age` 列つき 18,996 件）を抽出。列は元のまま、CSV 形式も同じ。
- **`craters_subset.csv`**：Robbins DB から教材用に緯度経度・直径・形状（離心率・扁平率等）の列を抽出。
- **`diviner_global.csv.gz`**：24 枚の瞬間温度マップを現地時間で位相整列し、地点ごとに
  現地時間 0〜23 時の温度カーブ（`t_lt00`〜`t_lt23`）に再構成。0.5°グリッド 259,200 点、gzip 圧縮。
  ※極付近（|緯度| > 70°）は整列手法が退化するため信頼性が落ちる。
- **`diviner_nighttime.csv.gz`**：`diviner_tbol_min.xyz`・`diviner_tbol_min_anom.xyz` を
  `lon, lat` で結合。列名を `temp_min_K`・`temp_min_anomaly_K` に。259,200 点、gzip 圧縮。
- **`lola_polar_illumination.csv`**：日照率＝PDS3 IMG（60 m/pixel）を約1 km ブロック平均し極ステレオ座標を
  緯度経度に逆変換。傾斜 `slope_deg`＝LOLA GDR LDSM（`DN×0.0015+45`、DN=0 は欠測）を同じ点に順投影で
  読み、5×5 画素平均。|緯度|>89.3° は欠測。日照率・傾斜とも**絶対値は文献と単純比較しない**。
- **`moon_geology_grid.csv`**：USGS 統合地質図のポリゴンを 1°グリッド（64,800 点）に空間結合し、
  相対年代（`relative_age`）、その数値版（`age_index` 1〜5）、海／陸（`区分`）を付与。
- **`landing_sites.csv`**：公表座標を1つの表に集約（29 件）。座標そのものは未加工。
- **`isochron_reference.csv`**：Neukum の生産関数＋編年関数から年代ごとのクレーター密度を計算した表（17 行）。
- **`site_environment.csv`**：`moon_geology_grid.csv`（USGS）と `diviner_global`／`diviner_nighttime`（NASA/UCLA）を
  1°グリッドで結合し、正午の太陽高度・地球の仰角を幾何計算で足した派生物（64,800 行）。新規観測なし。
  `slope_deg`・`elev_m` 列は LOLA GDR 全球標高 `ldem_16.img`（PDS Geosciences Node、NASA/LRO、
  パブリックドメイン）由来の派生物。`slope_deg` は傾斜を計算（基線 ≈ 1.9 km、|lat|≥85° は NaN、相対指標）、
  `elev_m` は同じ標高データを1°セル平均しただけ（基準球 R=1737.4km からの高さ[m]、極域も欠測なし）。
- **`candidate_regions.csv`**：候補地域8件の緯度経度の箱と理由・弱点（手キュレーション）。座標は USGS/IAU と各ミッション文献。
- **`lunar_pits.csv`**：溶岩チューブ天窓7件の座標・寸法。Wagner & Robinson (2014) Icarus 237 ほかの公表値を手入力（座標は事実）。

## 保持のみ（どのノートブックからも参照していない）

| ファイル | ライセンス | 備考 |
|---|---|---|
| `moon_ephemeris.csv` | パブリックドメイン（NASA JPL HORIZONS） | 地球ー月の距離・位相角の時系列。優先度3・未採用（requirements_v1.3 §7.2）。配布ビルド（webapp）には含めていない |

（`moon_earth_correlation.csv`〈月齢×地震〉は、科学的妥当性への疑義により requirements_v1.4 で
コアスコープから除外され、2026-09-04 にこのフォルダからも削除した。）

## クレジットのお願い

CC BY 4.0 のデータ（`craters_3d.csv`・`deepcraters.csv`）を使った成果物では、上記の著者・出典・
ライセンスを明記してください。パブリックドメインのデータ（NASA・USGS・JPL 由来）も、学術上の慣行として
出典の明記を推奨します。取得元 URL と前処理・検証の詳細は [SOURCES.md](SOURCES.md) を参照。

3D入口ページ（`webapp/react/`）が表示する約38の「代表地点」は、上記の観測データとは別の、
有名地点を紹介するための概略データです（`docs/explorer_data_verification.md` に検証記録）。
