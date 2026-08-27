# 月データ探索教材（仮称）

高校生が、月に関する3つの公開データセットを自由に組み合わせながら、
「気になる関係」を自分で見つけ出す探究教材。

> **スコープの原則（Ver.1.0）**：このリポジトリの現行実装（第2章のDS-1〜3）は、以下の3つに固定する。
> 追加のデータセット（LOLA・LAMP・LEND・生の衛星画像 等）は、Ver.1.0の範囲には含めない。
>
> **Ver.2.1での改訂**：拡張フェーズの要件定義を [docs/requirements_v2.1.md](docs/requirements_v2.1.md) にまとめた。
> 協議の結果、LOLA由来データの利用を正式に許可し、DS-4〜8のうちDS-4〜8すべて（DS-4/5/6/7/8）を
> 実データで検証・実装済み。DS-4（クレーター深さ）・DS-7（南極日照）の実装には、この検証環境への
> Python・7-Zipの追加インストールが必要だったため、その都度ユーザーの許可を得て導入した
> （生徒側の実行環境には影響しない。詳細はrequirements_v2.1.md §0.1）。

---

## 1. 目的

- 前処理済みの公開データのみを使い、Python環境の専門的な構築（GDAL等）を必要としない
- 生徒に単一の決まった問い（例：「直径と深さの関係」）を一方向に解かせるのではなく、
  **複数の変数を自由に選び、自分の気になる組み合わせを探索する**形にする
- 情報Ⅰの範囲（散布図・基本統計量・簡単な条件分岐）を超えない

## 2. 使用するデータセット（3つに固定）

| # | データセット名 | 提供元 | 得られる情報 | 想定形式 |
|---|---|---|---|---|
| 1 | Robbins Lunar Crater Database (2018) | USGS Astrogeology | 緯度・経度・直径・形状（離心率／扁平率）。**深さは含まれない（後述）** | CSV（実測：全量1,296,796件・約238MB。教材用は直径8km以上でフィルタリングし36,377件・約2.8MBに圧縮） |
| 2 | LRO Diviner 温度データ | UCLA Diviner Team（PDS由来データの低解像度ラスタープロダクト。詳細は下記） | 正午の温度・深夜0時の温度・緯度経度・昼夜温度差 | 元は.xyz（ASCII）。全球0.5度グリッド（720×360=259,200点）を1つのCSVに変換済み（約10.2MB） |
| 3 | DeepCraters Lunar Craters Database (2020) | Figshare (Chen Yang & Renchu Guan) | 推定地質年代（1=Pre-Nectarian 〜 5=Copernican のインデックス） | CSV（実測：18,996件・約0.85MB。件数は報告書記載どおりだが、サイズは報告書記載の約6.47MBではなく約0.85MBだった） |

### 検証結果（着手時に確認済み）

- [x] **DeepCraters**：Figshare (doi: 10.6084/m9.figshare.12768539) の `Aged_Lunar_Crater_Database_DeepCraters_2020(1).csv` を取得。件数は報告書どおり18,996件・6カラム（`Flags_data, ID, Lat, Lon, Diam_km, Age`）。ただしファイルサイズは実測873,823バイト（約0.85MB）で、報告書記載の約6.47MBとは一致しなかった（報告書側の誤記と判断）。経度は-180〜180度。
- [x] **Diviner**：NASA PDS Geosciences Nodeの正規アーカイブ（GCPプロダクト）は緯度帯ごとに1ファイル約156MB（0.5度×0.25時間ビン、月統計期間分）で、「低解像度」という条件を満たす製品が存在しないことが判明。代わりに、同じDivinerチーム（UCLA、Williams et al. 2017）が公開している**0.5 ppd（0.5度グリッド）の全球ラスタープロダクト**（`diviner_tbol_hour12.xyz`＝正午、`diviner_tbol_hour00.xyz`＝深夜0時、各約7.7MB）を採用し、2ファイルを結合して`diviner_global.csv`を作成した。そのため提供元はPDS Geosciences Nodeそのものではなく、**UCLA Diviner Lunar Radiometer Experimentチームの公開データ**である点に注意（データの取得元がNASA PDSアーカイブの一次データそのものである点は変わらない）。経度は-180〜180度。
- [x] **Robbins DB**：USGS Astropedia（CKAN経由、PDS4形式のzipアーカイブ、約91.77MB/96,227,201バイト）を取得・展開。実カラムは`CRATER_ID, LAT_CIRC_IMG, LON_CIRC_IMG, LAT_ELLI_IMG, LON_ELLI_IMG, DIAM_CIRC_IMG, ...`など21列で、**深さ（Depth）を表す列は存在しない**。直径8km以上（36,377件）に絞り、`lat, lon, diam_km, diam_major_km, diam_minor_km, eccentricity, ellipticity, rim_arc_fraction`の9列・約2.8MBに整形。経度は元データが0〜360度だったため、-180〜180度に変換した。
- [x] **座標系の統一**：Robbins DBのみ0〜360度だったため-180〜180度に変換し、3データセットとも-180〜180度に統一した。

### 判明した重要な差分（教材設計への影響）

