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

関数の分類（teacher_guide / helpersheet のヘルパー一覧もこの2階層で書く）:

  【core】まず覚える。ガイド型の本体で使う
    load / region / nearest / summary / summary_by / grid_count / scatter / hist / site_score

  【extended】必要になったら使う。地域選択・極域・発展編・前処理の補助
    south_pole / north_pole / region_type / earth_elevation / near_maria
    dist_to_permanent_shadow / box_area_km2 / classify_by_box / join_grid
    diurnal_curve / daily_swing

  site_score と region_type だけは中身が数行を超える。それぞれの docstring と
  本体のコメントに、何をしているか（正規化と重み付き和／緯度経度の箱で切り出し）を書いてある。

使い方:
    from moonkit import *
    温度 = load('温度')
    赤道 = region(温度, lat=(-10, 10))
    summary(赤道, 'temp_noon_K', 'temp_midnight_K')   # 平均・分散など
    diurnal_curve(赤道)                               # 1日の温度変化カーブ

'温度'（Diviner）データは、地点ごとに現地時間 0〜23時の温度 `t_lt00`〜`t_lt23` を持つ
（Williams et al. 2017 の瞬間温度マップ24枚を現地時間に位相合わせしたもの）。
昼夜の変化カーブが意味を持つのは概ね |緯度| < 70度。極付近は太陽が地平線近くを
回るだけで「昼夜」がはっきりせず、カーブは平坦・不規則になる（物理的にそうなる）。
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

__all__ = [
    # --- core（まず覚える）---
    'load', 'DATASETS', 'LT_COLS',
    'region', 'nearest',
    'summary', 'summary_by', 'grid_count',
    'scatter', 'hist', 'site_score',
    # --- extended（必要になったら）---
    'south_pole', 'north_pole', 'region_type', 'earth_elevation',
    'near_maria', 'dist_to_permanent_shadow',
    'box_area_km2', 'classify_by_box', 'join_grid',
    'diurnal_curve', 'daily_swing',
]

# Diviner の現地時間 0〜23時の温度列
LT_COLS = [f't_lt{h:02d}' for h in range(24)]

_R_MOON_KM = 1737.4  # 月の半径

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
    'クレーター深さ':   'craters_3d.csv',              # Wang & Wu 2021（直径・深さ。※現在の劣化した深さ）
    'クレーター年代':   'deepcraters.csv',             # DeepCraters（推定地質年代 1〜5）
    '温度':             'diviner_global.csv.gz',       # Diviner（現地時間0〜23時の温度カーブ）
    '極域日照':         'lola_polar_illumination.csv',  # LOLA（南極・北極の日照率・永久影率・傾斜 slope_deg）
    '地質':             'moon_geology_grid.csv',       # USGS 統合地質図（1度グリッド。海陸・相対年代の“答え合わせ”用）
    '着陸地点':         'landing_sites.csv',           # 実在の着陸地点・Artemis候補地・参照地形（手キュレーション）
    '夜の温度':         'diviner_nighttime.csv.gz',    # Diviner 夜の最低温度と異常（岩の多さ＝熱物性の代理。発展・クラスタリング用）
    'アイソクロン':     'isochron_reference.csv',      # クレーター密度→絶対年代の参照表（Neukum PF+編年関数。発展）
    '環境':             'site_environment.csv',        # 全球1度グリッドの環境指標（海陸・温度・地球可視性・傾斜。南極以外も同じ土俵で評価）
    '地域':             'candidate_regions.csv',       # 候補地域アーキタイプ（赤道の海／裏側／溶岩チューブ…。region_type で箱に切り出す）
    '縦孔':             'lunar_pits.csv',              # 溶岩チューブの天窓（放射線・熱の遮蔽＝長期滞在の候補地）
}

_AGE_NAMES = {
    1: '1:Pre-Nectarian(最も古い)', 2: '2:Nectarian', 3: '3:Imbrian',
    4: '4:Eratosthenian', 5: '5:Copernican(最も新しい)',
}


