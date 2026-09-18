# データの二次配布可否レビュー Ver.1.0

GitHub を public にしてよいか＝ `data/` の各 CSV（元データの派生物）を再配布する権利があるか、を確認した記録。
あわせて、取得データに見落としがないか・論文の図を再現できるかを検証した。

調査日：2026-09-04　／　調査者：須藤（M25-8118）

---

## 0. 結論

**public にしてよい。** `data/` の全ファイルは再配布が許可されている ―
2 件が CC BY 4.0（表示すれば再配布可）、残りは NASA / USGS / JPL 由来で
実質パブリックドメイン（NASA ミッションデータは既定で CC0）。

ただし **public 化の前に4点を直すべき**（いずれも「禁止」ではなく「表示義務・出所記録の不備」）：

1. CC BY 4.0 の2件に、ライセンス URL と「改変した旨」を明記する（現状は出典のみ）
2. Diviner の取得元 URL がリポジトリのどこにも記録されていない → 追記する
3. `data/*.csv` を作った前処理スクリプトが1つもコミットされていない → 出所と手順を `data/SOURCES.md` に残す（または스크립트をコミット）
4. 使っていない `moon_earth_correlation.csv`（月齢×地震）は科学的妥当性の懸念で v1.4 に除外済み。ファイルだけ `data/` に残っている → public 化前に削除を推奨

---

## 1. データセット別のライセンス判定

| ファイル | 出典 | ライセンス | 再配布 | 根拠 |
|---|---|---|---|---|
| `craters_3d.csv` | Wang & Wu (2021) JGR Planets、Zenodo `10.5281/zenodo.4983248` | **CC BY 4.0** | ✅ 表示すれば可 | Zenodo のライセンス欄に "Creative Commons Attribution 4.0 International" と明記。API で確認 |
| `deepcraters.csv` | Yang, Guan ほか (2020) Nature Communications、figshare `10.6084/m9.figshare.12768539`（ファイル `Aged_Lunar_Crater_Database_DeepCraters_2020(1).csv`） | **CC BY 4.0** | ✅ 表示すれば可 | figshare API で `license: {name: "CC BY 4.0", url: ...}` を確認。姉妹レコード `12765986` も同一 |
| `craters_subset.csv` | Robbins (2018) JGR Planets。NASA PDS Annex / USGS Astrogeology で配布 | 実質パブリックドメイン（PDS = CC0 相当、USGS = 米政府著作物） | ✅ 可 | AGU 論文本文「全データは公開アーカイブで自由に利用可能」。PDS データ利用方針「制限なし、引用を強く推奨」。USGS 惑星データは "Public Domain" 表示 |
| `diviner_global.csv(.gz)` | UCLA Diviner チーム（LRO/Diviner）の level4 ラスタ製品 `diviner_tbol_snapshot_{000..345}E.xyz`。科学的背景は Williams ほか (2017) Icarus | パブリックドメイン（NASA ミッションデータ = CC0） | ✅ 可 | NASA データ利用方針「NASA 主導ミッションのデータは既定で CC0、利用制限なし」。PDS Geosciences Node（Diviner アーカイブ）も自由再配布 |
| `lola_polar_illumination.csv` | LOLA チーム（LRO/LOLA、`imbrium.mit.edu`）の日照マップ IMG。背景は Mazarico ほか (2011) Icarus | パブリックドメイン（NASA = CC0） | ✅ 可 | 同上（LRO 搭載機器データ） |
| `maria_boundaries.csv` | USGS / IAU Gazetteer of Planetary Nomenclature | パブリックドメイン（米政府著作物 + IAU 公式命名） | ✅ 可 | USGS 惑星命名データは公開・自由利用 |
| `moon_geology_grid.csv` ※未使用 | USGS Unified Geologic Map of the Moon（Fortezzo ほか 2020, SIM 3316） | パブリックドメイン（USGS 刊行物） | ✅ 可 | USGS 刊行物は米政府著作物 |
| `moon_ephemeris.csv` ※未使用 | NASA JPL HORIZONS | パブリックドメイン（JPL/NASA） | ✅ 可 | HORIZONS は明示的に自由利用可 |
| `moon_earth_correlation.csv` ※未使用・除外済み | USGS 地震カタログ FDSN API + JPL HORIZONS | パブリックドメイン（USGS + JPL） | ✅ 可（ただし科学的懸念で削除推奨） | USGS 地震データは公開 |
| `notebooks/assets/lroc_color_2k.jpg` | NASA SVS「CGI Moon Kit」(ID 4720) | パブリックドメイン（NASA SVS） | ✅ 可 | SVS「全コンテンツはパブリックドメイン、ダウンロード・利用・再配布は自由」 |
| `docs/mare_outline.npz` | 上記 SVS モザイク 4k から閾値化して作った輪郭 | 派生物。元がパブリックドメインなので可 | ✅ 可 | 同上。4k 元画像 `docs/_lroc_color_4k.tif` は gitignore でコミットしない |

