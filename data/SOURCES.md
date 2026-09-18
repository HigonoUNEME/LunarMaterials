# データの取得元と前処理

`data/` の CSV は、下記の公開データを教材用に前処理した派生物です。
生データ（IMG・RAR・xyz・シェープファイル等）と前処理スクリプトはリポジトリに含めていません
（サイズが大きく、GDAL 等の専門環境を要するため）。ここに「どこから何を取り、どう処理したか」を残します。
ライセンスは [LICENSES.md](LICENSES.md) を参照。

前処理の実施環境（このリポジトリを作る側の作業。生徒は不要）：
Python 3.12 ＋ numpy / pandas / geopandas、7-Zip 26.x。詳細な判断根拠は `docs/requirements_v1.3.md`〜`v1.5.md`。

---

## craters_subset.csv ← Robbins Lunar Crater Database (2018)

- **取得元**：NASA PDS / USGS Astrogeology（`tools/build_crater_catalogs.py --robbins`）
  `https://asc-astropedia.s3.us-west-2.amazonaws.com/Moon/Research/Craters/Ancillary/Catalog_Moon_Release_20180815_shapefile180.zip`
  （約137MB。展開後 `Catalog_Moon_Release_20180815_1kmPlus_180.shp` に 1,296,796 クレーター）
- **前処理**：**位置は .shp のポイント座標**（円フィット中心、-180〜180°）。属性から
  `DIAM_C_IM`（円直径 km）・`D_E_MA_IM`/`D_E_MI_IM`（楕円長短径 km）・`D_E_EC_IM`（離心率）・
  `D_E_ELP_IM`（扁平率）・`ARC_IMG`（リム弧率）を取り、
  `crater_id, lat, lon, diam_km, diam_major_km, diam_minor_km, eccentricity, ellipticity, rim_arc_fraction`
  に整形。**直径 8 km 以上**に絞り込み（**36,377 件**）。値そのものは未加工。
- **検証**：`build_crater_catalogs.py` の出力が committed の全列と一致（位置は float 精度）。

## craters_3d.csv ← Wang & Wu (2021) LU1319373

- **取得元**：Zenodo `https://zenodo.org/records/4983248/files/LU1319373_Wang%26Wu_2021.rar`
  （25.3 MB。7-Zip で展開し `LU1319373_Wang & Wu_2021.txt` 約74MB。16 行のヘッダ＋タブ区切り、
  列 `ID, Longitude, Latitude, Diameter(m), Depth(m), Source, Source_lon, Source_lat, Source_dia`）
- **前処理**（`tools/build_crater_catalogs.py --wangwu`）：**直径 10 km 以上に絞り込み**（→ 24,982 件）、
  m を km に換算、経度を -180〜180 に、`crater_id, lat, lon, diameter_km, depth_km, depth_diameter_ratio`
  に整形。`depth_km ≤ 0` は 20 件のみ残る（超巨大古代盆地。出典 README 記載の「浸食が進んだクレーターでは
  ガウスフィット精度が落ちる」という既知の手法限界。データ破損ではない）。
- **d/D 中央値**：全体 0.069／10–15 km 帯 0.077。これは劣化後の**現在の深さ**で、教科書の
  「単純クレーター d/D ≒ 0.2」とは別物（`detailed_design_v3.md §2.4`）。
- **検証**：`build_crater_catalogs.py` の出力が committed の全列と一致（丸め・float 精度の範囲）。

## deepcraters.csv ← Yang, Zhao, Bruzzone ほか (2020) CE_DeepCraters

- **取得元**：figshare `https://doi.org/10.6084/m9.figshare.12768539`
  ファイル `Aged_Lunar_Crater_Database_DeepCraters_2020(1).csv`
  （姉妹レコード `10.6084/m9.figshare.12765986` にも同一ファイルがある。GitHub `hszhaohs/DeepCraters` も参照）
- **前処理**：Aged サブセット（`Age` 列つき、**18,996 件**）をそのまま採用。
  列 `Flags_data, ID, Lat, Lon, Diam_km, Age`。`Age` は 1（最古）〜5（最新）の地質系統区分。

## diviner_global.csv.gz ← LRO Diviner（UCLA チーム level-4）

