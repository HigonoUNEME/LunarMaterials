/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * 月球儀にカーソルを合わせたとき、いま重ねているデータ層の「その地点の値」を出すための
 * ルックアップ。静的な層（site_environment.csv 由来）は siteEnvironment.ts の3度グリッドを
 * そのまま使う。1日の温度アニメーションは utils/diurnalLookup.ts が別に担当する（データが大きく
 * 遅延読み込みのため）。
 */
import { nearestEnv, SiteEnv } from './siteEnvironment';

// MoonViewer3D.tsx の DATA_LAYERS の key → SiteEnv のどの列を見るか
const LAYER_FIELD: Partial<Record<string, keyof SiteEnv>> = {
  temp_amp_K: 'tempAmp',
  night_min_K: 'nightMin',
  noon_sun_elev_deg: 'noonSun',
  earth_elev_deg: 'earthElev',
  slope_deg: 'slopeDeg',
  age_index: 'ageIndex',
  elev_m: 'elevM'
};

/** 静的なデータ層（1日の温度アニメーション以外）の、lat/lon にいちばん近いセルの値。
 *  対応する層でない・欠測（NaN）のときは null。 */
export function staticLayerValueAt(layerKey: string, lat: number, lon: number): number | null {
  const field = LAYER_FIELD[layerKey];
  if (!field) return null;
  const env = nearestEnv(lat, lon);
  if (!env) return null;
  const v = env[field];
  return typeof v === 'number' ? v : null;
}
