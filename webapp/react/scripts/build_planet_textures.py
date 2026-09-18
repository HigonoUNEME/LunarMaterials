# -*- coding: utf-8 -*-
"""3D入口ページに「遊び心で」置く地球・太陽の見た目用テクスチャを用意する。

Solar System Scope の texture pack（3D可視化専用に作られた、CGI Moon Kit と同じ性格のアセット。
NASA Blue Marble / SDO のデータを元に再構成）から、地球（昼面）と太陽の等距円筒テクスチャ
（各2048×1024）を取得する。実際の見た目の大きさ・角度は Python 側では決めず、
MoonViewer3D.tsx が実際の半径・距離の比から見かけの角度を計算して球のサイズを決める。

    python webapp/react/scripts/build_planet_textures.py

出典：Solar System Scope Textures https://www.solarsystemscope.com/textures/
      ライセンス：CC BY 4.0（https://creativecommons.org/licenses/by/4.0/）。
      「地球」は NASA Blue Marble 相当の昼面カラー合成、「太陽」は NASA/SDO 由来の光球面画像を
      3D 用に再構成したもの（同サイトの説明による）。改変：JPEG再圧縮のみ（解像度は変更なし）。
"""
import os
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")
TEX_OUT = os.path.join(os.path.dirname(HERE), "public", "textures")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(TEX_OUT, exist_ok=True)

BASE_URL = "https://www.solarsystemscope.com/textures/download/"
ITEMS = [
    # (ソースファイル名, キャッシュ名, 出力名, JPEG品質)
    ("2k_earth_daymap.jpg", "earth_daymap_2k_src.jpg", "earth_daymap_2k.jpg", 90),
    ("2k_sun.jpg", "sun_2k_src.jpg", "sun_2k.jpg", 90),
]


def _download(url_name: str, cache_name: str) -> str:
    path = os.path.join(CACHE, cache_name)
    if not os.path.exists(path):
        print(f"download {BASE_URL}{url_name}")
        urllib.request.urlretrieve(BASE_URL + url_name, path)
    return path


def main() -> None:
    for url_name, cache_name, out_name, quality in ITEMS:
        src = _download(url_name, cache_name)
        im = Image.open(src).convert("RGB")
        out_path = os.path.join(TEX_OUT, out_name)
        im.save(out_path, "JPEG", quality=quality, optimize=True)
        print(f"wrote {out_path}  {im.size}  ({os.path.getsize(out_path)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