### 論文（引用のみ・再配布していない）

Robbins 2018 / Wang & Wu 2021 は JGR Planets（AGU/Wiley）、Williams 2017 は Icarus（Elsevier）、
Yang ほか 2020 は Nature Communications。**いずれも論文本文・図は配布しておらず、データだけを別アーカイブ
（Zenodo・figshare・PDS・UCLA サーバ）から取得している。** Elsevier / Wiley の supplement を使って
いないため、出版社の著作権は問題にならない。

---

## 2. CC BY 4.0 の2件が満たすべき条件（現状と対応）

CC BY 4.0 は再配布・改変を許すが、**(a) クレジット (b) ライセンスへのリンク (c) 改変した旨の表示** を要求する。

| | 現状（`data/LICENSES.md` ・ `NOTICE`） | 必要な追記 |
|---|---|---|
| (a) クレジット | 著者・年・誌名は記載あり | 完全な書誌（`Wang, Y., Wu, B., Xue, H., Li, X., & Ma, J. (2021)…` / `Yang, C., Zhao, H., Bruzzone, L. ほか (2020)…`）に |
| (b) ライセンスリンク | なし | `https://creativecommons.org/licenses/by/4.0/` を明記 |
| (c) 改変の表示 | 「前処理済みの派生物です」と1行のみ | 具体的に：`craters_3d.csv`＝直径10km以上に絞り込み・列名変更・CSV化／`deepcraters.csv`＝Aged サブセットを抽出・列そのまま |

→ `data/LICENSES.md` と `NOTICE` を上記の形に更新すれば CC BY 4.0 コンプライアンスは満たせる。

---

## 3. 取得データの見落としチェック

### 3.1 出所（プロヴェナンス）の記録漏れ

- **Diviner**：`requirements_v1.5.md §2.3` に「UCLA Diviner の瞬間温度マップ24枚（`diviner_tbol_snapshot_000E.xyz`〜`_345E.xyz`）」とあるが、**取得 URL がリポジトリのどこにも書かれていない**。
  実際の配布元は `http://luna1.diviner.ucla.edu/~jpierre/diviner/level4_raster_data/diviner_tbol_snapshot_XXXE.xyz`
  （XXX = subsolar 経度 000〜345、°E）。※このサーバは TLS 設定が古く（DH_KEY_TOO_SMALL）、通常の
  Python/requests では落ちることがある。ブラウザまたは `curl --ciphers` で取得する。
- **前処理スクリプトが1つもコミットされていない**。`data/craters_subset.csv` `craters_3d.csv` `deepcraters.csv`
  `diviner_global.csv.gz` `lola_polar_illumination.csv` は、生データ（PDS の IMG、Zenodo の RAR、UCLA の xyz 等）
  から作られた成果物だが、**その変換コードがリポジトリに無い**。教材としての再現性・検証可能性の観点で弱い。
  → 最低限、`data/SOURCES.md` に「各ファイル ← どの URL の何を ← どう処理したか」を1ファイルにまとめる。
  できれば前処理スクリプトを `tools/` としてコミットする。
- `course/data/`（`temp_grid.csv` ほか）は gitignore。`course/build_course_data.py` はコミット済みで、
  これは `data/` の CSV から作れる（生データ不要）ので再現性はある。ゼミスライドの図は `course/data/temp_grid.csv`
  から生成される。

### 3.2 使っていないのに `data/` に残っているファイル

`moon_geology_grid.csv` `moon_ephemeris.csv` `moon_earth_correlation.csv` は、どのノートブックからも
参照されていない（`requirements_v1.3 §7.2` / `v1.4` で UI から削除）。ライセンス上は問題ないが：

- `moon_earth_correlation.csv`（月齢×地震件数）は **「科学的妥当性に疑義がある仮説」** として v1.4 で
  コアスコープから完全除外された経緯がある。ファイルだけ残すと、public リポジトリを見た人が
  「月齢と地震の相関データ」として使ってしまう恐れがある。**public 化の前に削除を推奨。**
- 他2つ（地質年代グリッド・天体暦）は無害だが、使わないなら消してもよい。

---

## 4. 論文の図の再現性チェック

### 4.1 Diviner 温度 vs Williams et al. (2017)  ― 赤道：一致

