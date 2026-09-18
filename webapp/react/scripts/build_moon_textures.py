# -*- coding: utf-8 -*-
"""3D入口ページの月面テクスチャを、ズームしたときだけ高解像度に差し替えられるように準備する。

NASA SVS「CGI Moon Kit」(ID 4720, 2019年版) の LROC カラーモザイクを 4K・8K で取得し、
JPEG に変換して public/textures/ に置く（2K 版は既存のものをそのまま使う）。
生データ（TIFF、13MB・51MB）はリポジトリに含めない（_cache/ に置き .gitignore 済み）。
MoonViewer3D.tsx はカメラ距離に応じて 2K→4K→8K を切り替える（初期表示は軽い 2K のまま）。

    python webapp/react/scripts/build_moon_textures.py

出典：NASA SVS CGI Moon Kit https://svs.gsfc.nasa.gov/4720
      "This image is optimized for aesthetics, not science."（可視化用。パブリックドメイン、NASA画像の慣例に準拠）
      同じ 4k 版は docs/build_mare_outline.py でも使用（マリアの輪郭抽出用）。
"""
import os
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")
TEX_OUT = os.path.join(os.path.dirname(HERE), "public", "textures")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(TEX_OUT, exist_ok=True)

BASE_URL = "https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/"
TIERS = [
    # (ソースファイル名, 出力JPEG名, JPEG品質)
    ("lroc_color_poles_4k.tif", "moon_lroc_color_4k.jpg", 90),
    ("lroc_color_poles_8k.tif", "moon_lroc_color_8k.jpg", 88),
]


def _download(name: str) -> str:
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        print(f"download {BASE_URL}{name}")
        urllib.request.urlretrieve(BASE_URL + name, path)
    return path


def main() -> None:
    for src_name, out_name, quality in TIERS:
        src = _download(src_name)
        im = Image.open(src).convert("RGB")
        out_path = os.path.join(TEX_OUT, out_name)
        im.save(out_path, "JPEG", quality=quality, optimize=True)
        print(f"wrote {out_path}  {im.size}  ({os.path.getsize(out_path)/1024/1024:.1f} MB, "
              f"元TIFF {os.path.getsize(src)/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
