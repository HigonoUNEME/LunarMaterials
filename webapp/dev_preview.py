# -*- coding: utf-8 -*-
"""ローカルで「公開されるサイトそのまま」を確認する。

GitHub Pages に出るのと同じ構成（`/` 入口ページ・`/app/` ノートブック・`/data.html`・
`/data/` の CSV）を組み立てて http で配信する。

    python webapp/dev_preview.py            # 差分ビルド（速い）。JupyterLite は前回の生成物を再利用
    python webapp/dev_preview.py --full     # JupyterLite も作り直す（初回・ノートブック更新時）
    python webapp/dev_preview.py --port 8000

なぜ必要か: `webapp/react` を単体で `npm run dev` すると `data.html` と `/app/` が
存在しない（この2つは deploy ワークフローの「Compose the site」で合成される）。
入口ページの「データ一覧」「分析をはじめる」リンクを確認するには合成後を配信する必要がある。

生成物は OneDrive の外（%LOCALAPPDATA%\\Temp\\moon-site）に作る。OneDrive 内だと
ビルド中の一時ファイルがロックされて rmtree が失敗するため。
"""
import argparse
import functools
import http.server
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

try:  # Windows の cp932 コンソールで絵文字などがあっても落ちないように
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp"
REACT = WEBAPP / "react"

WORK = pathlib.Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "Temp" / "moon-site"
CONTENT = WORK / "content"
DL = WORK / "_dl"
OUT = WORK / "_output"


def run(cmd, **kw):
    print(f"$ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kw)


def npm_cmd() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def build(full: bool) -> None:
    WORK.mkdir(parents=True, exist_ok=True)

    # 1. JupyterLite 用の content と DL 用 CSV（出力先は OneDrive の外）
    run([sys.executable, str(WEBAPP / "assemble.py"),
         "--out", str(CONTENT), "--dl-out", str(DL)])

    # 2. JupyterLite 本体（重い）。--full か、まだ無いときだけ
    app_dir = OUT / "app"
    if full or not (app_dir / "index.html").exists():
        if app_dir.exists():
            shutil.rmtree(app_dir, ignore_errors=True)
        run(["jupyter", "lite", "build",
             "--contents", str(CONTENT),
             "--output-dir", str(app_dir)])
    else:
        print(f"= JupyterLite は再利用（作り直すなら --full）: {app_dir}")

    # 3. 3D 入口ページ。src が dist より新しい（＝作り変えた）とき、--full のとき、
    #    dist がまだ無いときだけビルドする。それ以外は既存の dist を使う（node 不要）。
    dist = REACT / "dist"
    dist_index = dist / "index.html"
    src_mtime = max((p.stat().st_mtime for p in (REACT / "src").rglob("*") if p.is_file()),
                    default=0.0)
    # site_environment.csv を入口ページ用 JSON に間引く（古ければ作り直す）
    env_json = REACT / "src" / "data" / "siteEnvironment.generated.json"
    env_csv = ROOT / "data" / "site_environment.csv"
    if env_csv.exists() and (not env_json.exists()
                             or env_csv.stat().st_mtime > env_json.stat().st_mtime):
        run([sys.executable, str(REACT / "scripts" / "gen_site_env.py")])
        src_mtime = max(src_mtime, env_json.stat().st_mtime)

    # 月面に重ねるデータ層テクスチャ（「地球の風」Phase1）を site_environment.csv から作る
    overlay_json = REACT / "src" / "data" / "overlayLayers.generated.json"
    overlay_png = REACT / "public" / "textures" / "overlay_temp_amp_K.png"
    if env_csv.exists() and (not overlay_png.exists()
                             or env_csv.stat().st_mtime > overlay_png.stat().st_mtime):
        run([sys.executable, str(REACT / "scripts" / "gen_overlay_textures.py")])
        src_mtime = max(src_mtime, overlay_json.stat().st_mtime, overlay_png.stat().st_mtime)

    # 1日の温度アニメーション（24枚、「地球の風」Phase3）を diviner_global.csv.gz から作る。
    # 生成が重い（14MBのCSVを読む）ので、元データが変わったときだけ作り直す。
    diurnal_json = REACT / "src" / "data" / "diurnalFrames.generated.json"
    diviner_csv = ROOT / "data" / "diviner_global.csv.gz"
    if diviner_csv.exists() and (not diurnal_json.exists()
                                 or diviner_csv.stat().st_mtime > diurnal_json.stat().st_mtime):
        run([sys.executable, str(REACT / "scripts" / "gen_diurnal_frames.py")])
        src_mtime = max(src_mtime, diurnal_json.stat().st_mtime)

    # 月球儀にカーソルを合わせたときの「1日の温度」ホバー値用ルックアップ（常設ピン廃止に伴う対応）
    diurnal_lookup_json = REACT / "src" / "data" / "diurnalLookup.generated.json"
    if diviner_csv.exists() and (not diurnal_lookup_json.exists()
                                 or diviner_csv.stat().st_mtime > diurnal_lookup_json.stat().st_mtime):
        run([sys.executable, str(REACT / "scripts" / "gen_diurnal_lookup.py")])
        src_mtime = max(src_mtime, diurnal_lookup_json.stat().st_mtime)

    stale = (not dist_index.exists()) or src_mtime > dist_index.stat().st_mtime
    if full or stale:
        if not (REACT / "node_modules").exists():
            run([npm_cmd(), "ci"], cwd=REACT)
        vite_js = REACT / "node_modules" / "vite" / "bin" / "vite.js"
        node = shutil.which("node")
        if node and vite_js.exists():
            # npm 経由だと環境によって vite の終了コードを取りこぼすので node で直接叩く
            run([node, str(vite_js), "build"], cwd=REACT)
        else:
            run([npm_cmd(), "run", "build"], cwd=REACT)
    else:
        print(f"= 3D入口ページは既存の dist を再利用: {dist}")

    # 4. 合成（deploy-pages.yml の "Compose the site" と同じ）
    OUT.mkdir(parents=True, exist_ok=True)
    for item in REACT.joinpath("dist").iterdir():
        dst = OUT / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)
    shutil.copy2(WEBAPP / "data.html", OUT / "data.html")
    if (WEBAPP / "shadow_sim.html").exists():
        shutil.copy2(WEBAPP / "shadow_sim.html", OUT / "shadow_sim.html")
    data_dir = OUT / "data"
    data_dir.mkdir(exist_ok=True)
    for csv in DL.iterdir():
        shutil.copy2(csv, data_dir / csv.name)

    print(f"\n合成完了 -> {OUT}")


def serve(port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"\n-> http://localhost:{port}/  (Ctrl+C stop)")
        print(f"   iriguchi     http://localhost:{port}/index.html")
        print(f"   data ichiran http://localhost:{port}/data.html")
        print(f"   notebook     http://localhost:{port}/app/")
        httpd.serve_forever()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="JupyterLite も作り直す")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--no-serve", action="store_true", help="ビルドだけして配信しない")
    args = ap.parse_args()

    build(args.full)
    if not args.no_serve:
        serve(args.port)


if __name__ == "__main__":
    main()
