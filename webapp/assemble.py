# -*- coding: utf-8 -*-
"""webapp/content/ を組み立てる（JupyterLite に渡す教材一式）。

- notebooks/ の .ipynb に、ブラウザ用のブートストラップセルを先頭に追加する
- moonkit.py / moonkit_ml.py と、教材で使う data/ ・ assets/ をコピーする
- docs/ の md・pdf も参照用にコピーする
- Diviner の gz を展開して、素の csv もダウンロードできるようにする
- データカタログ webapp/data.html を、実データから生成する

GitHub Actions（.github/workflows/deploy-pages.yml）から呼ばれる。ローカルでも
`python webapp/assemble.py && jupyter lite build --contents webapp/content` で確認できる。
"""
import argparse
import csv
import gzip
import html
import json
import pathlib
import shutil
import warnings

import nbformat

warnings.filterwarnings("ignore", message="Cell is missing an id field")

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp"

# ブラウザ版に含めるノートブック
NOTEBOOKS = [
    "course_moonbase.ipynb",
    "course_moonbase_ml.ipynb",
    "petit_inquiry_start.ipynb",
    "explore.ipynb",
    "explore_advanced.ipynb",
]
# 一緒に置く Python ファイル
PYFILES = ["moonkit.py", "moonkit_ml.py"]
# 教材が読み込むデータ（凍結・未使用の3つは含めない）
DATA = [
    "craters_subset.csv", "craters_3d.csv", "deepcraters.csv",
    "diviner_global.csv.gz", "lola_polar_illumination.csv", "maria_boundaries.csv",
]
ASSETS = ["NotoSansJP-Regular.ttf", "lroc_color_2k.jpg"]
DOCS = [
    "petit_inquiry_brief.md", "petit_inquiry_helpersheet.pdf",
    "petit_inquiry_mentor_notes.md", "teacher_guide_course.md",
    "worksheet_course.pdf",
]

# ブートストラップが fetch するファイルの一覧（content/ からの相対パス）
FETCH_LIST = (
    PYFILES
    + [f"data/{d}" for d in DATA]
    + [f"assets/{a}" for a in ASSETS]
)

# データカタログ（data.html）に載せる情報。ファイル名 → (見出し, 説明, ライセンス, 出典)
CATALOG = {
    "craters_subset.csv": (
        "クレーターの緯度経度・直径・形",
        "USGS の月クレーターDB（Robbins 2018）から直径8km以上を抽出。離心率・扁平率で「どれくらい丸いか」がわかる。",
        "パブリックドメイン", "USGS Astrogeology / Robbins, S. J. (2018)"),
    "craters_3d.csv": (
        "クレーターの直径と深さ",
        "3D形態情報つきカタログ（Wang & Wu 2021、査読付き）から直径10km以上。複数のグローバルDEMからガウスフィットで深さを算出。",
        "CC BY 4.0", "Wang, Y. & Wu, B. (2021), JGR Planets. Zenodo 10.5281/zenodo.4983248"),
    "deepcraters.csv": (
        "クレーターの推定地質年代",
        "嫦娥1・2号データから機械学習で抽出し、地質年代（1=最古〜5=最新）を推定したカタログ。",
        "CC BY 4.0", "Yang, C., Guan, R. ほか (2020), CE_DeepCraters, figshare 10.6084/m9.figshare.12768539"),
    "diviner_global.csv.gz": (
        "月面の温度（現地時間0〜23時の1日のカーブ）",
        "LRO Diviner の瞬間温度マップ24枚（Williams et al. 2017）を現地時間に位相合わせしたもの。全球0.5度グリッド。"
        "信頼できるのは概ね緯度±70度より低い範囲。",
        "パブリックドメイン（NASA）", "Williams, J.-P. ほか (2017), Icarus 283, 300–325 / UCLA Diviner チーム"),
    "lola_polar_illumination.csv": (
        "月の南極・北極の日照率と永久影率",
        "LOLA 標高データから horizon 法で日照条件をシミュレーション（Mazarico et al. 2011）。南北緯82.96〜90度。"
        "日照率の絶対値は他文献と単純比較しないこと（「暗い／明るい」の順序は信頼できる）。",
        "パブリックドメイン（NASA）", "Mazarico, E. ほか (2011), Icarus 211 / LRO LOLA Team (NASA GSFC)"),
    "maria_boundaries.csv": (
        "月の海・大洋 23件の中心座標と半径",
        "USGS 地名辞典から抽出。教材のステップ2で「海」と「陸」を分けるのに使う。",
        "パブリックドメイン", "USGS Gazetteer of Planetary Nomenclature"),
}


def bootstrap_source() -> str:
    tmpl = (WEBAPP / "bootstrap_template.py").read_text(encoding="utf-8")
    files_repr = "[\n        " + ",\n        ".join(json.dumps(f) for f in FETCH_LIST) + ",\n    ]"
    return tmpl.replace("__FILE_LIST__", files_repr)


