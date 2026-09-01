# -*- coding: utf-8 -*-
"""webapp/content/ を組み立てる（JupyterLite に渡す教材一式）。

- notebooks/ の .ipynb に、ブラウザ用のブートストラップセルを先頭に追加する
- moonkit.py / moonkit_ml.py と、教材で使う data/ ・ assets/ をコピーする
- docs/ の md・pdf も参照用にコピーする

GitHub Actions（.github/workflows/deploy-pages.yml）から呼ばれる。ローカルでも
`python webapp/assemble.py && jupyter lite build --contents webapp/content` で確認できる。
"""
import argparse
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


def bootstrap_source() -> str:
    tmpl = (WEBAPP / "bootstrap_template.py").read_text(encoding="utf-8")
    files_repr = "[\n        " + ",\n        ".join(json.dumps(f) for f in FETCH_LIST) + ",\n    ]"
    return tmpl.replace("__FILE_LIST__", files_repr)


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
    for name in ASSETS:
        shutil.copy2(ROOT / "notebooks" / "assets" / name, CONTENT / "assets" / name)
    for name in DOCS:
        src = ROOT / "docs" / name
        if src.exists():
            shutil.copy2(src, CONTENT / "docs" / name)

    print(f"assembled -> {CONTENT}")
    for p in sorted(CONTENT.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(CONTENT)}  ({p.stat().st_size:,} B)")


if __name__ == "__main__":
    main()
