# -*- coding: utf-8 -*-
"""層をまたいだ整合性チェック（requirements_v3.3.md I7）。

過去3回「文書は直したがノートブック実物が直っていない」不整合が起きた。
その再発防止。1コマンドで緑/赤を出す。

  python tools/check_consistency.py            # 構造チェックのみ（数秒）
  python tools/check_consistency.py --execute  # 全ノートブックの nbconvert 実行も（数分）

チェック項目:
  C1  moonkit.DATASETS の値 ⊆ data/ の実ファイル
  C2  webapp/assemble.py の DATA ⊆ data/ の実ファイル、かつ ⊇ DATASETS の値
  C3  DATASETS の各ファイルが data/SOURCES.md と data/LICENSES.md に出てくる
  C4  README.md のデータ種数の記述が実態と合う
  C5  assemble.py の NOTEBOOKS が notebooks/ に実在
  C6  teacher_guide_course.md が参照するノートブック名が実在
  C7  (--execute) 全ノートブックが nbconvert --execute を通る
"""
from __future__ import annotations
import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
NB = ROOT / "notebooks"

FAILS: list[str] = []
WARNS: list[str] = []


def fail(tag: str, msg: str) -> None:
    FAILS.append(f"[{tag}] {msg}")
    print(f"  ✗ {msg}")


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def warn(tag: str, msg: str) -> None:
    WARNS.append(f"[{tag}] {msg}")
    print(f"  ! {msg}")


def _literal_after(text: str, name: str):
    """`name = [...]` または `name = {...}` を1つ取り出して ast で評価する。"""
    m = re.search(rf"^{re.escape(name)}\s*=\s*", text, re.M)
    if not m:
        return None
    start = m.end()
    depth = 0
    opener = text[start]
    close = {"[": "]", "{": "}", "(": ")"}[opener]
    for i in range(start, len(text)):
        c = text[i]
        if c == opener:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return ast.literal_eval(text[start:i + 1])
    return None


def moonkit_datasets() -> dict:
    text = (NB / "moonkit.py").read_text(encoding="utf-8")
    d = _literal_after(text, "DATASETS")
    if not isinstance(d, dict):
        fail("C1", "moonkit.py の DATASETS を読めなかった")
        return {}
    return d


def assemble_lists() -> tuple[list, list]:
    text = (ROOT / "webapp" / "assemble.py").read_text(encoding="utf-8")
    data = _literal_after(text, "DATA") or []
    nbs = _literal_after(text, "NOTEBOOKS") or []
    return list(data), list(nbs)


def check_structure() -> None:
    ds = moonkit_datasets()
    data_files = {p.name for p in DATA.iterdir() if p.is_file()}

    print("C1  moonkit.DATASETS ⊆ data/")
    for key, fname in ds.items():
        if fname in data_files:
            ok(f"{key} -> {fname}")
        else:
            fail("C1", f"DATASETS['{key}'] = {fname} が data/ に無い")

    print("C2  assemble.py DATA / NOTEBOOKS")
    adata, anbs = assemble_lists()
    for f in adata:
        if f not in data_files:
            fail("C2", f"assemble DATA の {f} が data/ に無い")
    missing_from_assemble = set(ds.values()) - set(adata)
    if missing_from_assemble:
        fail("C2", f"DATASETS にあるが assemble DATA に無い: {sorted(missing_from_assemble)}")
    else:
        ok(f"DATA {len(adata)} 件すべて実在、DATASETS の値をすべて含む")

    print("C3  SOURCES.md / LICENSES.md に記載")
    src = (DATA / "SOURCES.md").read_text(encoding="utf-8")
    lic = (DATA / "LICENSES.md").read_text(encoding="utf-8")
    for fname in sorted(set(ds.values())):
        stem = fname.replace(".csv.gz", "").replace(".csv", "")
        if stem not in src:
            fail("C3", f"{fname} が data/SOURCES.md に出てこない")
        if stem not in lic:
            warn("C3", f"{fname} が data/LICENSES.md に出てこない")
    if not any(f"[C3]" in x for x in FAILS):
        ok("SOURCES.md に全データが記載")

    print("C4  README のデータ種数")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    n_load = len(ds)          # 生徒が load() で読む名前つきデータ
    n_dist = len(adata)       # 配布ファイル（ヘルパー maria_boundaries 込み）
    nums = set(int(x) for x in re.findall(r"(\d+)\s*(?:種|データセット|datasets?)", readme))
    if nums & {n_load, n_dist}:
        ok(f"README のデータ種数が実態と整合（load {n_load} / 配布 {n_dist}）")
    elif nums:
        warn("C4", f"README のデータ種数 {sorted(nums)} が実態（load {n_load} / 配布 {n_dist}）と一致しない")
    else:
        warn("C4", f"README にデータ種数の明示が見つからない（load {n_load} / 配布 {n_dist}）")

    print("C5  assemble NOTEBOOKS が実在")
    for name in anbs:
        if (NB / name).exists():
            ok(name)
        else:
            fail("C5", f"assemble NOTEBOOKS の {name} が notebooks/ に無い")

    print("C5b  入口ページ用 site_environment JSON が最新")
    env_json = ROOT / "webapp" / "react" / "src" / "data" / "siteEnvironment.generated.json"
    env_csv = DATA / "site_environment.csv"
    if not env_json.exists():
        warn("C5b", "siteEnvironment.generated.json が無い（gen_site_env.py を実行）")
    elif env_csv.stat().st_mtime > env_json.stat().st_mtime:
        warn("C5b", "site_environment.csv が JSON より新しい（gen_site_env.py を実行）")
    else:
        ok("siteEnvironment.generated.json は site_environment.csv と同期")

    print("C6  teacher_guide が参照するノートブック名")
    tg = (ROOT / "docs" / "teacher_guide_course.md").read_text(encoding="utf-8")
    for name in re.findall(r"`?([a-z_]+\.ipynb)`?", tg):
        if (NB / name).exists():
            ok(name)
        else:
            fail("C6", f"teacher_guide が参照する {name} が存在しない")


def check_execute() -> None:
    print("C7  nbconvert --execute（全ノートブック）")
    _, anbs = assemble_lists()
    for name in anbs:
        path = NB / name
        r = subprocess.run(
            [sys.executable, "-m", "nbconvert", "--to", "notebook", "--execute",
             "--output", str(Path(__file__).parent / "_exec_check.ipynb"), str(path)],
            capture_output=True, text=True, cwd=str(NB),
        )
        if r.returncode == 0:
            ok(f"{name} 実行 OK")
        else:
            tail = (r.stderr or r.stdout).strip().splitlines()[-3:]
            fail("C7", f"{name} 実行失敗: {' / '.join(tail)}")
    tmp = Path(__file__).parent / "_exec_check.ipynb"
    if tmp.exists():
        tmp.unlink()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="全ノートブックを実行して確認（数分）")
    args = ap.parse_args()

    print("=" * 60)
    print("整合性チェック  (requirements_v3.3.md I7)")
    print("=" * 60)
    check_structure()
    if args.execute:
        check_execute()
    else:
        print("C7  スキップ（--execute で有効化）")

    print("\n" + "=" * 60)
    if FAILS:
        print(f"NG: {len(FAILS)} 件の不整合")
        for x in FAILS:
            print("  -", x)
        if WARNS:
            print(f"（警告 {len(WARNS)} 件）")
        return 1
    print("OK: 構造チェック通過" + ("（+ ノートブック実行）" if args.execute else ""))
    if WARNS:
        print(f"警告 {len(WARNS)} 件:")
        for x in WARNS:
            print("  -", x)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