def load(key):
    """データセットを日本語キーで読み込んで DataFrame を返す。

    使えるキー: 'クレーター' / 'クレーター深さ' / 'クレーター年代' / '温度' / '極域日照'
              / '地質'（海陸・相対年代の答え合わせ用）/ '着陸地点'（実在の着陸地点）
              / '夜の温度'（夜の最低温度と異常。発展・クラスタリング用）
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
    """南極側（緯度 <= -deg）だけにしぼる。

    注意：`load('極域日照')` は南北 |緯度|≳83度 しか収録していない（日照率・傾斜・永久影率は
    極域専用データ）。赤道・中緯度・裏側を評価したいときは `load('環境')` と `region_type()` を使う。
    """
    lat_c, _ = _latlon_cols(df)
    return df[df[lat_c] <= -deg].copy()


def north_pole(df, deg=80):
    """北極側（緯度 >= deg）だけにしぼる。"""
    lat_c, _ = _latlon_cols(df)
    return df[df[lat_c] >= deg].copy()


def box_area_km2(lat, lon):
    """緯度経度の四角い範囲の、球面上の面積 [km^2]。

        box_area_km2(lat=(20, 45), lon=(-40, -5))   # 雨の海のあたり
    月半径 1737.4 km。area = R^2 · Δλ · (sinφ2 − sinφ1)。
    """
    la = np.deg2rad(sorted(lat))
    lo = np.deg2rad(sorted(lon))
    return float(_R_MOON_KM ** 2 * (lo[1] - lo[0]) * (np.sin(la[1]) - np.sin(la[0])))


def nearest(df, lat, lon, n=1):
    """指定した緯度・経度にいちばん近い行を返す（グリッドデータを『実在の地点』で引く）。

        nearest(load('温度'), 0.674, 23.473)        # Apollo 11 の場所の温度カーブ
        nearest(load('地質'), -69.37, 32.35)        # Chandrayaan-3 の場所の地質
        nearest(load('極域日照'), -86.0, -2.9, n=5)  # Malapert Massif 近傍5点
    """
    lat_c, lon_c = _latlon_cols(df)
    dlat = df[lat_c] - lat
    dlon = ((df[lon_c] - lon + 180) % 360 - 180) * np.cos(np.deg2rad(lat))
    d = np.hypot(dlat, dlon)
    out = df.assign(_km=(d * 1737.4 * np.pi / 180)).nsmallest(n, '_km')
    return out.iloc[0] if n == 1 else out


def region_type(df, name):
    """名前つきの候補地域（`data/candidate_regions.csv`）の緯度経度の箱で df を切り出す。

        赤道の海 = region_type(load('環境'), '赤道の海（静かの海）')
        裏側     = region_type(load('環境'), '裏側・赤道（電波天文の候補域）')
        site_score(裏側, {'earth_elev_deg': ('低い', 3), 'temp_amp_K': ('低い', 2)})

    使える名前は `load('地域')['name']` で一覧できる。'南極（Shackleton…）' のように
    経度が -180〜180 全域の箱は緯度だけでしぼる。
    """
    path = _find('data', 'candidate_regions.csv')
    if path is None:
        raise FileNotFoundError('candidate_regions.csv')
    regions = pd.read_csv(path)
    hit = regions[regions['name'] == name]
    if hit.empty:
        raise ValueError(f"地域名が見つかりません: {name}\n"
                         f"使える名前: {'／'.join(regions['name'])}")
    r = hit.iloc[0]
    lat_c, lon_c = _latlon_cols(df)
    m = df[lat_c].between(r['lat_min'], r['lat_max'])
    lo_min, lo_max = float(r['lon_min']), float(r['lon_max'])
    if not (lo_min <= -179.9 and lo_max >= 179.9):        # 全経度指定でなければ経度もしぼる
        if lo_max > 180:                                   # +180度をまたぐ箱（裏側など）
            m &= (df[lon_c] >= lo_min) | (df[lon_c] <= lo_max - 360)
        else:
            m &= df[lon_c].between(lo_min, lo_max)
    return df[m].copy()


def earth_elevation(lat, lon):
    """ある地点から見た地球のおおよその仰角 [度]。正なら表側、負なら裏側（地球が地平線の下）。

        earth_elevation(0.674, 23.473)     # Apollo 11 ≒ +66（地球がほぼ真上）
        earth_elevation(-45.44, 177.60)    # Chang'e 4（裏側）< 0

    sub-Earth 点を（緯度0, 経度0）とみなし、そこからの角距離を 90度から引いた近似。
    秤動（±約7度）は無視。`load('環境')` の `earth_elev_deg` 列と同じ計算。
    """
    ang = np.degrees(np.arccos(np.clip(
        np.cos(np.radians(lat)) * np.cos(np.radians(lon)), -1.0, 1.0)))
    return float(90.0 - ang)


def classify_by_box(df, boxes, colname='区分', other='その他'):
    """緯度・経度の四角い範囲で地点にラベルを付けた列を足す（例: 海 と 陸 を分ける）。

    1つのラベルに箱を複数与えたいときは、箱をリストにする。

        boxes = {
            '海': [{'lat': (20, 50), 'lon': (-40, 5)},     # 雨の海
                   {'lat': (-5, 20), 'lon': (18, 45)}],    # 静かの海
            '陸': {'lat': (-55, -25), 'lon': (-15, 35)},   # 南の高地
        }
        classify_by_box(クレーター, boxes)   # どの箱にも入らない地点は 'その他'
    """
    lat_c, lon_c = _latlon_cols(df)
    out = df.copy()
    out[colname] = other
    for label, box in boxes.items():
        for b in (box if isinstance(box, list) else [box]):
            m = pd.Series(True, index=out.index)
            if 'lat' in b:
                m &= out[lat_c].between(b['lat'][0], b['lat'][1])
            if 'lon' in b:
                m &= out[lon_c].between(b['lon'][0], b['lon'][1])
            out.loc[m, colname] = label
    return out


def join_grid(left, right, value_cols, step=0.5):
    """left の各地点に、同じ緯度経度マス（step 度）にある right の列（value_cols の平均）を
    くっつけて返す。粒度の違うデータセットを緯度経度でつなぐときに使う。

        極 = south_pole(load('極域日照'))
        極 = join_grid(極, daily_swing(load('温度')), ['t_swing_K'])
    """
    if isinstance(value_cols, str):
        value_cols = [value_cols]
    lla, llo = _latlon_cols(left)
    rla, rlo = _latlon_cols(right)
    key_r = list(zip(np.floor(right[rla] / step) * step, np.floor(right[rlo] / step) * step))
    agg = right.assign(_gk=key_r).groupby('_gk')[value_cols].mean()
    key_l = list(zip(np.floor(left[lla] / step) * step, np.floor(left[llo] / step) * step))
    return left.assign(_gk=key_l).join(agg, on='_gk').drop(columns='_gk')


def _greatcircle_km(lat1, lon1, lat2, lon2):
    """月面上の2点間の距離 [km]（大円距離）。lat1/lon1 は配列、lat2/lon2 はスカラーでよい。"""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return _R_MOON_KM * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def near_maria(df, scale=0.8, colname='区分'):
    """各地点が「月の海（マリア）」の中でどうかを判定して `海`/`陸` のラベル列を足す。

    USGS 地名辞典の23の海・大洋の中心座標と半径（`data/maria_boundaries.csv`）を使う。
    ある海の中心から (その海の半径 × scale) km 以内なら『海』。scale を下げると中心部だけになる。

        c = near_maria(load('クレーター'), scale=0.8)
        summary_by(c, group='区分', value='diam_km')
    """
    path = _find('data', 'maria_boundaries.csv')
    if path is None:
        raise FileNotFoundError('maria_boundaries.csv')
    maria = pd.read_csv(path)
    lat_c, lon_c = _latlon_cols(df)
    lat = df[lat_c].to_numpy()
    lon = df[lon_c].to_numpy()
    inside = np.zeros(len(df), dtype=bool)
    for _, m in maria.iterrows():
        inside |= _greatcircle_km(lat, lon, m['center_lat'], m['center_lon']) <= m['radius_km'] * scale
    out = df.copy()
    out[colname] = np.where(inside, '海', '陸')
    return out


def dist_to_permanent_shadow(df, threshold=0.9, colname='km_to_shadow'):
    """各地点から、いちばん近い永久影までの「おおよその距離」[km] を `km_to_shadow` 列として足す。

    永久影＝`permanent_shadow_fraction >= threshold` の地点。極付近を平面に近似し、
    最近傍探索（scipy.spatial.cKDTree）で距離を求める。**'極域日照'（|緯度|≳83度）専用**。
    赤道・中緯度・裏側には永久影も永久影データも無いので、この関数は使えない。

        極 = dist_to_permanent_shadow(south_pole(load('極域日照')))
    """
    from scipy.spatial import cKDTree

    lat_c, lon_c = _latlon_cols(df)
    lat = df[lat_c].to_numpy()
    lon = df[lon_c].to_numpy()
    # 極からの角距離 r[deg] と経度 theta で平面座標に（1度 ≒ π/180 × 月半径 km）
    deg_km = np.radians(1.0) * _R_MOON_KM
    r = (90.0 - np.abs(lat)) * deg_km
    th = np.radians(lon)
    x, y = r * np.cos(th), r * np.sin(th)

    is_psr = df['permanent_shadow_fraction'].to_numpy() >= threshold
    if not is_psr.any():
        raise ValueError(f'permanent_shadow_fraction >= {threshold} の地点がありません')
    tree = cKDTree(np.c_[x[is_psr], y[is_psr]])
    d, _ = tree.query(np.c_[x, y], k=1)
    out = df.copy()
    out[colname] = d
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

    if not is_map and x != y and plot_df[x].dtype.kind in 'if' and plot_df[y].dtype.kind in 'if':
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
    # 0) want に挙げた列のうち、この df では全部欠測のもの（例：南極で slope_deg）は
    #    使えないので外す（クラッシュせず、何を外したか知らせる）
    want = dict(want)
    for col in [c for c in list(want) if c in df.columns and df[c].isna().all()]:
        print(f'※ {col} はこの範囲では全部欠測のため、スコアから外しました')
        want.pop(col)
    # 1) want に挙げた列に欠測がある行は落とす（比べられないので）
    out = df.dropna(subset=list(want)).copy()
    total_w = sum(w for _, w in want.values())
    score = pd.Series(0.0, index=out.index)
    for col, (direction, w) in want.items():
        s = out[col]
        # 2) min–max 正規化：その列の最小→0、最大→1 に直す（Excel なら =(x-MIN)/(MAX-MIN)）
        lo, hi = s.min(), s.max()
        norm = (s - lo) / (hi - lo) if hi > lo else pd.Series(0.5, index=out.index)
        # 3) 「低いほどよい」指標は向きを反転（1 から引く）
        if direction in ('低い', 'low', '小さい'):
            norm = 1 - norm
        out[f'_norm_{col}'] = norm          # 途中経過も列に残す（ブラックボックスにしない）
        # 4) 重みをかけて足していく
        score += w * norm
    # 5) 重みの合計で割って 0〜1 に戻したものが「スコア」
    out['スコア'] = score / total_w
    out = out.sort_values('スコア', ascending=False)
    return out.head(top) if top is not None else out


# --------------------------------------------------------------------------
# 温度の1日の変化（Diviner の t_lt00〜t_lt23 を使う。層2a ステップ1）
# --------------------------------------------------------------------------
def diurnal_curve(df, show=True):
    """（しぼり込んだ）温度データの、現地時間ごとの平均温度カーブを描く／返す。

        赤道 = region(load('温度'), lat=(-5, 5))
        diurnal_curve(赤道)

    返り値は現地時間 0〜23時の平均温度（24個）の Series。
    """
    mean_curve = df[LT_COLS].mean()
    mean_curve.index = range(24)
    if show:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(range(24), mean_curve.values, marker='o')
        ax.set_xlabel('現地時間 [時]')
        ax.set_ylabel('平均温度 [K]')
        ax.set_xticks(range(0, 24, 3))
        ax.set_title(f'1日の温度変化（{len(df):,} 地点の平均）')
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()
        swing = mean_curve.max() - mean_curve.min()
        print(f'いちばん暑い時刻: {mean_curve.idxmax()}時（{mean_curve.max():.0f} K）')
        print(f'いちばん寒い時刻: {mean_curve.idxmin()}時（{mean_curve.min():.0f} K）')
        print(f'1日の気温差（平均カーブの最大－最小）: {swing:.0f} K')
    return mean_curve


def daily_swing(df):
    """各地点について、1日の温度カーブ（t_lt00〜t_lt23）から
    平均・較差（最大－最小）・標準偏差 を計算した列を足して返す。

        band = daily_swing(region(load('温度'), lat=(-5, 5)))
        summary(band, 't_mean_K', 't_swing_K', 't_std_K')
    """
    out = df.copy()
    t = out[LT_COLS]
    out['t_mean_K'] = t.mean(axis=1)
    out['t_swing_K'] = t.max(axis=1) - t.min(axis=1)
    out['t_std_K'] = t.std(axis=1)
    return out
