# 自校の関心に合わせて教材を差し替える手引き

この教材は「実施形態・分析ツール・実行環境に依存しない」ことを要件にしています。
さらに、**先生が関心のあるデータや指標に差し替えられる**ようにしてあります。
（衛星データ教材 `Pythonで学ぶ衛星データ解析基礎`（田中ほか 2022）の「少しのコード変更で対象地域を
変えられる」という設計に相当します。）

対象：教材を自分の授業に合わせて改造したい先生。Python が少し読める前提。

---

## パターン1　データセットを1つ足す（例：月の磁気異常、He-3 濃度、別のクレーターカタログ）

### 手順

1. **前処理スクリプトを書く**：`tools/build_template.py` をコピーして `tools/build_<name>.py` に。
   - docstring に**取得元 URL・値の復元式・ライセンス**を書く（`data/SOURCES.md` の他の項目にならう）。
   - `load_raw()` で取得、`shape()` で列名を教材の約束に合わせる：
     - 緯度は `lat`、経度は `lon`（**-180〜180**）。グリッドなら他データと同じ刻みが望ましい。
     - 値の列はわかりやすい名前。必要なら丸める（**座標は丸めない**＝結合が壊れる）。
   - `verify()` で**既知の地点・文献値と照合**する（ここを必ず書く。教材の主眼）。
2. `python tools/build_<name>.py --write` で `data/<name>.csv`（大きければ `.csv.gz`）を作る。
3. **`notebooks/moonkit.py` の `DATASETS` に1行足す**：
   ```python
   DATASETS = {
       ...
       '磁気異常': 'lunar_magnetic.csv',     # ← これだけ
   }
   ```
   これで `load('磁気異常')` がノートブックで使えるようになります（`explore.ipynb` の自由探索ツールに
   出したい場合は、そのノートブックの `datasets` 辞書にも同じ形で足す）。
4. `data/LICENSES.md`・`data/SOURCES.md` に1項目書く。CC BY のデータなら帰属要件も。
5. webapp に含めたい場合は `webapp/assemble.py` の `DATA` リストと `CATALOG` に足す。

### `load()` は未知のファイル名でもそのまま読める

`DATASETS` に登録しなくても、`load('lunar_magnetic.csv')` のようにファイル名を直接渡せば
`data/` から読み込みます。試すだけならこれで十分です。

---

## パターン2　`site_score` の指標を差し替える（例：通信中継基地＝地球可視性）

ステップ4の「最適地スコア」は、`site_score(df, want=...)` の `want` 辞書を変えるだけで
評価軸を差し替えられます。列さえあれば何でも指標にできます。

```python
# 例：地球が見える度合いの列 earth_visibility を自分で作って足す
極 = south_pole(load('極域日照'))
極['earth_visibility'] = ...      # 自校で定義（例：緯度と経度から幾何計算）
site_score(極, want={
    'earth_visibility':             ('高い', 3),   # 通信重視
    'average_illumination_percent': ('高い', 1),   # 電力も少し
    'slope_deg':                    ('低い', 2),
})
```

`moonkit.site_score` の中身は十数行です（`notebooks/moonkit.py`）。読めば、
0〜1 正規化と重み付き和をしているだけだと分かります。ブラックボックスではありません。

---

## パターン3　対象地域・緯度帯を変える

- 温度の緯度帯：`region(load('温度'), lat=(自校の関心), lon=(...))`
- 極を北にする：`north_pole(load('極域日照'))`
- 海の一区画：`region(load('クレーター'), lat=(..), lon=(..))` で切って `len` や `summary`

「月面基地」というゴール自体を変えることもできます（例：着陸探査機の候補地、
科学的に面白い地点、資源の分布）。ワークシートの「ミッション」を書き換えてください。

---

## 変えないほうがよいところ

- **座標の約束**（`lat` / `lon` / -180〜180）。ここを崩すと `nearest` や `join_grid` が壊れます。
- **`verify()` を書くこと**。「文献値・既知の地点と照合してから使う」は、この教材が生徒に
  教えていることそのものです。前処理を作った本人が省いてはいけません。
- **機械学習を層1（`moonkit.py`）に入れないこと**。教師なし／教師ありは `moonkit_ml.py` に限定。

---

## 参考

- 既存の前処理スクリプト：`tools/`（`build_slope.py`・`build_diviner_curve.py` などが実例）
- データの約束と検証記録：`data/SOURCES.md`
- ヘルパーの一覧：`docs/petit_inquiry_helpersheet.pdf`