`data/diviner_global.csv.gz`（259,200点＝0.5°全球グリッド、欠損0）で赤道帯（|緯度|≤1°）を集計：

| 指標 | この教材のデータ | Williams+2017 | 判定 |
|---|---|---|---|
| 1日の平均最高温度 | 390.5 K | 392.3 K | ✅ 差 0.5% |
| 1日の平均最低温度 | 95.6 K | 94.3 K | ✅ 差 1.4% |
| 1日の較差（振幅） | 294.9 K | 約 290〜298 K | ✅ 一致 |
| 最高温度の現地時刻 | 中央値 12時、9〜15時の外れ 0% | 正午前後 | ✅ |

赤道の最高温度がわずかに低め（−1.8 K）なのは、**再構成が現地時間15°（≒1時間）刻みで正午のピークを
少し丸めるため**で、データ破損ではない。**再ダウンロード不要。**

ゼミスライドの数値（平均 217 K・赤道の較差 295 K・緯度60° の較差 236 K）は
`course/data/temp_grid.csv` と整合。緯度60°は信頼範囲（<70°）内。

### 4.2 Diviner 高緯度（>70°）  ― ずれあり・原因特定済み・対処済み

| 緯度 | この教材のデータの較差 | Williams+2017（概略） |
|---|---|---|
| 70° | 210 K | 〜180 K |
| 85° | 153 K | 〜120 K |
| 88° | 124 K | 〜110 K |

高緯度で振幅が2〜3割大きく出る。**原因：24枚の全球スナップショットを現地時間で位相整列する方法が
極付近で退化する**（太陽が沈まず地平線を回るだけなので「現地時間」が意味を失う）。
実データでも |緯度|>82° の点の **24%** が「最高温度の時刻が 9〜15時の外」にある（赤道は 0%）。

これは **既知の方法論的限界で、`requirements_v1.9` で検証済み・対処済み**：
- 教材の緯度帯比較は **60°で打ち切り**、極域には温度カーブを使わず LOLA 日照データに切り替え
- ゼミスライドの図（`fig_temp_curve` 赤道のみ／`fig_temp_bands` 赤道・30°・60°）は
  すべて信頼範囲内。**発表する図に影響なし。**

**再ダウンロードでは直らない**（元データの問題ではなく整列手法の問題）。この限界は
報告書・教材の注記として残すべき。

### 4.3 クレーターカタログ  ― 件数・座標範囲は正常

| ファイル | 件数 | 絞り込み | 座標範囲 |
|---|---|---|---|
| `craters_subset.csv` | 36,377 | Robbins DB（≥1km）から教材用に抽出 | lat/lon 正常 |
| `craters_3d.csv` | 24,982 | Wang & Wu（132万件）から直径10km以上 | 正常、depth_km≤0 は既知の20件のみ |
| `deepcraters.csv` | 18,996 | DeepCraters の Aged サブセット | Age・Diam_km 正常 |

いずれも `requirements_v2.1` の記載件数と一致。個別の論文図の再現（サイズ頻度分布など）は
未実施だが、件数・範囲・欠損に異常なし。

---

## 5. public 化前のチェックリスト

- [x] `data/LICENSES.md`・`NOTICE` を CC BY 4.0 準拠に更新（§2）：完全書誌 + ライセンス URL + 改変の明記 ← 2026-09-04 対応
- [x] `data/SOURCES.md` を新規作成：各 CSV の取得元 URL と前処理手順（特に Diviner の UCLA URL） ← 新規作成
- [x] `moon_earth_correlation.csv` を `data/` から削除（科学的懸念・未使用） ← 削除・README/LICENSES に経緯記載
- [x] `moon_geology_grid.csv`・`moon_ephemeris.csv` の扱い ← 「保持のみ・配布ビルド非同梱」と LICENSES.md / SOURCES.md / README に明記
- [x] README の「データは PD/CC BY」の記述に CC BY 2件の帰属要件を追記 ← §ライセンス を書き換え
- [x] Diviner 高緯度の限界を報告書の注記に入れる（§4.2） ← `docs/report_v2.0.html` 【活動内容】層0段落に追記、PDF 再生成（2ページ維持）
- [x] `webapp/data.template.html` のフッターに CC BY 帰属要件と SOURCES.md への参照を追記
- [ ] （任意・未対応）前処理スクリプトを `tools/` にコミットして完全再現可能にする ← SOURCES.md に手順は文章で記録済み。スクリプト化は今後

**ライセンス上の障害は無く、上記の必須項目は対応済み。public 化して問題ない。**
（残る任意項目：前処理スクリプトのコミット。）