def _fmt_bytes(n: int) -> str:
    x = float(n)
    for unit in ("B", "KB", "MB"):
        if x < 1024 or unit == "MB":
            return f"{x:.0f} {unit}" if unit == "B" else f"{x:.1f} {unit}"
        x /= 1024
    return f"{x:.1f} MB"


def _preview_rows(path: pathlib.Path, gz: bool, n: int = 6):
    opener = gzip.open if gz else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        rows = [next(r, None) for _ in range(n)]
    return header, [x for x in rows if x is not None]


def _table_html(header, rows) -> str:
    th = "".join(f"<th>{html.escape(c)}</th>" for c in header)
    trs = ""
    for row in rows:
        tds = "".join(f"<td>{html.escape(c)}</td>" for c in row)
        trs += f"<tr>{tds}</tr>"
    return f'<div class="tablewrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def write_data_catalog(content: pathlib.Path) -> None:
    """webapp/data.html を実データから生成する。"""
    sections = []
    for fname, (title, desc, lic, src) in CATALOG.items():
        gz = fname.endswith(".gz")
        srcfile = ROOT / "data" / fname
        header, rows = _preview_rows(srcfile, gz)
        size = srcfile.stat().st_size
        n_rows = sum(1 for _ in (gzip.open(srcfile, "rt", encoding="utf-8") if gz
                                 else open(srcfile, "rt", encoding="utf-8"))) - 1

        dl = f'<a class="dl" href="./files/data/{fname}" download>{fname}（{_fmt_bytes(size)}）</a>'
        if gz:
            plain = fname[:-3]  # .gz を外した名前（assemble が content に展開して置く）
            dl = (f'<a class="dl" href="./files/data/{plain}" download>{plain}（展開版・約42 MB）</a>'
                  f'<a class="dl alt" href="./files/data/{fname}" download>{fname}（{_fmt_bytes(size)}・gzip圧縮）</a>')

        sections.append(f"""
  <section>
    <h2>{html.escape(title)}</h2>
    <p class="desc">{html.escape(desc)}</p>
    <p class="meta">{n_rows:,} 行 ／ {len(header)} 列 ／ ライセンス：{html.escape(lic)}<br>
       出典：{html.escape(src)}</p>
    <p class="dls">{dl}</p>
    <details><summary>先頭の数行を見る</summary>
    {_table_html(header, rows)}
    </details>
  </section>""")

    template = (WEBAPP / "data.template.html").read_text(encoding="utf-8")
    (WEBAPP / "data.html").write_text(
        template.replace("<!--SECTIONS-->", "\n".join(sections)), encoding="utf-8")
    print(f"wrote {WEBAPP / 'data.html'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(WEBAPP / "content"),
                    help="出力先（既定：webapp/content）")
    CONTENT = pathlib.Path(ap.parse_args().out).resolve()

    if CONTENT.exists():
        shutil.rmtree(CONTENT)
    (CONTENT / "data").mkdir(parents=True)
    (CONTENT / "assets").mkdir(parents=True)
    (CONTENT / "docs").mkdir(parents=True)

    boot = bootstrap_source()
    for name in NOTEBOOKS:
        nb = nbformat.read(ROOT / "notebooks" / name, as_version=4)
        cell = nbformat.v4.new_code_cell(boot, metadata={"tags": ["webapp-bootstrap"]})
        nb.cells.insert(0, cell)
        # JupyterLite の Pyodide カーネルは name="python"。合わせておかないと
        # 「No Kernel」になる。
        nb.metadata["kernelspec"] = {"name": "python", "display_name": "Python (Pyodide)"}
        for i, c in enumerate(nb.cells):   # 全セルに id を付ける（元ノートブックには無い）
            c.setdefault("id", f"{name[:-6]}-{i:02d}")
        nbformat.validate(nb)
        nbformat.write(nb, CONTENT / name)

    for name in PYFILES:
        shutil.copy2(ROOT / "notebooks" / name, CONTENT / name)
    for name in DATA:
        shutil.copy2(ROOT / "data" / name, CONTENT / "data" / name)
        if name.endswith(".gz"):   # 素の csv もダウンロードできるよう展開版を置く
            with gzip.open(ROOT / "data" / name, "rb") as fi, \
                 open(CONTENT / "data" / name[:-3], "wb") as fo:
                shutil.copyfileobj(fi, fo)
    for name in ASSETS:
        shutil.copy2(ROOT / "notebooks" / "assets" / name, CONTENT / "assets" / name)
    for name in DOCS:
        src = ROOT / "docs" / name
        if src.exists():
            shutil.copy2(src, CONTENT / "docs" / name)

    write_data_catalog(CONTENT)

    print(f"assembled -> {CONTENT}")
    for p in sorted(CONTENT.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(CONTENT)}  ({p.stat().st_size:,} B)")


if __name__ == "__main__":
    main()
