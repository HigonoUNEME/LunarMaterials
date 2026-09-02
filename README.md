# 月データ探索教材

高校生が、月の公開データ（クレーター・温度・極域日照）を使って
**情報Ⅰの範囲（散布図・基本統計量・条件分岐）でデータ分析を体験する**探究学習教材。

## ▶ ブラウザで開く（インストール不要）

**https://\<ユーザー名\>.github.io/\<リポジトリ名\>/**

Python もデータもブラウザ内で動く（JupyterLite / Pyodide）。初回だけ 1〜2 分かかる。
重い計算をしたいときは Colab / ローカルでも同じノートブックが動く（下記）。

- GDAL 等の専門環境は不要。
- 「総合的な探究の時間」や「情報Ⅰ」で、**データ分析を通した探究**として活用できる。
  実授業での試行と改善は今後の課題。
- 開発の経緯と設計判断は `docs/requirements_v1.5.md`（3層構成）／`v1.6.md`（弱点対処）／
  `v1.7.md`（Web アプリ化）にまとめている（v1.0〜v1.4 の履歴も `docs/` に残す）。

---

## 3層構成

教材は「共有の土台」と「二つの届け方」に分かれている。

```
┌───────────────────────────┬───────────────────────────┐
│ 層2a  ガイド型（探究講座）    │ 層2b  オープン型（プチ探究） │
│  1コマ完結・クラス全体      │  数週間・選択した班         │
│  強い足場                  │  弱い足場                  │
│  手順固定のノートブック＋    │  課題ブリーフ＋チートシート  │
│  ワークシート＋進行表       │  ＋指導者メモ＋出発点        │
│  ゴール：ムーンベース最適地  │  問い・提案は生徒が決める    │
│  （任意）ステップ6：ML比較  │  自由探索ツール explore     │
├───────────────────────────┴───────────────────────────┤
│ 層1  解析ヘルパー  moonkit.py（十数個の関数・各数行・機械学習なし）│
├───────────────────────────────────────────────────────┤
│ 層0  共有データ基盤（CSV 5種・座標統一・月面画像）          │
└───────────────────────────────────────────────────────┘
```

| | 層2a ガイド型 | 層2b オープン型 |
|---|---|---|
| 足場 | 強い（`# ★ここを変える` の数値だけ書き換え） | 弱い（データと道具のみ） |
| 時間 | 1コマ（150〜180分）で完走 | 数回に分けて（導入 → 追究 → 発信） |
| 対象 | クラス全体 | 選択した少人数のグループ |
| 設計根拠 | 「解析体験」型チュートリアル | 石田(2022) の主体性 |

---

## リポジトリ構成

```
repo/
├── data/                              層0：共有データ基盤（下表の5種＋保持のみ4種）
├── notebooks/
│   ├── moonkit.py                     層1：解析ヘルパー（機械学習なし）
│   ├── moonkit_ml.py                  任意ステップ6：モデル比較（scikit-learn）
│   ├── course_moonbase.ipynb          層2a：ガイド型（ステップ1〜5）
│   ├── course_moonbase_ml.ipynb       任意ステップ6のノートブック
│   ├── petit_inquiry_start.ipynb      層2b：オープン型の最小の出発点
│   ├── explore.ipynb                  自由探索ツール（変数選択式の散布図）
│   ├── explore_advanced.ipynb         発展編（numpy.polyfit のべき乗則フィット）
│   └── assets/                        日本語フォント・月面背景画像
├── docs/
│   ├── requirements_v1.5.md           要件定義（3層構成・機械学習の限定解禁）
│   ├── requirements_v1.6.md           要件定義（模擬授業前の弱点対処）
│   ├── requirements_v1.7.md           要件定義（Web アプリ化）
│   ├── requirements_v1.2〜1.4.md       履歴
│   ├── requirements_v2.1.md           データ検証の技術記録
│   ├── worksheet_course.html / .pdf   層2a：生徒用ワークシート
│   ├── teacher_guide_course.md        層2a：指導者用の進行表
│   ├── petit_inquiry_brief.md         層2b：課題ブリーフ
│   ├── petit_inquiry_helpersheet.html / .pdf   層2b：ヘルパー チートシート
│   ├── petit_inquiry_mentor_notes.md  層2b：指導者用メモ
│   ├── worksheet.pdf                  旧・自由探索用ワークシート
│   └── report_v2.html / .pdf          教材の解説（2ページ）
├── webapp/                            ブラウザ版（JupyterLite）の組み立てスクリプト
│   ├── assemble.py                    notebooks+data+assets → 配布用 content/
│   ├── bootstrap_template.py          各ノートブックに足す「準備」セル
│   └── index.html                     トップページ
├── .github/workflows/deploy-pages.yml push のたびに GitHub Pages にデプロイ
├── requirements.txt                   ローカル実行用
└── run_notebook.bat                   ローカルで Jupyter を起動（Windows）
```