- **取得元**：`http://luna1.diviner.ucla.edu/~jpierre/diviner/level4_raster_data/diviner_tbol_snapshot_XXXE.xyz`
  XXX = subsolar 経度 `000`〜`345`（15° 刻み、計 24 枚）。ASCII、`lon lat T_bol[K]`、各 0.5° グリッド・約6.7MB、計約161MB。
  ※このサーバは TLS 設定が古く（`DH_KEY_TOO_SMALL`）、新しめの Python/OpenSSL では接続に失敗することがある。
  ブラウザ、`curl --ciphers DEFAULT@SECLEVEL=1`、または古い環境で取得する。
- **前処理**：各地点について 24 枚から現地時間 0〜23 時の温度カーブを構成。
  現地時間 = `(12 + (経度 − subsolar経度)/15) mod 24`、整数時に円環線形補間。
  成果物 `lon, lat, temp_noon_K, temp_midnight_K, temp_diff_K, t_lt00…t_lt23`、259,200 点、gzip 約14MB。
  `temp_noon_K = t_lt12`、`temp_midnight_K = t_lt00`。
- **検証**：赤道帯の平均最高 390.5 K・平均最低 95.6 K・較差 294.9 K は Williams et al. (2017) の
  392.3 / 94.3 K・約290–298 K と一致（`docs/data_redistribution_review.md §4`）。
  **|緯度| > 70° は位相整列が退化して振幅が過大に出る**（既知の限界。教材は緯度帯比較を 60° で打ち切り、
  極域は LOLA 日照データに切り替えている）。

## diviner_nighttime.csv.gz ← LRO Diviner（UCLA チーム level-4）　― 2026-09-04 追加

- **取得元**：`https://luna1.diviner.ucla.edu/~jpierre/diviner/level4_raster_data/`
  `diviner_tbol_min.xyz`（夜の最低温度、0.5 ppd、`lon lat T[K]`）＋
  `diviner_tbol_min_anom.xyz`（その緯度平均を引いた異常、K。「熱物性に対応」と製品説明にあり、Williams+2017 を参照）。
  ※TLS が古く urllib は失敗しうる → `tools/build_diviner_nighttime.py` は curl にフォールバック。
- **前処理**：2 ファイルを `lon, lat` で結合。`temp_min_K`・`temp_min_anomaly_K`（259,200 点、gzip）。
- **意味**：夜、岩塊の多い地形は熱をためて冷めにくい（熱慣性大）＝周りより暖かい＝ `temp_min_anomaly_K` が正。
  Bandfield et al. (2011) の岩石量マップと同じ原理の代理指標。
- **検証**：Tycho（月で最も新しい大クレーター）周辺の異常が全球平均より明確に高い（周辺3°平均 +10.7 K、
  中心近傍は +30 K 超）。Copernicus・Aristarchus も正。古い平らな海（静かの海）はほぼ 0。
- **用途**：`notebooks/explore_clustering.ipynb` の B（場所の夜のふるまいでクラスタリング → 「周りと違う場所」の発見）。

## lola_polar_illumination.csv ← LRO LOLA（MIT チーム ＋ PDS GDR）

**列**：`lat, lon, average_illumination_percent, permanent_shadow_fraction, slope_deg`、157,922 点。

### 日照率・永久影率（average_illumination_percent, permanent_shadow_fraction）

- **取得元**：`http://imbrium.mit.edu/BROWSE/EXTRAS/ILLUMINATION/`
  南極：`AVGVISIB_85S_060M_201608.IMG`（平均日照率、60 m/pixel、5058×5058、約51MB）＋
  `LPSR_85S_060M_201608.IMG`（永久影マスク）。北極：`AVGVISIB_85N_060M` ＋ `LPSR_85N_060M`。
  いずれも PDS3 バイナリラスタ（LSB 符号付き16bit整数）、南極／北極ステレオ図法、球体半径 1737.4 km。
- **前処理**：18×18 ピクセル（約1.08 km 四方）でブロック平均し、極ステレオ座標 (x,y) を緯度経度に逆変換。
  緯度変換式は画像四隅の ρ から求めた最大緯度が PDS3 ラベルの `MAXIMUM_LATITUDE = -82.9°` と一致することで検証。
  南北を結合して1ファイルに（緯度の符号で区別）。
- **注意**：日照率の**絶対値は文献と単純比較しない**（Mazarico et al. 2011 の手法と新しい高解像度 DTM 解析で
  差が出る。既知のクレーター Shackleton・Shoemaker では illumination=0 を再現でき、明暗の順序は信頼できる）。

### 傾斜（slope_deg）― 2026-09-04 追加

