# -*- coding: utf-8 -*-
"""あらあら版の3コマ指導案（docs/lesson_plan_3koma_draft.md）を、一般的な学習指導案の様式
（単元設定の理由〈教材観・生徒観・指導観〉／単元の目標／評価規準／指導計画／本時の学習指導）
に整形してPDFにする。

    python docs/build_lesson_plan_pdf.py

出力：docs/lesson_plan_3koma.pdf
フォント：notebooks/assets/NotoSansJP-Regular.ttf（他のPDF教材と同じ、リポジトリ同梱のフォント）
"""
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "notebooks", "assets", "NotoSansJP-Regular.ttf")
OUT_PATH = os.path.join(ROOT, "docs", "lesson_plan_3koma.pdf")

pdfmetrics.registerFont(TTFont("NotoJP", FONT_PATH))

INK = colors.HexColor("#1f2933")
SUB = colors.HexColor("#52606d")
ACCENT = colors.HexColor("#0f4c81")
LINE = colors.HexColor("#9aa5b1")
HEAD_BG = colors.HexColor("#e4ecf7")

styles = {
    "title": ParagraphStyle("title", fontName="NotoJP", fontSize=17, leading=22,
                             textColor=INK, alignment=1, spaceAfter=4),
    "subtitle": ParagraphStyle("subtitle", fontName="NotoJP", fontSize=10.5, leading=15,
                                textColor=SUB, alignment=1, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="NotoJP", fontSize=13, leading=18,
                          textColor=colors.white, backColor=ACCENT,
                          leftIndent=6, spaceBefore=14, spaceAfter=8,
                          borderPadding=(4, 4, 4, 6)),
    "h2": ParagraphStyle("h2", fontName="NotoJP", fontSize=11, leading=16,
                          textColor=ACCENT, spaceBefore=10, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="NotoJP", fontSize=9.5, leading=15,
                            textColor=INK, spaceAfter=6),
    "note": ParagraphStyle("note", fontName="NotoJP", fontSize=8.5, leading=13,
                            textColor=SUB, spaceAfter=4),
    "cell": ParagraphStyle("cell", fontName="NotoJP", fontSize=8.7, leading=12.5,
                            textColor=INK),
    "cellhead": ParagraphStyle("cellhead", fontName="NotoJP", fontSize=9, leading=12.5,
                                textColor=ACCENT),
    "meta_k": ParagraphStyle("meta_k", fontName="NotoJP", fontSize=9, leading=13,
                              textColor=SUB),
    "meta_v": ParagraphStyle("meta_v", fontName="NotoJP", fontSize=9.5, leading=13,
                              textColor=INK),
}


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, styles[style])


def section(title: str):
    return P(title, "h1")


def table_grid(rows, col_widths, header_rows=1, row_heights=None):
    t = Table(rows, colWidths=col_widths, rowHeights=row_heights, repeatRows=header_rows)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "NotoJP"),
        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header_rows:
        style.append(("BACKGROUND", (0, 0), (-1, header_rows - 1), HEAD_BG))
    t.setStyle(TableStyle(style))
    return t