---

## 使い方

- **主：ブラウザ**（上記の GitHub Pages URL）。インストール不要。`webapp/README.md` 参照。
- **従1：Google Colaboratory**。ノートブックの「Open in Colab」から起動し、冒頭セルで
  リポジトリを `git clone` する（`data/` と `notebooks/` が一緒に来る）。追加インストール不要。
- **従2：ローカル**（Jupyter / VSCode）。`pip install -r requirements.txt`。

どのノートブックでも、最初に `from moonkit import *` を実行してから使う。
ヘルパーの一覧は [`docs/petit_inquiry_helpersheet.pdf`](docs/petit_inquiry_helpersheet.pdf) を参照。

---

## データセット（層0・5種）

| `load()` キー | 内容 | 出典 |
|---|---|---|
| `'クレーター'` | 緯度経度・直径・形（離心率・扁平率）。36,377個（直径8km以上） | Robbins Lunar Crater Database, USGS [3] |
| `'クレーター深さ'` | 直径・深さ・深さ÷直径比。24,982個（直径10km以上） | Wang & Wu 2021 [4] |
| `'クレーター年代'` | 推定地質年代（1〜5）。18,996個 | DeepCraters, figshare [5] |
| `'温度'` | 地点ごとの現地時間0〜23時の温度カーブ。259,200地点（全球0.5度） | LRO Diviner, UCLA [6] |
| `'極域日照'` | 平均日照率・永久影率。157,922地点（南北緯82.96〜90度） | LOLA, Mazarico et al. 2011 [7] |
| （`maria_boundaries.csv`） | 23の海・大洋の中心座標と半径。**ステップ2の `near_maria` 分類にのみ使用**（`load()` の選択肢には出さない） | USGS 地名辞典 |

**データの注意（教材に明記）**
- 温度カーブが信頼できるのは概ね **緯度 ±70度より低い**範囲（極付近は「昼夜」が成立しない）。
  極域の基地判断は温度ではなく LOLA の日照データで行う（要件 `docs/requirements_v1.6.md` §2）。
- 日照率の絶対値（○○%）は他文献と単純比較しない。「暗い／明るい」の順序のみ信頼する。
- `moon_earth_correlation.csv` / `moon_ephemeris.csv` / `moon_geology_grid.csv` は
  `data/` に残すが、教材からは参照しない（経緯は `docs/requirements_v1.4.md` §9）。

---

## 学習指導要領との対応

- 情報Ⅰ：(4) データの収集・整理・分析／(3) モデル化とシミュレーション
- 地学基礎：(2) 変動する地球　宇宙、太陽系と地球の誕生
- 任意ステップ6（機械学習の比較）は情報Ⅱの先取り・発展に位置づける。

## 明示的にスコープ外とするもの

- 生の衛星画像（GeoTIFF 等）の直接処理、GIS 操作（前処理済みグリッド CSV までは許容）
- 外部 API へのライブ接続、バックエンドサーバー（Web アプリは静的ファイルのみ）
- KNIME・PCA/K-means 等による自動分類パイプライン（「今後の展望」に記載）
- 機械学習は層2a の任意ステップ6（`moonkit_ml.py`）に限る。層1 は機械学習を含まない。

---

## 出典

1. 文部科学省, 高等学校学習指導要領（平成30年告示）解説 情報編 (2018)。
2. 石田光宏, 高等学校「課題探究型授業」における天文分野の調査結果, 天文教育 34(2) (2022)。
3. Robbins, S. J., *A New Global Database of Lunar Impact Craters*, JGR Planets, 124 (2019)。
4. Wang, Y., Wu, B., *An improved global catalog of lunar impact craters (≥1 km) with 3D morphometric information*, JGR Planets, 126 (2021)。Zenodo: 10.5281/zenodo.4983248 (CC BY 4.0)。
5. Yang, C., Guan, R. ほか, *CE_DeepCraters* (Aged Lunar Crater Database), figshare (2020)。10.6084/m9.figshare.12768539 (CC BY 4.0)。
6. Williams, J.-P. ほか, *The global surface temperatures of the Moon as measured by the Diviner Lunar Radiometer Experiment*, Icarus, 283, 300–325 (2017)。データ配布：UCLA Diviner チーム（瞬間温度マップ24枚を現地時間に位相合わせして利用）。
7. Mazarico, E. ほか, *Illumination conditions of the lunar polar regions using LOLA topography*, Icarus, 211 (2011)。データ配布：LRO LOLA Team (NASA GSFC)。
8. NASA Scientific Visualization Studio, *CGI Moon Kit*（散布図の背景画像、パブリックドメイン）。