- **取得元**：LOLA GDR（PDS Geosciences Node、パブリックドメイン）
  `https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/`
  `ldsm_75s_240m.img/.lbl`（南極 75–90°S、双方向傾斜、基線 240 m、極ステレオ、3812×3812、LSB int16、約29MB）＋
  `ldsm_75n_240m.img/.lbl`（北極）。
- **値の復元**：`slope_deg = DN × 0.0015 + 45`（`DN == 0` は no-data）。
- **前処理**（`tools/build_slope.py`）：既存の 157,922 点の各 (lat, lon) を極ステレオに順投影
  （ISIS PolarStereographic 準拠、`LINE/SAMPLE_PROJECTION_OFFSET = 1905.60874…`）し、
  5×5 ピクセル（約 1.2 km）平均。**|緯度| > 89.3° はトラック収束ノイズのため NaN**（全体の 1.5%）。
- **検算**：クレーター床（Shoemaker 4.0°、de Gerlache 4.8°、Haworth 5.7°）は平坦、
  山塊・クレーター縁（Malapert 8.0°、Amundsen 縁 17.3°）は急。中央値 8.0°、四分位 5.3–12.3°。
- **注意**：GDR 由来の LOLA 軌道トラックに沿った縞アーティファクトが残る。South Pole-Aitken 盆地の
  縁で本来起伏が大きく、値は文献の地域平均よりやや高め。**日照率と同じく「相対的な起伏の指標」**として使う。

## maria_boundaries.csv ← USGS / IAU Gazetteer

- **取得元**：`https://planetarynames.wr.usgs.gov/`（月の全命名地形 KMZ）
- **前処理**：`type` が「Mare, maria」または「Oceanus, oceani」の項目 23 件（Oceanus Procellarum 含む）を抽出。
  中心座標と近似半径。成果物 23 行。ステップ2の `near_maria`（円近似）で使う。
  ※円近似の「海の割合」は約19%で、下記 USGS 地質図の面積重み 16% より大きい（円が海岸線の外の陸を含むため）。
  教材ではこの差自体を「近似の限界」の題材にする。

## moon_geology_grid.csv ← USGS Unified Geologic Map of the Moon　― 2026-09-04 に凍結解除

- **取得元**：`https://asc-astropedia.s3.us-west-2.amazonaws.com/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2.zip`
  （約214MB。Fortezzo, C. M., Skinner, J. A., Jr., & Hunter, M. A. (2020), *Unified Geologic Map of
  the Moon*, USGS Scientific Investigations Map 3316、1:5,000,000）。展開後
  `Lunar_GIS/Shapefiles/GeoUnits.shp`。パブリックドメイン（USGS 刊行物）。
- **前処理**（`tools/build_geology_grid.py --shp GeoUnits.shp`）：CRS は Moon2000 正距円筒（メートル、
  球半径 1737400）。Earth と混ざるため pyproj 変換はせず、定義式 x=R·λ, y=R·φ でグリッド点を作る。
  `geopandas` の `sjoin` で 1° グリッド（180×360 = 64,800 点）に point-in-polygon 空間結合。
  属性 `FIRST_Un_1`（地質系統名）→ `relative_age` ／ `FIRST_Un_2` に "Mare" を含むか → `区分`（海/陸）。
- **検証**：`build_geology_grid.py` の出力が committed の `区分`・`relative_age` と 100% 一致。
  `relative_age`＝ポリゴン属性 `FIRST_Un_1`（Pre-Nectarian〜Copernican および遷移期）。
  `age_index`＝1（最古）〜5（最新）の数値化。`terrain_type`／`区分`＝`FIRST_Un_2` に「Mare」を含むかで判定。
- **検証（2026-09-04）**：**面積重み（cos 緯度）つきの海の割合 = 15.7%**（文献値 約16%、表側 29% と整合。
  裏側 2.3%）。海は Imbrian 84% ＋ Eratosthenian 16%、Nectarian 以前はゼロ。
  陸は Pre-Nectarian〜Imbrian に広く分布。面積重み平均 age_index は 海 3.16・陸 2.38 で、
  **海のほうが系統的に若い**（Hiesinger らの海の玄武岩年代 3.1–3.9 Ga、LHB 後の高地地殻と整合）。
- **用途**：ステップ2/6 で、クレーターの数から推定した「海は新しい」を USGS 公式地質図と**答え合わせ**する。

---

## 保持のみ（webapp 配布ビルドには含めない・ノートブックからも参照しない）

