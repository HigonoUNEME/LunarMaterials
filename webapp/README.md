# webapp — ブラウザで動く教材

`.github/workflows/deploy-pages.yml` が push のたびに2本立てでビルドし、GitHub Pages に公開する。

| 公開パス | 中身 | ビルド元 |
|---|---|---|
| `/` | 3Dの月球儀で有名な地点を見る入口ページ | `webapp/react/`（Vite / React / Three.js） |
| `/app/` | 分析ノートブック本体（JupyterLite / Pyodide） | `notebooks/*.ipynb` ＋ `webapp/assemble.py` |
| `/data.html` | 月データ（CSV）のダウンロード一覧 | `webapp/data.template.html` ＋ `assemble.py` |
| `/data/` | CSV 実体（Diviner は展開版と gzip の両方） | `assemble.py` の `stage_downloads()` → `webapp/_dl/` |

- 公開URL：`https://<ユーザー名>.github.io/<リポジトリ名>/`
- ノートブックの実体は `notebooks/*.ipynb` そのもの（＋先頭に「準備」セルを1つ）。
  Colab / ローカルでも同じものが動く。

## 仕組み

| ファイル | 役割 |
|---|---|
| `assemble.py` | `notebooks/`＋`data/`＋`assets/` から JupyterLite 用 `content/` を組み立て（各 `.ipynb` の先頭に `bootstrap_template.py` のセルを足し、カーネル名を `python` にする）、データ一覧 `data.html` を実データから生成し、DL 用 `_dl/` に CSV を用意する |
| `bootstrap_template.py` | ブラウザ版で最初に走るセル。`sys.platform == "emscripten"` のときだけ ipywidgets を入れ、`data/`・`assets/` を fetch する |
| `data.template.html` | データ一覧ページの枠（`<!--SECTIONS-->` に `assemble.py` が流し込む） |
| `react/` | 3D入口ページ。`base:'./'` でビルドしてサブパス配信に対応。約38の「代表地点」データは `react/src/data/lunarData.ts`（検証記録は `docs/explorer_data_verification.md`） |
| `content/`, `_output/`, `_dl/` | 生成物（gitignore 済み）。`react/node_modules`・`react/dist` も同様。`react/package-lock.json` はコミットする |

含めるデータは `assemble.py` の `DATA` で指定（凍結・未使用の3つは含めない）。

## ローカルで確認する

`webapp/react` を単体で `npm run dev` すると **`data.html` と `/app/` が無い**（この2つは
deploy ワークフローの「Compose the site」で合成される）。入口ページの「データ一覧」
「分析をはじめる」まで含めて確認するには、合成後を配信する必要がある。

```bash
pip install "jupyterlite-core==0.8.*" "jupyterlite-pyodide-kernel==0.8.*" jupyterlab nbformat

python webapp/dev_preview.py           # 差分ビルドして http://localhost:8899/ で配信
python webapp/dev_preview.py --full    # ノートブックを変えたとき（JupyterLite も作り直す）
```

`dev_preview.py` が assemble → JupyterLite → `npm run build` → 合成 → 配信までやる。
生成物は OneDrive の外（`%LOCALAPPDATA%\Temp\moon-site`）に作る（OneDrive 内だと
ビルド中の一時ファイルがロックされて失敗するため）。

手順を分けて回したいときは README 履歴の旧コマンド（`assemble.py --out … / jupyter lite build …`）を参照。

## GitHub Pages を有効にする（最初の1回）

リポジトリの Settings → Pages → Build and deployment → Source を
**「GitHub Actions」** にする。以後は push で自動デプロイされる。
