# webapp — ブラウザで動く教材（JupyterLite）

`notebooks/` の教材を、インストール不要でブラウザ上で動かすための一式。
`.github/workflows/deploy-pages.yml` が push のたびにビルドして GitHub Pages に公開する。

- **公開URL**：`https://<ユーザー名>.github.io/<リポジトリ名>/`
- 中身は `notebooks/*.ipynb` そのもの（＋先頭に「準備」セルを1つ足したもの）。
  Colab / ローカルでも同じノートブックが動く（「準備」セルはブラウザ版でだけ処理をする）。

## 仕組み

| ファイル | 役割 |
|---|---|
| `assemble.py` | `notebooks/` ＋ `data/` ＋ `assets/` から `content/` を組み立てる。各 `.ipynb` の先頭に `bootstrap_template.py` のセルを追加し、カーネル名を `python`（Pyodide）に直す |
| `bootstrap_template.py` | ブラウザ版で最初に走るセル。`sys.platform == "emscripten"` のときだけ、ipywidgets を入れ、`data/` と `assets/` を fetch する |
| `index.html` | トップページ（各ノートブックへのリンク）。`#jupyter-config-data` を含む必要がある |
| `content/`, `_output/` | 生成物（gitignore 済み）。GitHub Actions がビルドする |

含めるデータは `assemble.py` の `DATA` で指定（凍結・未使用の3つは含めない）。
`maria_boundaries.csv` は `near_maria` が使うので含める。

## ローカルで確認する

```bash
pip install "jupyterlite-core==0.8.*" "jupyterlite-pyodide-kernel==0.8.*" jupyterlab nbformat
python webapp/assemble.py                       # webapp/content/ を作る
jupyter lite build --contents webapp/content --output-dir webapp/_output
cp webapp/index.html webapp/_output/index.html
cd webapp/_output && python -m http.server 8000  # http://localhost:8000/
```

Windows の OneDrive フォルダ内だとビルド中の一時ファイルがロックされることがある。
その場合は `--out` と `--output-dir` を OneDrive の外（例：`%LOCALAPPDATA%\Temp`）に向ける。

## GitHub Pages を有効にする（最初の1回）

リポジトリの Settings → Pages → Build and deployment → Source を
**「GitHub Actions」** にする。以後は push で自動デプロイされる。