- **moon_ephemeris.csv** ← NASA JPL HORIZONS API `https://ssd.jpl.nasa.gov/api/horizons.api`
  （QUANTITIES=10,13,20,24、過去5年・日次。`distance_km` は AU×149,597,870.7）。1,827 行。

`moon_earth_correlation.csv`（USGS 地震 FDSN ＋ HORIZONS、月齢×地震件数）は
科学的妥当性への疑義により requirements_v1.4 でコアスコープから除外され、2026-09-04 に削除した。

## isochron_reference.csv ← 計算値（2026-09-04 追加、発展編）

- **内容**：17 行。`age_Ga, N_ge_1km_per_Mkm2, N_ge_8km_per_Mkm2, N_ge_20km_per_Mkm2`。
  「その年代の地面なら、直径 D 以上のクレーターが 100 万 km² あたり何個あるはず」。
- **計算**：Neukum 生産関数（12 次多項式、Neukum, Ivanov & Hartmann 2001）＋ 月の編年関数
  `N(1,T) = 5.44e-14·(exp(6.93·T) − 1) + 8.38e-4·T`。参照面（~1 Ga）の PF を N(1,T)/N(1,ref) で
  スケール。式は `data/build`（下記）に記録：
  ```python
  a = [-3.0876, -3.557528, 0.781027, 1.021521, -0.156012, -0.444058,
       0.019977, 0.086850, -0.005874, -0.006809, 8.25e-4, 5.54e-5]
  npf_logN(D) = sum(a[n] * log10(D)**n for n in range(12))
  N_ge(D, T)  = 10**npf_logN(D) * chrono_N1(T) / 10**a[0]
  ```
- **検証**：雨の海の一区画（緯度 22–42、経度 −35〜−8）で D≥8km を数えて密度→年代 ≈ **3.5 Ga**
  （文献：Hiesinger らの雨の海の玄武岩 3.3–3.6 Ga と整合）。`notebooks/explore_advanced.ipynb §B`。
- **ライセンス**：参考文献に基づく計算値。式の出典（Neukum et al. 2001）を明記すること。

## landing_sites.csv ← 手キュレーション（2026-09-04 追加）

- **内容**：29 行。`name, kind, lat, lon, terrain, year, note`。
  Apollo 11–17（有人）、Luna 16/17/20/21/24、Surveyor 1/3/5/6/7、Chang'e 3/4/5/6、Chandrayaan-3、
  Artemis III 南極候補地 4 件、参照地形（Shackleton・Copernicus・Tycho・Tsiolkovskiy）。
- **座標の出典**：Wagner, R. V. ほか (2017), *Coordinates of anthropogenic features on the Moon*, Icarus 283
  （Apollo/Luna/Surveyor）／各ミッションの公表値（Chang'e 4–6, Chandrayaan-3）／
  NASA Artemis III candidate regions（2024）／USGS 地名辞典（参照地形）。すべてパブリックドメイン。
- **検証**：29 件中 25 件で `terrain` 列（海／陸）が USGS 地質図の分類と一致。不一致 4 件はいずれも
  「高地の盆地の中の玄武岩の床」（Chang'e 4/6）または海岸線上（Copernicus）で、注記を調整済み。
- **用途**：グリッドの分析結果を「実在の場所」に結びつける（例：選んだ南極最適地と Artemis 候補地の比較）。

## site_environment.csv ← 既存データの結合＋幾何計算（2026-09-07 追加・要件 v3.2 R1）

- **目的**：「月面基地の最適地」を **南極以外の場所でも同じ土俵で** 評価できるようにする全球 1°グリッド
  （64,800 行）。教材が南極に誘導されすぎている問題（requirements_v3.2）への対処。
- **入力（`区分`〜`earth_elev_deg` は既存の `data/` ファイルのみ。新規ダウンロードなし）**：
  `moon_geology_grid.csv`（区分・age_index・relative_age）／`diviner_global.csv.gz`（0〜23時カーブの
  最大・最小・差を 1°セル平均）／`diviner_nighttime.csv.gz`（夜の最低温度を 1°セル平均）。
- **列**：`区分, age_index, relative_age, temp_max_K, temp_min_K, temp_amp_K, night_min_K,
  noon_sun_elev_deg（=90−|lat|）, night_length_days（会合月の半分≒14.77日。|lat|>85° は NaN）,
  earth_elev_deg（=90 − 角距離(sub-Earth点(0,0))。正＝表側、負＝裏側）,
  slope_deg（全球の傾斜。下記の LDEM_16 由来。|lat|≥85° は NaN）,
  elev_m（標高。下記の LDEM_16 由来。基準球 R=1737.4km からの高さ[m]、極域含め欠測なし）`。