- **「クレーターの直径と深さの関係」という問いは、この3データセットでは検証できない。** Robbins Lunar Crater Databaseには深さのカラムが無いため。第3章の「問いの例」からは削除し、代わりに「直径と離心率・扁平率（真円度）の関係」を候補にした（`notebooks/explore.ipynb`・`docs/worksheet.pdf`に反映済み）。

## 3. 教材の設計方針

- **単一の設問形式ではなく、探索ツール形式にする**。生徒がX軸・Y軸に使う変数を選べるUI
  （プルダウンやチェックボックス）を用意し、選んだ組み合わせで散布図が描画される
- 生徒自身の「気になる」を出発点にするため、最初に予想を書かせる前に、まず自由に触らせる
  時間を設ける（第4章の「教材の実施形態」を参照）
- 迷った生徒向けに、以下の「問いの例」をヒントとして選択式で提示する（正解として提示しない）

### 問いの例（ヒントとして提示する候補）

> 2026-08-27時点：実データ確認の結果、Robbins DBに深さ（Depth）の列が存在しないことが判明した
> （代わりにVer.2.1でWang & Wu 2021の深さ付きカタログ`craters_3d.csv`を追加し、1番として復活させた）。

1. クレーターの直径と深さの関係（`craters_3d.csv`, Wang & Wu 2021）
2. クレーターの直径と、離心率・扁平率（＝どれくらい丸いか）の関係（Robbins DB）
3. クレーターの空間密度（緯度経度分布のかたより）
4. 緯度と正午の温度の関係
5. 同一地点の昼夜の温度差（正午と深夜0時の温度差）
6. クレーターの推定年代と、直径・分布との関係（DeepCraters追加により可能）
7. 月の南極で太陽光発電に向いた場所を探す（日照率が高く永久影の少ない場所、Ver.2.1で追加）

## 4. リポジトリ構成

```
repo/
├── README.md                        このファイル
├── data/
│   ├── craters_subset.csv           Robbins DBから直径8km以上を抽出・整形（36,377件・約2.8MB）
│   ├── diviner_global.csv           Diviner正午/深夜0時温度、全球0.5度グリッド（259,200件・約10.2MB）
│   ├── deepcraters.csv              DeepCratersの年代付きクレーターデータ（18,996件・約0.85MB）
│   ├── maria_boundaries.csv         月の海・大洋23件の中心座標（USGS地名辞典、Ver.2.1で追加）
│   ├── moon_ephemeris.csv           地球ー月の距離・視直径等、過去5年日次（JPL HORIZONS、Ver.2.1で追加）
│   ├── moon_earth_correlation.csv   月齢・理論潮汐力・地震件数、過去5年日次（Ver.2.1で追加）
│   ├── craters_3d.csv               クレーターの直径・深さ（Wang & Wu 2021、直径10km以上・24,982件・約1.1MB、Ver.2.1で追加）
│   └── lola_south_pole_illumination.csv  月南極の平均日照率・永久影割合、約1kmグリッド（78,961件・約2.3MB、Ver.2.1で追加）
├── notebooks/
│   ├── explore.ipynb                標準編（情報Ⅰ範囲、Colab起動を主に想定）
│   └── explore_advanced.ipynb       発展編（scipy.stats等、Ver.2.1で追加）
├── docs/
│   ├── worksheet.pdf                紙のワークシート（予想を書く欄・考察欄）
│   └── requirements_v2.1.md         拡張版の要件定義書（データ検証結果を含む）
├── requirements.txt                 ローカル実行用
└── .gitignore
```

上記は着手時点（2026-08-27）で実際に構築済みの状態。

## 5. 実行環境

- 主：Google Colaboratory（「Open in Colab」ボタンでブラウザのみで起動）
- 従：ローカル環境（Jupyter／VSCode、`requirements.txt`で環境構築）
- 変数選択のUIは `ipywidgets` を使用し、コードを直接書かなくても操作できるようにする

## 6. 学習指導要領との対応（概要）

- 情報Ⅰ：(4)データの収集・整理・分析／(3)モデル化とシミュレーション
- 地学基礎：(2)変動する地球　宇宙、太陽系と地球の誕生

## 7. 明示的にスコープ外とするもの

- Ver.1.0時点：LOLA・LAMP・LEND等、他のLRO搭載機器のデータ（Ver.2.1でLOLAのみ許可に改訂、[docs/requirements_v2.1.md](docs/requirements_v2.1.md)参照）
- LAMP・LENDのデータ（Ver.2.1でも引き続きスコープ外）
- 生の衛星画像（GeoTIFF等）そのものの直接表示・処理（前処理済みラスタ→グリッドCSV化までは許容）
- 外部APIへのライブ接続、バックエンドサーバーの構築・運用（事前に1回だけ取得した静的CSVとして配布する）
- 機械学習・AIによる予測（今後の展望として報告書にのみ記述し、本教材には実装しない）

## 8. 今後の展望（本教材には含まないが、報告書に記述する内容）

- Ver.2.1で拡張予定のデータセット（クレーター深さ・マリア分布・天体暦・極域日照・月齢×地球環境）の
  詳細は [docs/requirements_v2.1.md](docs/requirements_v2.1.md) を参照
- 修士研究（TSUKIMIのñ(T)データ、PINNs）との接続による発展的な教材化
