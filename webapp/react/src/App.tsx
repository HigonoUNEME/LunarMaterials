/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo, useCallback } from 'react';
import { LUNAR_DATASETS } from './data/lunarData';
import { LunarFeature, MoonViewerSettings } from './types';
import { MoonViewer3D } from './components/MoonViewer3D';
import { MinimalSidePanel } from './components/MinimalSidePanel';
import { Header } from './components/Header';
import { CheckCircle2 } from 'lucide-react';

export default function App() {
  const [activeDatasetId, setActiveDatasetId] = useState<string>('landing-sites');
  // 既定では何も選択しない（須藤の指摘：勝手にアポロ11号が「選択中」になっているのは不要）。
  // ユーザーが月をクリックするか、右の一覧から選ぶまで null のまま。
  const [selectedFeature, setSelectedFeature] = useState<LunarFeature | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const [settings, setSettings] = useState<MoonViewerSettings>({
    autoRotate: false,
    rotationSpeed: 0.35,
    wireframe: false,
    showGrid: true,
    lightIntensity: 2.2,
    moonRotationDeg: 0,
    selectedCategoryFilter: 'all',
    showDataLayer: false,
    dataLayerKey: 'temp_amp_K'
  });

  const handleUpdateSettings = useCallback((patch: Partial<MoonViewerSettings>) => {
    setSettings(prev => ({ ...prev, ...patch }));
  }, []);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3600);
  }, []);

  const activeDataset = useMemo(
    () => LUNAR_DATASETS.find(d => d.id === activeDatasetId) || LUNAR_DATASETS[0],
    [activeDatasetId]
  );

  // 3D月球儀は常設ピンを出さず、カーソルを合わせたときの名前判定・クリック選択のためだけに
  // 全データセットの地点を渡す（どのパネルを開いていても、近くの地点名が出るようにする）。
  const allFeatures = useMemo(() => {
    const seen = new Set<string>();
    const out: LunarFeature[] = [];
    for (const ds of LUNAR_DATASETS) {
      for (const f of ds.data) {
        if (!seen.has(f.id)) {
          seen.add(f.id);
          out.push(f);
        }
      }
    }
    return out;
  }, []);

  const handleSelectFeature = useCallback((feature: LunarFeature) => {
    setSelectedFeature(feature);
    const parent = LUNAR_DATASETS.find(d => d.data.some(x => x.id === feature.id));
    if (parent && parent.id !== activeDatasetId) setActiveDatasetId(parent.id);
  }, [activeDatasetId]);

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100 font-sans overflow-hidden selection:bg-cyan-500/30">
      {toast && (
        <div
          id="global-toast"
          className="fixed top-16 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2.5 bg-emerald-950/95 border border-emerald-500/50 text-emerald-200 px-4 py-2.5 rounded-xl shadow-2xl backdrop-blur-md text-xs font-medium"
        >
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          {toast}
        </div>
      )}

      <Header />

      {/* 二段組み：左＝月、右＝データ選択。狭い画面では縦に積む。 */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        <div className="relative h-[42vh] lg:h-auto lg:w-[46%] lg:min-w-[420px] shrink-0 border-b lg:border-b-0 lg:border-r border-slate-800">
          <MoonViewer3D
            features={allFeatures}
            selectedFeature={selectedFeature}
            onSelectFeature={handleSelectFeature}
            settings={settings}
            onUpdateSettings={handleUpdateSettings}
            fill
          />
        </div>

        <div className="flex-1 overflow-y-auto lg:min-w-0">
          <MinimalSidePanel
            datasets={LUNAR_DATASETS}
            activeDatasetId={activeDatasetId}
            onSelectDatasetId={setActiveDatasetId}
            onToast={showToast}
          />
        </div>
      </div>
    </div>
  );
}
