import React from 'react';
import { Moon } from 'lucide-react';

/**
 * 画面いちばん上の細い帯。タイトルだけのシンプル版（公開最小版 2026-09-18）。
 * ノートブック（Colab/JupyterLite）・データ一覧ページはまだ用意していないため、
 * それらへの導線は含めない。用意でき次第 Header.tsx にリンクを戻す。
 */
export const Header: React.FC = () => {
  return (
    <header className="shrink-0 border-b border-slate-800/80 bg-slate-950/95 backdrop-blur-md">
      <div className="flex items-center gap-3 px-4 sm:px-5 py-2.5">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-slate-800 to-cyan-950 border border-cyan-500/30 shrink-0">
            <Moon className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="min-w-0">
            <h1 className="text-sm font-bold text-white truncate">
              月データでムーンベースの場所を決めよう
            </h1>
            <p className="text-[11px] text-slate-400 truncate">
              3D月球儀でデータを見て、CSVをダウンロードできる入口ページ（公開準備中・最小版）
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};