def build():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        topMargin=16 * mm, bottomMargin=16 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
        title="学習指導案：月データでムーンベースの場所を決めよう（3コマ・あらあら版）",
    )
    story = []

    # ---- 表紙相当 ----
    story.append(P("学習 指 導 案", "title"))
    story.append(P("（あらあら版・v1／今後の検討課題は末尾に記載）", "subtitle"))

    meta_rows = [
        [P("教科・科目", "meta_k"), P("探究基礎", "meta_v"),
         P("時数", "meta_k"), P("全3時間（50分×3コマ・計150分）", "meta_v")],
        [P("単元名", "meta_k"), P("月データでムーンベースの場所を決めよう", "meta_v"),
         P("対象", "meta_k"), P("高等学校第1学年　1学級（3〜4人班編成）", "meta_v")],
        [P("実施日", "meta_k"), P("未定", "meta_v"),
         P("指導者", "meta_k"), P("未定", "meta_v")],
        [P("使用教材", "meta_k"),
         P("① 3D入口Webアプリ　② 表計算ソフト（またはノートブック）　③ ワークシート", "meta_v"),
         "", ""],
    ]
    meta_t = Table(meta_rows, colWidths=[24 * mm, 62 * mm, 20 * mm, 62 * mm], rowHeights=None)
    meta_t.setStyle(TableStyle([
        ("SPAN", (1, 3), (3, 3)),
        ("FONTNAME", (0, 0), (-1, -1), "NotoJP"),
        ("BOX", (0, 0), (-1, -1), 0.8, INK),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (0, -1), HEAD_BG),
        ("BACKGROUND", (2, 0), (2, 1), HEAD_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 4 * mm))

    # ---- 1. 単元設定の理由 ----
    story.append(section("1．単元設定の理由"))
    story.append(P("（1）教材観", "h2"))
    story.append(P(
        "月の公開データ（クレーターの位置・大きさ、Diviner の温度、LOLA の地形・傾斜、USGS の地質図など）は、"
        "生の衛星画像処理や専門的な GIS 操作を必要とせず、前処理済みの CSV としてブラウザだけで扱える。"
        "情報Ⅰ「(4) データの収集・整理・分析」とも重なる、平均・分散・群比較・複数条件の統合判断といった"
        "分析の型を、探究基礎の中で、身近ではないが直感的に興味を引く題材（月面基地の最適地選び）を通して"
        "体験できる。"
        "今回新たに整備した3D入口Webアプリは、統計処理を経ずに「月面を見る・触る・場所の感覚をつかむ」段階を"
        "独立させたものであり、データ分析に入る前の動機づけと、分析結果を可視化して検算する場面の両方に使える。",
        "body"))
    story.append(P("（2）生徒観", "h2"))
    story.append(P(
        "情報の授業等で表計算やグラフ作成の基礎は学習している一方、「複数の指標を統合して意思決定する」経験は"
        "探究の場面でもまだ少ないと想定される。また、緯度経度で位置を捉える経験も地学基礎等に限られ、"
        "月面での温度差（約290K）"
        "のような、日常の量感から外れた数値を捉えにくい生徒がいることが予想される。"
        "（実施校・学年の実態に応じて加筆する）",
        "body"))
    story.append(P("（3）指導観", "h2"))
    story.append(P(
        "足場を強く設定した「ガイド型」の探究とし、各時間で「予想する→データで確かめる→意味づける」という"
        "サイクルを短く回す。班ごとに異なるミッション（太陽光発電・電波天文台・氷採掘・有人総合拠点）"
        "を割り当てることで、同じデータ・同じ手順を使っても班によって結論（最適地）が分かれることを体験させ、"
        "「探究には唯一の正解があるとは限らない」という実感につなげる。3D入口Webアプリは第1時の導入と、"
        "第3時で決定した最適地の確認（検算・可視化）の2箇所で用いる。",
        "body"))

    # ---- 2. 単元の目標 ----
    story.append(section("2．単元の目標"))
    for t in [
        "月面環境に関する複数のデータ（温度・地形・地球の見え方等）から、平均・分散・群比較などの"
        "基本統計量を用いて特徴を読み取ることができる。",
        "目的（ミッション）に応じて評価指標に重みをつけたスコアを設計し、複数の候補地を比較・判断する"
        "ことができる。",
        "自分たちの分析結果を他班の結果や実在の探査計画と比較し、判断の根拠やデータの限界を振り返ろうと"
        "する。",
    ]:
        story.append(P(f"・{t}", "body"))

    # ---- 3. 単元の評価規準 ----
    story.append(section("3．単元の評価規準"))
    eval_rows = [
        [P("知識・技能", "cellhead"), P("思考・判断・表現", "cellhead"),
         P("主体的に学習に取り組む態度", "cellhead")],
        [P("平均・分散などの基本統計量の意味を理解し、表計算ソフトやノートブックの操作で"
           "求めることができる。", "cell"),
         P("目的に応じて評価指標に重みをつけ、根拠を示して最適な候補地を選ぶことができる。", "cell"),
         P("自分たちの結論を他班の結果や実例と比較し、データの限界や妥当性を検討しようとしている。",
           "cell")],
    ]
    story.append(table_grid(eval_rows, col_widths=[54 * mm, 54 * mm, 54 * mm]))
    story.append(Spacer(1, 3 * mm))

    # ---- 4. 指導計画 ----
    story.append(section("4．指導計画（全3時間）"))
    plan_rows = [
        [P("時", "cellhead"), P("ねらい", "cellhead"), P("主な学習活動", "cellhead")],
        [P("1", "cell"),
         P("月面環境の特徴をつかみ、ミッションに応じた最適地を予想する。", "cell"),
         P("3D入口Webアプリでの自由探索、ミッションの確認、予想の記入・共有", "cell")],
        [P("2", "cell"),
         P("基本的な統計処理（平均・分散・群比較）でデータの特徴を読み取る。", "cell"),
         P("温度の1日の変化の分析（既存ステップ1相当）、海と陸の比較（既存ステップ2相当）", "cell")],
        [P("3", "cell"),
         P("複数指標を統合したスコア設計で最適地を決定し、他班・実例と比較する。", "cell"),
         P("全球俯瞰（既存ステップ3相当）、ミッション別スコア設計（既存ステップ4相当）、"
           "Webアプリでの確認、班発表・まとめ", "cell")],
    ]
    story.append(table_grid(plan_rows, col_widths=[10 * mm, 68 * mm, 84 * mm]))

    # ---- 5. 本時の学習指導 ----
    story.append(PageBreak())
    story.append(section("5．本時の学習指導"))

    def lesson_block(no: str, title: str, goal: str, rows):
        block = [P(f"第{no}時：{title}", "h2"), P(f"【目標】{goal}", "note")]
        widths = [16 * mm, 16 * mm, 60 * mm, 60 * mm, 30 * mm]
        header = [P("段階", "cellhead"), P("時間", "cellhead"), P("学習活動", "cellhead"),
                  P("指導上の留意点・支援", "cellhead"), P("評価", "cellhead")]
        table_rows = [header] + [
            [P(r[0], "cell"), P(r[1], "cell"), P(r[2], "cell"), P(r[3], "cell"), P(r[4], "cell")]
            for r in rows
        ]
        block.append(table_grid(table_rows, col_widths=widths))
        block.append(Spacer(1, 4 * mm))
        return block

    # 第1時
    story += lesson_block(
        "1", "3D入口Webアプリで月面環境を探索する",
        "月が大気を持たない環境であることを実感し、緯度経度・データ層という「地図の読み方」に"
        "慣れながら、自分の班のミッションに引きつけて最適地を予想する（仮説を立てる）。",
        [
            ("導入", "10分",
             "月には大気がない＝地球と全く違う環境であることを説明。本単元のゴール"
             "（データで基地の最適地を決める）を示し、班ごとにミッション"
             "（太陽光発電・電波天文台・氷採掘・有人総合）を割り当てる。",
             "少なくとも氷採掘・電波天文台・太陽光か有人の3種類がクラスに揃うようにする"
             "（後の時間で結論が分かれる核になるため）。",
             "―"),
            ("展開", "25分",
             "3D入口Webアプリ（各自 or 班で1台）を操作。ドラッグで月を回す、データ層"
             "（1日の温度／傾斜／地質年代／標高）を切り替える、気になる場所をクリックして"
             "ピンを立てる、左下の展開図で自分が見ている範囲とピンの位置を確認する。",
             "この時間は正解を出させない。数値の正しさより「触って気づく」ことを重視し、"
             "机間指導では操作のつまずき（データ層の切替え・ピンの消し方等）を支援する。",
             "（形成的）月面の様子や場所ごとの違いに気づき、記録しようとしているか。"),
            ("まとめ", "15分",
             "ワークシートに気づいたこと・自分のミッションでの予想（大まかな緯度経度でよい）を"
             "記入。数班に発表させ、「予想は本当に正しいか、次回以降データで確かめよう」と"
             "次時への問いを共有する。",
             "予想の正誤は問わない。次時以降で検証する見通しを持たせる。",
             "主体的に予想を記述し、発表しようとしているか。"),
        ]
    )

    # 第2時
    story += lesson_block(
        "2", "温度・海陸のデータから月面の特徴を読み取る",
        "1日の温度変化の幅（日較差）や、海と陸のクレーター密度・年代の違いを、平均・分散・群比較"
        "という統計の型を用いて数値で確かめる。",
        [
            ("導入", "5分",
             "前時の予想を振り返り、本時は「データで確かめる」時間であることを確認。"
             "表計算ソフト（またはノートブック）を開く。",
             "前時に記入したワークシートを参照させる。",
             "―"),
            ("展開①", "20分",
             "赤道付近と極付近の1日の温度カーブを比較し、日較差（最高温度－最低温度）を求める。"
             "既存の教材（`course_moonbase` の温度分析部分）を使用。",
             "「分散（ばらつき）」と「1日の温度差」を結びつけて説明する。極付近はデータが崩れる"
             "ことにも触れ、データの信頼できる範囲を考えさせる。",
             "（記録的）日較差の数値を正しく読み取り、記録できているか。〈知識・技能〉"),
            ("展開②", "20分",
             "海（暗い部分）と陸（明るい部分）でクレーターの密度・推定年代を比較する。"
             "USGS地質図のデータとも突き合わせる。",
             "「クレーターが少ない＝新しい」理由（溶岩に覆われて古いクレーターが消えた）を"
             "問い返しながら確認する。",
             "（記録的）群ごとの平均を比較し、違いの理由を説明しようとしているか。"
             "〈思考・判断・表現〉"),
            ("まとめ", "5分",
             "本時で分かったこと（日較差の大きさ、海と陸の違い）を一言でワークシートに"
             "まとめる。",
             "次時に「これらの指標を組み合わせて最適地を決める」ことを予告する。",
             "―"),
        ]
    )

    # 第3時
    story += lesson_block(
        "3", "指標を組み合わせて最適地を決定し、共有する",
        "複数の環境指標を統合したスコアを設計して自分たちの班の最適地を決定し、"
        "Webアプリで可視化して確認したうえで、他班・実在の探査計画と比較して考察する。",
        [
            ("導入", "5分",
             "前時までの分析（日較差・海陸の違い）を振り返る。本時のゴール"
             "（ミッションに応じた最適地を1つ決める）を確認。",
             "―",
             "―"),
            ("展開①", "15分",
             "月全体を俯瞰するデータ（日較差・地球の見え方・太陽高度・傾斜）を全球マップで見る。"
             "「どの指標も同時に最良になる場所はない」ことに気づかせる。",
             "「あなたのミッションでどの指標がいちばん大事か」を問い、次の重み付けにつなげる。",
             "（記録的）複数指標を比較し、トレードオフに気づいているか。〈思考・判断・表現〉"),
            ("展開②", "20分",
             "班のミッションに応じて指標に重みをつけたスコア式を設計し、上位の候補地を求める。"
             "決定した緯度経度を3D入口Webアプリでクリックしてピンを立て、実際にその場所が"
             "平らか・日照が良さそうかを目で見て確認する。",
             "地域を選ばず全球でスコアを計算すると南極ばかりが上位に来る班が出やすいので、"
             "先に地域タイプを選ばせる（＝目的の言語化）ことを徹底する。",
             "（記録的）重み付けの根拠を説明できるか。Webアプリでの確認結果を"
             "スコアと結び付けられるか。〈知識・技能〉〈思考・判断・表現〉"),
            ("まとめ", "10分",
             "班ごとに「ミッション・選んだ地域・最終的な緯度経度」を発表。黒板の月全球図に"
             "各班の最適地をプロットし、実在の探査計画（Artemis III＝南極、LCRT＝月の裏側、"
             "Apollo 11＝赤道）と比較する。",
             "「同じデータなのになぜ班ごとに違う場所になったか」「データのどこが信じきれないか」"
             "を問い、単元全体を振り返らせる。",
             "（総括的）他班・実例との比較から、判断の根拠やデータの限界を振り返ろうと"
             "しているか。〈主体的に学習に取り組む態度〉"),
        ]
    )

    # ---- 6. 使用教材・参考資料 ----
    story.append(PageBreak())
    story.append(section("6．使用教材・参考資料"))
    mat_rows = [
        [P("教材", "cellhead"), P("役割", "cellhead"), P("備考", "cellhead")],
        [P("3D入口Webアプリ\n（higonouneme.github.io/moon-data-lesson/）", "cell"),
         P("第1時の導入・第3時の確認", "cell"), P("公開済み。インストール不要", "cell")],
        [P("表計算ソフト版教材（18シート）\nまたは Colab版ノートブック", "cell"),
         P("第2・3時のデータ分析", "cell"),
         P("既存教材。3コマ用の抜粋版は今後作成", "cell")],
        [P("ワークシート", "cell"), P("生徒配布用の記録・振り返り", "cell"),
         P("既存の45分×4コマ版を、本案（3コマ）用に改訂する必要あり", "cell")],
        [P("進行表（教員用）", "cell"), P("各時のねらい・想定される結果・生徒のつまずき", "cell"),
         P("既存の45分×4コマ版を参照。本案はその抜粋・圧縮版", "cell")],
    ]
    story.append(table_grid(mat_rows, col_widths=[58 * mm, 46 * mm, 58 * mm]))

    # ---- 7. 今後の検討課題 ----
    story.append(Spacer(1, 4 * mm))
    story.append(section("7．今後の検討課題（あらあら版としての申し送り）"))
    for t in [
        "各時間の時間配分（特に第2・3時）が実際に50分に収まるかは未検証。一度リハーサルして"
        "計測する必要がある。",
        "本案専用のワークシート（3コマ構成）は未作成。",
        "第2・3時で表計算ソフト版とノートブック版のどちらを使うかは、実施校のICT環境を"
        "確認してから決定する。",
        "3D入口Webアプリは分析ノートブック本体（ブラウザ内で動くPythonノートブック）を"
        "まだ含んでいないため、第2・3時のデータ分析は現状Webアプリの外（表計算ソフトまたは"
        "ノートブック）で行う。将来アプリに統合できれば、教材間の行き来がより簡単になる。",
        "評価規準・評価方法（特に「主体的に学習に取り組む態度」の評価場面）は、実施校の"
        "評価方針に合わせて具体化する必要がある。",
        "本指導案は初期検討のたたき台であり、実際の実践・改善は別担当が行う前提で作成している。",
    ]:
        story.append(P(f"・{t}", "note"))

    doc.build(story)
    print(f"wrote {OUT_PATH}  ({os.path.getsize(OUT_PATH)/1024:.0f} KB)")


if __name__ == "__main__":
    build()
