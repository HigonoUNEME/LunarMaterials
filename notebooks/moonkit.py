# -*- coding: utf-8 -*-
"""moonkit — 月データ探索教材の解析ヘルパー（層1）

要件定義書 Ver.1.5 の「層1：解析ヘルパー」。生徒（および教員）が、コードのエラーで
止まらずに「データを見る／比べる／しぼる」を行えるようにする、薄い関数の集まり。

方針（Ver.1.5 §3.4）:
- 各関数の中身は数行。返り値は DataFrame や配列など「中身が見える形」にする。
- 機械学習ライブラリ（scikit-learn 等）はこのファイルでは使わない
  （機械学習の1ステップは moonkit_ml.py に分離）。
- 情報Ⅰの範囲（平均・分散・相関・件数・閾値・重み付き和）を超える処理を関数の中に隠さない。
- サンプリングを行う関数は乱数の種を固定し、実行ごとに結果が変わらないようにする。

使い方:
    from moonkit import *
    温度 = load('温度')
    赤道 = region(温度, lat=(-10, 10))
    summary(赤道, 'temp_noon_K', 'temp_midnight_K')   # 平均・分散など
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

__all__ = [
    'load', 'DATASETS',
    'region', 'south_pole', 'north_pole', 'classify_by_box',
    'summary', 'summary_by', 'grid_count',
    'scatter', 'hist', 'site_score',
]

# --------------------------------------------------------------------------
# ファイルの場所を探す（Colab／ローカル、カレントが repo 直下でも notebooks/ でも動くように）
# --------------------------------------------------------------------------
_SEARCH_ROOTS = ('.', '..', '../..', os.path.dirname(os.path.abspath(__file__)),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def _find(*relparts):
    rel = os.path.join(*relparts)
    for root in _SEARCH_ROOTS:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            return p
    return None


# --------------------------------------------------------------------------
# 日本語フォント（explore.ipynb と同じ同梱フォントを使う。無ければ警告のみ）
# --------------------------------------------------------------------------
_font_path = _find('notebooks', 'assets', 'NotoSansJP-Regular.ttf') or _find('assets', 'NotoSansJP-Regular.ttf')
if _font_path:
    fm.fontManager.addfont(_font_path)
    plt.rcParams['font.family'] = fm.FontProperties(fname=_font_path).get_name()
else:
    print('⚠️ 日本語フォント(assets/NotoSansJP-Regular.ttf)が見つかりません。'
          'グラフの日本語表示が文字化けする可能性があります。')

# 月面背景画像（散布図の背景用。NASA CGI Moon Kit, パブリックドメイン）
_moon_bg_path = _find('notebooks', 'assets', 'lroc_color_2k.jpg') or _find('assets', 'lroc_color_2k.jpg')
_MOON_BG = plt.imread(_moon_bg_path) if _moon_bg_path else None


# --------------------------------------------------------------------------
# データセット
# --------------------------------------------------------------------------
DATASETS = {
    'クレーター':       'craters_subset.csv',          # Robbins DB（緯度経度・直径・形）
    'クレーター深さ':   'craters_3d.csv',              # Wang & Wu 2021（直径・深さ）
    'クレーター年代':   'deepcraters.csv',             # DeepCraters（推定地質年代 1〜5）
    '温度':             'diviner_global.csv',          # Diviner（正午/深夜0時の温度・昼夜差）
    '極域日照':         'lola_polar_illumination.csv',  # LOLA（南極・北極の平均日照率・永久影率）
}

_AGE_NAMES = {
    1: '1:Pre-Nectarian(最も古い)', 2: '2:Nectarian', 3: '3:Imbrian',
    4: '4:Eratosthenian', 5: '5:Copernican(最も新しい)',
}


def load(key):
    """データセットを日本語キーで読み込んで DataFrame を返す。

    使えるキー: 'クレーター' / 'クレーター深さ' / 'クレーター年代' / '温度' / '極域日照'
    ファイル名（例 'diviner_global.csv'）を直接渡してもよい。
    """
    fname = DATASETS.get(key, key)
    path = _find('data', fname)
    if path is None:
        raise FileNotFoundError(
            f"データが見つかりません: {key}\n"
            f"使えるキー: {', '.join(DATASETS)}"
        )
    df = pd.read_csv(path)
    if fname == 'deepcraters.csv' and 'Age' in df.columns:
        df['Age_name'] = df['Age'].map(_AGE_NAMES)  # 年代を意味のわかる文字列にした列を足す
    return df


# --------------------------------------------------------------------------
# しぼり込み
# --------------------------------------------------------------------------
def _latlon_cols(df):
    """緯度・経度の列名を返す（データセットによって 'lat/lon' と 'Lat/Lon' がある）。"""
    lat = next((c for c in df.columns if c.lower() == 'lat'), None)
    lon = next((c for c in df.columns if c.lower() == 'lon'), None)
    return lat, lon


def region(df, lat=None, lon=None):
    """緯度・経度の範囲でデータをしぼる。

        region(温度, lat=(-10, 10))              # 緯度 -10〜10度
        region(クレーター, lat=(60, 90), lon=(-30, 30))
    """
    lat_c, lon_c = _latlon_cols(df)
    out = df
    if lat is not None:
        out = out[(out[lat_c] >= lat[0]) & (out[lat_c] <= lat[1])]
    if lon is not None:
        out = out[(out[lon_c] >= lon[0]) & (out[lon_c] <= lon[1])]
    return out.copy()


def south_pole(df, deg=80):
    """南極側（緯度 <= -deg）だけにしぼる。"""
    lat_c, _ = _latlon_cols(df)
    return df[df[lat_c] <= -deg].copy()


def north_pole(df, deg=80):
    """北極側（緯度 >= deg）だけにしぼる。"""
    lat_c, _ = _latlon_cols(df)
    return df[df[lat_c] >= deg].copy()


def classify_by_box(df, boxes, colname='区分', other='その他'):
    """緯度・経度の四角い範囲で地点にラベルを付けた列を足す（例: 海 と 陸 を分ける）。

        boxes = {
            '雨の海あたり': {'lat': (15, 45), 'lon': (-30, 5)},
            '高地あたり':   {'lat': (-60, -30), 'lon': (0, 60)},
        }
        classify_by_box(クレーター, boxes)   # 'その他' はどの箱にも入らなかった地点
    """
    lat_c, lon_c = _latlon_cols(df)
    out = df.copy()
    out[colname] = other
    for label, box in boxes.items():
        m = pd.Series(True, index=out.index)
        if 'lat' in box:
            m &= out[lat_c].between(box['lat'][0], box['lat'][1])
        if 'lon' in box:
            m &= out[lon_c].between(box['lon'][0], box['lon'][1])
        out.loc[m, colname] = label
    return out


# --------------------------------------------------------------------------
# 要約統計
# --------------------------------------------------------------------------
def summary(df, *cols):
    """指定した列の 件数・平均・標準偏差・分散・最小・最大 を表にして返す。

        赤道 = region(温度, lat=(-10, 10))
        summary(赤道, 'temp_noon_K', 'temp_midnight_K')
    """
    cols = list(cols) if cols else [c for c in df.columns if df[c].dtype.kind in 'if']
    rows = {}
    for c in cols:
        s = df[c].dropna()
        rows[c] = {'件数': len(s), '平均': s.mean(), '標準偏差': s.std(),
                   '分散': s.var(), '最小': s.min(), '最大': s.max()}
    return pd.DataFrame(rows).T


def summary_by(df, group, value):
    """group 列の値ごとに、value 列の 件数・平均・標準偏差・分散 を表にして返す。

        c = classify_by_box(クレーター, boxes)
        summary_by(c, group='区分', value='diam_km')
    """
    g = df.dropna(subset=[group, value]).groupby(group)[value]
    tbl = g.agg(件数='count', 平均='mean', 標準偏差='std', 分散='var')
    return tbl


def grid_count(df, lat_step=10, lon_step=10, show=True):
    """緯度・経度をビンに分けて、そのマスに入る件数を数える（クレーター密度など）。

    返り値は「行=緯度ビン, 列=経度ビン」の表。show=True でヒートマップも描く。
    """
    lat_c, lon_c = _latlon_cols(df)
    lat_bins = np.arange(-90, 90 + lat_step, lat_step)
    lon_bins = np.arange(-180, 180 + lon_step, lon_step)
    lat_cut = pd.cut(df[lat_c], lat_bins)
    lon_cut = pd.cut(df[lon_c], lon_bins)
    tbl = df.groupby([lat_cut, lon_cut], observed=False).size().unstack(fill_value=0)
    tbl = tbl.iloc[::-1]  # 上が北になるように
    if show:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        im = ax.imshow(tbl.values, aspect='auto', cmap='inferno',
                       extent=[-180, 180, -90, 90])
        fig.colorbar(im, ax=ax, label='この範囲に入った件数')
        ax.set_xlabel('経度 [度]')
        ax.set_ylabel('緯度 [度]')
        ax.set_title(f'{lat_step}度 × {lon_step}度のマスごとの件数')
        plt.tight_layout()
        plt.show()
    return tbl


# --------------------------------------------------------------------------
# 図
# --------------------------------------------------------------------------
def scatter(df, x, y, color=None, moon_bg=True, logx=False, logy=False,
            max_points=3000, seed=0):
    """散布図を描く。x・y が緯度・経度なら月面画像を背景に敷く。

        scatter(クレーター深さ, 'diameter_km', 'depth_km')
        scatter(クレーター, 'lon', 'lat', color='diam_km')
    """
    n = min(len(df), max_points)
    plot_df = df.sample(n=n, random_state=seed) if len(df) > n else df

    lat_c, lon_c = _latlon_cols(df)
    is_map = (x == lon_c and y == lat_c)

    fig, ax = plt.subplots(figsize=(7, 6))
    if is_map and moon_bg and _MOON_BG is not None:
        ax.imshow(_MOON_BG, extent=[-180, 180, -90, 90], aspect='auto', alpha=0.6, zorder=0)
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)

    if color is not None and color in plot_df.columns:
        if plot_df[color].dtype.kind in 'if':
            sc = ax.scatter(plot_df[x], plot_df[y], c=plot_df[color], cmap='plasma',
                            s=8, alpha=0.8, zorder=2)
            fig.colorbar(sc, ax=ax, label=color)
        else:  # 文字列などのカテゴリは色を割り当てて凡例を出す
            cats = plot_df[color].astype('category')
            sc = ax.scatter(plot_df[x], plot_df[y], c=cats.cat.codes, cmap='viridis',
                            s=8, alpha=0.75, zorder=2)
            handles, _ = sc.legend_elements()
            ax.legend(handles, list(cats.cat.categories), title=color,
                      bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        ax.scatter(plot_df[x], plot_df[y], s=8, alpha=0.5, zorder=2)

    try:
        if logx:
            ax.set_xscale('log')
        if logy:
            ax.set_yscale('log')
    except ValueError:
        print('⚠️ 0以下の値が含まれているため、その軸は対数目盛りにできません。')

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f'表示 {n:,} / 全 {len(df):,} 件')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    if x != y and plot_df[x].dtype.kind in 'if' and plot_df[y].dtype.kind in 'if':
        r = plot_df[[x, y]].corr().iloc[0, 1]
        print(f'相関係数 r = {r:.3f}')


def hist(df, col, bins=40, vline=None):
    """ヒストグラム（度数分布）を描く。vline にしきい値を渡すと赤い線を引く。

        hist(south_pole(極域日照), 'average_illumination_percent', vline=5)
    """
    s = df[col].dropna()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(s, bins=bins, color='steelblue', alpha=0.8)
    if vline is not None:
        ax.axvline(vline, color='crimson', linestyle='--', label=f'しきい値 {vline}')
        ax.legend()
    ax.set_xlabel(col)
    ax.set_ylabel('地点数')
    ax.set_title(f'{col} のヒストグラム（{len(s):,} 件）')
    plt.tight_layout()
    plt.show()


# --------------------------------------------------------------------------
# 複数の指標を1つのスコアに束ねる（層2a ステップ4：最適地の提案）
# --------------------------------------------------------------------------
def site_score(df, want, top=10):
    """複数の列を「0〜1のスコア」に直して重み付き平均を取り、点数の高い地点を返す。

        want = {
            'average_illumination_percent': ('高い', 2),   # 日照率は高いほどよい（重み2）
            'permanent_shadow_fraction':    ('低い', 1),   # 永久影は少ないほどよい（重み1）
        }
        site_score(south_pole(極域日照), want, top=10)

    各列を (値 - 最小) / (最大 - 最小) で 0〜1 に直し、'低い' なら 1 から引く。
    それらを重みで加重平均したものが 'スコア' 列（0〜1、大きいほど条件に合う）。
    """
    out = df.copy()
    total_w = sum(w for _, w in want.values())
    score = pd.Series(0.0, index=out.index)
    for col, (direction, w) in want.items():
        s = out[col]
        lo, hi = s.min(), s.max()
        norm = (s - lo) / (hi - lo) if hi > lo else pd.Series(0.5, index=out.index)
        if direction in ('低い', 'low', '小さい'):
            norm = 1 - norm
        out[f'_norm_{col}'] = norm
        score += w * norm
    out['スコア'] = score / total_w
    return out.sort_values('スコア', ascending=False).head(top)