- **生成**：`tools/build_site_environment.py --write`（`区分`〜`earth_elev_deg`）→
  `tools/build_global_slope.py --write`（`slope_deg` を追記）→
  `tools/build_global_elevation.py --write`（`elev_m` を追記。2026-09-18 追加）。
- **`slope_deg`・`elev_m` の元データ（2026-09-07 追加・requirements_v3.3 I6。**唯一のダウンロードを伴う列**）**：
  LOLA GDR 全球標高 `ldem_16.img`（16 pix/度・5760×2880・LSB int16・標高[m]=DN×0.5、
  等緯度経度・中心経度180°、33 MB）
  https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/ldem_16.img
  （PDS Geosciences Node、NASA/LRO、パブリックドメイン）。各画素の双方向傾斜（緯度で東西距離を補正）を
  atan(|∇z|) で求め、16×16 画素を 1°セルに平均。基線 ≈ 1.9 km。極域の傾斜は
  `lola_polar_illumination.csv` の `slope_deg`（240m 基線・極ステレオ投影）を使う。
  海の平均 ≈ 1.0°／陸の平均 ≈ 5.9°（＝「海は平ら」を数値で裏づけ）。「相対的な起伏の指標」。
  `elev_m` は同じ標高データをそのまま 1°セル平均しただけ（傾斜と違い緯度微分をしないので極域も
  欠測にしていない）。海の平均 ≈ −2117m／陸の平均 ≈ −306m／全体の最小 ≈ −8176m（南極エイトケン盆地
  付近）・最大 ≈ +9102m。
- **検証**（同スクリプト）：Apollo 11 `earth_elev ≈ +66°`／Chang'e 4（裏側）`earth_elev ≈ −44°`／
  Shackleton `earth_elev ≈ 0°・temp_amp ≈ 150K`／赤道 `temp_amp ≈ 290–300K`。
  物理チェック（赤道で日較差大／裏側で earth_elev 負／表側で正）をアサーションで確認。
- **注意（教材で必ず伝える）**：`temp_*` の曲線の形は |lat|>70° で退化する（最大・最小の包絡は目安には
  使える）。`noon_sun_elev_deg` / `night_length_days` は地形無視の幾何近似で、極の連続日照・永久影は
  `lola_polar_illumination.csv` を見ること。`earth_elev_deg` は秤動（±約7°）を無視した平均。

## candidate_regions.csv ← 手キュレーション（2026-09-07 追加・要件 v3.2 R3）

- **内容**：8 行。`name, lat_min, lat_max, lon_min, lon_max, rationale, caveat`。
  赤道の海（静かの海）／危機の海／中緯度の火砕丘（Aristarchus 高原）／嵐の大洋／
  裏側・南極エイトケン（フォン・カルマン）／裏側・赤道（電波天文の候補域）／
  南極（Shackleton-de Gerlache）／溶岩チューブ天窓（Marius Hills）。
- **出典**：緯度経度の箱は USGS/IAU 地名辞典の座標と各ミッション・構想（Artemis III / LCRT /
  Chang'e 4,6 ほか）に基づく手キュレーション。`moonkit.region_type(df, name)` で切り出す。
- **用途**：`site_environment` を地域タイプ単位で切り出し、目的別に `site_score` する（course ステップ4）。

## lunar_pits.csv ← 文献値の手キュレーション（2026-09-07 追加・要件 v3.2 R4）

- **内容**：7 行。`name, lat, lon, host_terrain, opening_m, depth_m, note`。
  Marius Hills Pit・Mare Tranquillitatis Pit・Mare Ingenii Pit（裏側）・Lacus Mortis Pit ほか。
- **出典**：Wagner, R. V. & Robinson, M. S. (2014), *Distribution, formation mechanisms, and
  significance of lunar pits*, Icarus 237, 52–63 ／ Robinson, M. S. ほか (2012), Planet. Space Sci. 69 ／
  Lunar Pit Atlas (LROC/ASU)。**座標・寸法は論文の公表値を数件手入力**（全アトラスの再配布はしない）。
  座標そのものは事実なので二次配布の問題はない。
- **用途**：「放射線・微隕石・熱を遮蔽できる長期滞在拠点」というミッションを成立させる
  （地下空洞に通じる可能性のある地点）。
