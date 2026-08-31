# -*- coding: utf-8 -*-
"""moonkit_ml — 機械学習モデルの比較（探究講座の任意ステップ6・要件 Ver.1.5 §4.5）

方針：**アルゴリズムの仕組みは教えない。**「1つの課題・2つの特徴量・1つの `train()`」で
モデルを取り替え、決定境界の形・正解率・「ルールを言葉で説明できるか」を比べる。
機械は生徒の判断を置き換える神託ではなく、手作業で決めた基準と突き合わせる
セカンドオピニオン。

`scikit-learn` はこのファイルでのみ使う（`moonkit.py` は機械学習を含まない）。
Colab には標準搭載。ローカルは `pip install scikit-learn`。

使い方:
    from moonkit import *
    from moonkit_ml import train
    極 = south_pole(load('極域日照'))
    train(極, features=['average_illumination_percent', 'lat'],
          label=(極['permanent_shadow_fraction'] >= 0.5),
          method='決定木', my_threshold=1)
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

__all__ = ['train', 'METHODS']

METHODS = ['ロジスティック回帰', '決定木', 'k近傍', 'ニューラルネット', 'ランダムフォレスト']

# このモデルは「なぜそう判定したか」を人が言葉で説明できるか
_READABLE = {
    'ロジスティック回帰': '△（各特徴量の重みは見えるが、式の形）',
    '決定木': '◯（if〜then のルールがそのまま読める）',
    'k近傍': '×（近くの例を見ているだけ。ルールは無い）',
    'ニューラルネット': '×（中の重みは人には読めない）',
    'ランダムフォレスト': '×（たくさんの木の多数決。全体像は読めない）',
}


def _build(method, 複雑さ, seed):
    hard = 複雑さ in ('高い', 'high', '複雑')
    if method == 'ロジスティック回帰':
        return make_pipeline(StandardScaler(), LogisticRegression())
    if method == '決定木':   # 木・森は目盛りに影響されないので、生の値のまま学習する
        return DecisionTreeClassifier(max_depth=(None if hard else 3), random_state=seed)
    if method == 'k近傍':
        return make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=(1 if hard else 15)))
    if method == 'ニューラルネット':
        return make_pipeline(StandardScaler(),
                             MLPClassifier(hidden_layer_sizes=((64, 64, 64) if hard else (16, 16)),
                                           max_iter=1000, random_state=seed))
    if method == 'ランダムフォレスト':
        return RandomForestClassifier(n_estimators=80,
                                      max_depth=(None if hard else 6), random_state=seed)
    raise ValueError(f"method は {METHODS} のどれか（'{method}' は不明）")


def train(df, features, label, method='決定木', 複雑さ='ふつう',
          n_sample=5000, test_size=0.3, seed=0, my_threshold=None, show=True):
    """2つの特徴量から label（0/1）を予測するモデルを学習し、決定境界と正解率を出す。

    features : 特徴量にする2つの列名のリスト（例 ['average_illumination_percent', 'lat']）
    label    : 0/1（または True/False）の列名、あるいは boolean の Series
    method   : METHODS のどれか
    複雑さ   : 'ふつう' か '高い'（'高い' で k近傍のkを1に・NNを大きく・木を深く＝過学習の実験）
    my_threshold : features[0] にこの値で縦線を引き、「自分のルール（features[0] <= しきい値）」の
                   正解率も一緒に表示する（ステップ3で決めたしきい値との比較用）
    """
    fx, fy = features
    d = df.copy()
    d['_y'] = np.asarray(label).astype(int) if not isinstance(label, str) else d[label].astype(int)
    d = d.dropna(subset=[fx, fy, '_y'])
    if len(d) > n_sample:
        d = d.sample(n=n_sample, random_state=seed)

    X = d[[fx, fy]].to_numpy()
    y = d['_y'].to_numpy()
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size,
                                          random_state=seed, stratify=y)
    model = _build(method, 複雑さ, seed)
    model.fit(Xtr, ytr)
    acc_tr, acc_te = model.score(Xtr, ytr), model.score(Xte, yte)
    base = max(y.mean(), 1 - y.mean())   # 「いつも多い方に賭ける」だけの正解率

    if show:
        print(f'モデル：{method}（複雑さ {複雑さ}）')
        print(f'  正解率  練習データ {acc_tr:.3f} / テストデータ {acc_te:.3f}'
              f'   （何も考えず多い方に賭けると {base:.3f}）')
        if acc_tr - acc_te > 0.03:
            print('  ⚠ 練習データに比べてテストの正解率がかなり低い＝「丸暗記（過学習）」ぎみ')
        print(f'  ルールを言葉で説明できる？：{_READABLE[method]}')
        if my_threshold is not None:
            mine = ((Xte[:, 0] <= my_threshold).astype(int) == yte).mean()
            print(f'  自分のルール「{fx} <= {my_threshold}」だけの正解率：{mine:.3f}')
        if method == '決定木':
            print('  この木が見つけたルール：')
            print(export_text(model, feature_names=[fx, fy]))
        _plot_boundary(model, Xte, yte, fx, fy, method, my_threshold)

    return {'model': model, 'テスト正解率': acc_te, '説明できる': _READABLE[method]}


def _plot_boundary(model, X, y, fx, fy, method, my_threshold):
    x0, x1 = X[:, 0].min(), X[:, 0].max()
    y0, y1 = X[:, 1].min(), X[:, 1].max()
    xx, yy = np.meshgrid(np.linspace(x0, x1, 300), np.linspace(y0, y1, 300))
    zz = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    # 境界線の形が見えるように、予測が横に切り替わる列＋少数派クラスの点の範囲へ横軸をよせる
    changes = np.where(np.any(np.diff(zz, axis=1) != 0, axis=0))[0]
    mino = 1 if (y == 1).mean() < 0.5 else 0
    xs = list(X[y == mino, 0])
    if len(changes):
        xs += [xx[0, changes.min()], xx[0, changes.max() + 1]]
    if xs:
        xa, xb = min(xs), max(xs)
        pad = 0.6 * (xb - xa) + 1e-6
        x0, x1 = max(x0, xa - pad), min(x1, xb + pad)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.contourf(xx, yy, zz, levels=[-0.5, 0.5, 1.5], colors=['#dfe7f2', '#f6d9c4'], alpha=0.9)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], s=6, c='#2b4c7e', label='実際に「0」', alpha=0.5)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], s=6, c='#c2571a', label='実際に「1」', alpha=0.6)
    if my_threshold is not None:
        ax.axvline(my_threshold, color='crimson', ls='--', lw=1.5,
                   label=f'自分のルール（{fx}={my_threshold}）')
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_xlabel(fx)
    ax.set_ylabel(fy)
    ax.set_title(f'{method} が引いた境界（色つき）と、テストデータの正解（点）')
    ax.legend(loc='best', fontsize=8)
    plt.tight_layout()
    plt.show()
