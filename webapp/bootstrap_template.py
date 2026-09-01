# === 準備（さわらないでください。ブラウザ版では実行に1分ほどかかります）===
# ローカル / Colab では何もしません。JupyterLite（ブラウザ）のときだけ、
# 必要なパッケージと教材ファイルを読み込みます。
import sys, os
if sys.platform == "emscripten":
    import piplite
    await piplite.install(["ipywidgets"])          # noqa: F704  (top-level await は JupyterLite で有効)
    import numpy, pandas, matplotlib, scipy, sklearn   # noqa: F401  (Pyodide にパッケージを読み込ませる)
    import js
    from pyodide.http import pyfetch
    _base = js.location.pathname.split("/extensions/")[0]
    _files = __FILE_LIST__
    for _f in _files:
        if not os.path.exists(_f):
            os.makedirs(os.path.dirname(_f) or ".", exist_ok=True)
            _r = await pyfetch(_base + "/files/" + _f)   # noqa: F704
            with open(_f, "wb") as _fh:
                _fh.write(await _r.bytes())              # noqa: F704
    if "" not in sys.path:
        sys.path.insert(0, "")
    print("OK: ブラウザ版の準備ができました")
