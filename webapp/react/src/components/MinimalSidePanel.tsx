import React, { useMemo } from 'react';
import { LunarDataset } from '../types';
import { downloadDatasetAsCSV } from '../utils/csvExport';
import { Download } from 'lucide-react';

interface MinimalSidePanelProps {
  datasets: LunarDataset[];
  activeDatasetId: string;
  onSelectDatasetId: (id: string) => void;
  onToast: (msg: string) => void;
}

/**
 * 公開最小版（2026-09-18）用の簡易パネル。
 * 「地点を選ぶ」一覧・詳細カードと「分析にすすむ」（ノートブック導線）は、
 * まだノートブックのColab/JupyterLite版を用意していないため今回は含めない。
 * データセットを選んでCSVをダウンロードできることだけに絞っている。
 * 通常版（一覧・検索・詳細カード付き）は SidePanel.tsx を参照。
 */
export const MinimalSidePanel: React.FC<MinimalSidePanelProps> = ({
  datasets,
  activeDatasetId,
  onSelectDatasetId,
  onToast
}) => {
  const activeDataset = useMemo(
    () => datasets.find(d => d.id === activeDatasetId) || datasets[0],
    [datasets, activeDatasetId]
  );
  const totalPoints = datasets.reduce((a, d) => a + d.data.length, 0);

  return (
    <div className="flex flex-col gap-5 p-4 sm:p-5 text-slate-200">
      <p className="text-xs leading-relaxed text-slate-400">
        月の有名な地点 <strong className="text-slate-200">{totalPoints}件</strong> のデータセットです。
        左の3D月球儀はドラッグで回転・ホイールで拡大縮小でき、🌡️アイコンから温度などのデータ層を重ねられます。
        データセットを選ぶと、その全件をCSVでダウンロードできます。
      </p>

      <section className="flex flex-col gap-2">
        <h2 className="flex items-center gap-2 text-xs font-bold text-slate-300">
          <span className="flex w-5 h-5 items-center justify-center rounded-full bg-slate-800 text-cyan-400 text-[11px] font-black">1</span>
          データを選ぶ
        </h2>
        <div className="flex flex-col gap-1.5">
          {datasets.map(ds => {
            const active = ds.id === activeDatasetId;
            return (
              <button
                key={ds.id}
                id={`dataset-pick-${ds.id}`}
                onClick={() => onSelectDatasetId(ds.id)}
                className={`w-full text-left rounded-xl border px-3 py-2.5 transition-colors ${
                  active
                    ? 'bg-cyan-950/40 border-cyan-500/50'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold ${active ? 'text-cyan-200' : 'text-slate-100'}`}>
                    {ds.titleJa}
                  </span>
                  <span className="ml-auto text-[10px] font-mono text-slate-400">{ds.data.length}件</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1 leading-snug line-clamp-2">{ds.description}</p>
              </button>
            );
          })}
        </div>
      </section>

      <section className="flex flex-col gap-2">
        <h2 className="flex items-center gap-2 text-xs font-bold text-slate-300">
          <span className="flex w-5 h-5 items-center justify-center rounded-full bg-slate-800 text-cyan-400 text-[11px] font-black">2</span>
          CSVをダウンロード
        </h2>
        <button
          id="btn-panel-download-csv"
          onClick={() => {
            downloadDatasetAsCSV(activeDataset);
            onToast(`「${activeDataset.titleJa}」を CSV でダウンロードしました`);
          }}
          className="flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition-colors"
        >
          <Download className="w-3.5 h-3.5" />
          「{activeDataset.titleJa}」の{activeDataset.data.length}件をCSVでダウンロード
        </button>
      </section>

      <footer className="pt-3 border-t border-slate-800/80 text-[10px] text-slate-500 leading-relaxed">
        代表地点は USGS Gazetteer・IAU・各ミッション公式・Apollo 地震カタログ等の公開情報にもとづく概略値。
        月面テクスチャは NASA/LROC カラーモザイク（パブリックドメイン）。
      </footer>
    </div>
  );
};
