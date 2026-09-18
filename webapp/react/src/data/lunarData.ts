import { LunarDataset } from '../types';

export const LUNAR_DATASETS: LunarDataset[] = [
  {
    id: 'landing-sites',
    title: 'Lunar Surface Missions & Landing Sites',
    titleJa: '月面着陸地点・探査機データベース',
    description: 'アポロ計画有人着陸地点、ルナ計画、嫦娥計画、SLIM、チャンドラヤーン等の緯度経度・帰還サンプル量・観測ステータスデータ',
    category: 'missions',
    categoryLabelJa: '探査・着陸ミッション',
    icon: 'Rocket',
    badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    downloadFileName: 'lunar_landing_missions_database.csv',
    columns: [
      { key: 'nameJa', label: 'ミッション・着陸機名 (日本語)' },
      { key: 'name', label: 'Mission / Lander Name (EN)' },
      { key: 'agency', label: '宇宙機関 / 国' },
      { key: 'year', label: '着陸年月日' },
      { key: 'latitude', label: '緯度 (deg)', unit: '°' },
      { key: 'longitude', label: '経度 (deg)', unit: '°' },
      { key: 'status', label: 'ミッション結果' },
      { key: 'sampleMassKg', label: '回収サンプル質量 (kg)', unit: 'kg' },
      { key: 'landingSiteFeature', label: '着陸地海・クレーター名' },
      { key: 'description', label: '概要と科学的成果' }
    ],
    data: [
      {
        id: 'apollo-11',
        name: 'Apollo 11 (Eagle Lander)',
        nameJa: 'アポロ11号 (静かの基地)',
        category: 'missions',
        agency: 'NASA (USA)',
        year: '1969-07-20',
        latitude: 0.67408,
        longitude: 23.47297,
        status: '成功 (有人着陸・サンプル採取)',
        description: '人類史上初の月面有人着陸。アームストロング船長とオルドリン飛行士が静かの海に着陸し、21.55kgの月試料を地球に持ち帰った。',
        attributes: {
          sampleMassKg: 21.55,
          landingSiteFeature: 'Mare Tranquillitatis (静かの海)',
          durationHours: 21.6,
          evaCount: 1
        }
      },
      {
        id: 'apollo-12',
        name: 'Apollo 12 (Intrepid Lander)',
        nameJa: 'アポロ12号 (嵐の大洋)',
        category: 'missions',
        agency: 'NASA (USA)',
        year: '1969-11-19',
        latitude: -3.01239,
        longitude: -23.42157,
        status: '成功 (ピンポイント着陸達成)',
        description: '無人探査機サーベイヤー3号からわずか183mの位置に高精度着陸。ALSEP科学観測ステーションを設置し、34.35kgのサンプルを回収。',
        attributes: {
          sampleMassKg: 34.35,
          landingSiteFeature: 'Oceanus Procellarum (嵐の大洋)',
          durationHours: 31.5,
          evaCount: 2
        }
      },
      {
        id: 'apollo-14',
        name: 'Apollo 14 (Antares Lander)',
        nameJa: 'アポロ14号 (フラ・マウロ)',
        category: 'missions',
        agency: 'NASA (USA)',
        year: '1971-02-05',
        latitude: -3.64530,
        longitude: -17.47136,
        status: '成功 (コーンクレーター探査)',
        description: '巨大衝突盆地インブリウムの噴出物地質帯であるフラ・マウロ高地を探査。42.28kgの岩石試料を採取。',
        attributes: {
          sampleMassKg: 42.28,
          landingSiteFeature: 'Fra Mauro Highlands (フラ・マウロ高地)',
          durationHours: 33.5,
          evaCount: 2
        }
      },
      {
        id: 'apollo-15',
        name: 'Apollo 15 (Falcon Lander)',
        nameJa: 'アポロ15号 (ハドリー谷・アペニン山脈)',
        category: 'missions',
        agency: 'NASA (USA)',
        year: '1971-07-30',
        latitude: 26.13222,
        longitude: 3.63386,
        status: '成功 (初の月面車ローバー運用)',
        description: '初のLRV（月面車）を導入し27.9kmを走破。創世記の石（ジェネシス・ロック: 斜長岩）を含む77.31kgのサンプルを採取。',
        attributes: {
          sampleMassKg: 77.31,
          landingSiteFeature: 'Hadley Rille / Apennine (ハドリー谷)',
          durationHours: 66.9,
          evaCount: 3
        }
      },
      {
        id: 'apollo-16',
        name: 'Apollo 16 (Orion Lander)',
        nameJa: 'アポロ16号 (デカルト高地)',
        category: 'missions',
        agency: 'NASA (USA)',
        year: '1972-04-21',
        latitude: -8.97301,
        longitude: 15.50019,
        status: '成功 (高地テクトニクス探査)',
        description: '月高地地帯デカルト高地に着陸。火山起源と予想されていた高地が衝突溶融角礫岩で構成されていることを実証。サンプル95.71kg。',
        attributes: {
          sampleMassKg: 95.71,
          landingSiteFeature: 'Descartes Highlands (デカルト高地)',
          durationHours: 71.0,
          evaCount: 3
        }
      },
      {
        id: 'apollo-17',
        name: 'Apollo 17 (Challenger Lander)',
        nameJa: 'アポロ17号 (タウルス・リトロウ谷)',
        category: 'missions',
        agency: 'NASA (USA)',
        year: '1972-12-11',
        latitude: 20.19080,
        longitude: 30.77168,
        status: '成功 (地質学者ハリスン・シュミット搭乗)',
        description: 'アポロ計画最後の有人月面着陸。オレンジ色の火山性ガラス土壌を発見。最重量となる110.52kgのサンプルを地球に持ち帰った。',
        attributes: {
          sampleMassKg: 110.52,
          landingSiteFeature: 'Taurus-Littrow Valley (タウルス・リトロウ谷)',
          durationHours: 75.0,
          evaCount: 3
        }
      },
      {
        id: 'slim-jaxa',
        name: 'SLIM (Smart Lander for Investigating Moon)',
        nameJa: 'SLIM (小型月着陸実証機・ピンポイント着陸)',
        category: 'missions',
        agency: 'JAXA (Japan)',
        year: '2024-01-20',
        latitude: -13.3160,
        longitude: 25.2510,
        status: '成功 (目標から約55mの超高精度着陸)',
        description: '日本初の月面着陸機。目標地点からわずか55mのピンポイント着陸に成功。マルチバンド分光カメラ（MBC）によりカンラン石組成を解析。',
        attributes: {
          sampleMassKg: 0,
          landingSiteFeature: 'Shioli Crater (神酒の海・シオリクレーター斜面)',
          durationHours: 720,
          evaCount: 0
        }
      },
      {
        id: 'change-4',
        name: 'Chang\'e 4 & Yutu-2 Rover',
        nameJa: '嫦娥4号＆玉兎2号 (月裏面初着陸)',
        category: 'missions',
        agency: 'CNSA (China)',
        year: '2019-01-03',
        latitude: -45.457,
        longitude: 177.588,
        status: '成功 (史上初の月裏面軟着陸)',
        description: '人類史上初となる月の裏面（南極エイトケン盆地内のフォン・カルマン・クレーター）への軟着陸。中継衛星「鵲橋」を介した通信で現在も走行中。',
        attributes: {
          sampleMassKg: 0,
          landingSiteFeature: 'Von Kármán Crater (フォン・カルマン・クレーター)',
          durationHours: 40000,
          evaCount: 0
        }
      },
      {
        id: 'change-5',
        name: 'Chang\'e 5',
        nameJa: '嫦娥5号 (若年玄武岩サンプルリターン)',
        category: 'missions',
        agency: 'CNSA (China)',
        year: '2020-12-01',
        latitude: 43.099,
        longitude: -51.837,
        status: '成功 (1.731kgサンプル回収)',
        description: 'リュムカー山付近の若い玄武岩地帯（約20億年前）からサンプルを採取し地球に帰還。月の火山活動期間の定説を10億年近く更新した。',
        attributes: {
          sampleMassKg: 1.731,
          landingSiteFeature: 'Mons Rümker (リュムカー山北西)',
          durationHours: 48,
          evaCount: 0
        }
      },
      {
        id: 'change-6',
        name: 'Chang\'e 6',
        nameJa: '嫦娥6号 (月裏面初サンプルリターン)',
        category: 'missions',
        agency: 'CNSA (China)',
        year: '2024-06-01',
        latitude: -41.638,
        longitude: -153.985,
        status: '成功 (月裏面から1.935kgサンプル回収)',
        description: '人類史上初となる月の裏面（アポロ・クレーター南部）からのサンプルリターンに成功。月の表裏非対称性の起源解明へ。',
        attributes: {
          sampleMassKg: 1.935,
          landingSiteFeature: 'Apollo Crater South (アポロ衝突盆地南部)',
          durationHours: 48,
          evaCount: 0
        }
      },
      {
        id: 'chandrayaan-3',
        name: 'Chandrayaan-3 (Vikram / Pragyan)',
        nameJa: 'チャンドラヤーン3号 (月南極域軟着陸)',
        category: 'missions',
        agency: 'ISRO (India)',
        year: '2023-08-23',
        latitude: -69.373,
        longitude: 32.319,
        status: '成功 (高緯度・南極付近着陸)',
        description: 'インド初の月面軟着陸機。南緯69度付近の「シブ・シャクティ点」に着陸し、プラギャン探査車により硫黄やアルミニウムなどの元素を検出。',
        attributes: {
          sampleMassKg: 0,
          landingSiteFeature: 'Shiv Shakti Point (マンジナスとボガスラフスキー間)',
          durationHours: 336,
          evaCount: 0
        }
      },
      {
        id: 'luna-9',
        name: 'Luna 9 (Soviet Union)',
        nameJa: 'ルナ9号 (人類初の月面軟着陸)',
        category: 'missions',
        agency: 'Soviet Space Program (USSR)',
        year: '1966-02-03',
        latitude: 7.08,
        longitude: -64.37,
        status: '成功 (月面からの初パノラマ写真送信)',
        description: '人類史上初めて天体に制御された軟着陸を果たした探査機。月面が厚いダスト層に覆われて沈み込むという仮説を否定した。',
        attributes: {
          sampleMassKg: 0,
          landingSiteFeature: 'Oceanus Procellarum (嵐の大洋西部)',
          durationHours: 75,
          evaCount: 0
        }
      },
      {
        id: 'luna-16',
        name: 'Luna 16 (Automatic Sample Return)',
        nameJa: 'ルナ16号 (無人自動サンプルリターン)',
        category: 'missions',
        agency: 'Soviet Space Program (USSR)',
        year: '1970-09-20',
        latitude: -0.68,
        longitude: 56.30,
        status: '成功 (101g自動回収・帰還)',
        description: '無人ロボットドリルによる自動穿孔とサンプルリターンカプセルによる地球帰還を世界で初めて無人で達成。',
        attributes: {
          sampleMassKg: 0.101,
          landingSiteFeature: 'Mare Fecunditatis (豊かの海)',
          durationHours: 26,
          evaCount: 0
        }
      },
      {
        id: 'surveyor-3',
        name: 'Surveyor 3 Lander',
        nameJa: 'サーベイヤー3号 (ロボットアーム土壌試験)',
        category: 'missions',
        agency: 'NASA (USA)',
        year: '1967-04-20',
        latitude: -3.015,
        longitude: -23.418,
        status: '成功 (アポロ12号による回収調査)',
        description: 'ロボットアームで月土壌を掘削試験。後にアポロ12号の宇宙飛行士が訪問しカメラなどの部品を地球に持ち帰って宇宙環境暴露を解析した。',
        attributes: {
          sampleMassKg: 0,
          landingSiteFeature: 'Oceanus Procellarum (嵐の大洋)',
          durationHours: 336,
          evaCount: 0
        }
      }
    ]
  },
  {
    id: 'craters',
    title: 'Major Lunar Craters Catalog',
    titleJa: '月面主要クレーター・地質地形カタログ',
    description: 'ティコ、コペルニクス、アリスタルコス、シャックルトン等の直径・深度・地質年代・光条構造。直径と深度は USGS Gazetteer 系の代表値（文献により多少の幅がある）',
    category: 'geomorphology',
    categoryLabelJa: '衝突地形・クレーター',
    icon: 'Disc',
    badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    downloadFileName: 'lunar_craters_geomorphology_catalog.csv',
    columns: [
      { key: 'nameJa', label: 'クレーター名 (日本語)' },
      { key: 'name', label: 'Crater Name (EN)' },
      { key: 'diameterKm', label: '直径 (km)', unit: 'km' },
      { key: 'depthKm', label: '深度 (km)', unit: 'km' },
      { key: 'latitude', label: '緯度 (deg)', unit: '°' },
      { key: 'longitude', label: '経度 (deg)', unit: '°' },
      { key: 'geologicEra', label: '地質年代' },
      { key: 'raySystem', label: '光条 (レイ) の有無' },
      { key: 'description', label: '地形特徴・命名由来' }
    ],
    data: [
      {
        id: 'crater-tycho',
        name: 'Tycho',
        nameJa: 'ティコ・クレーター',
        category: 'craters',
        diameterKm: 85,
        depthKm: 4.8,
        latitude: -43.31,
        longitude: -11.36,
        description: '満月時に月面全体に広がる1,500km以上の顕著な白い光条系（レイ）を持つ若年クレーター。中央峰の高さは約1.6km。',
        attributes: {
          geologicEra: 'コペルニクス代 (約1億800万年前)',
          raySystem: '極めて明瞭 (最大長 1500km+)',
          centralPeakHeightKm: 1.6,
          namedAfter: 'デンマークの天文学者ティコ・ブラーエ'
        }
      },
      {
        id: 'crater-copernicus',
        name: 'Copernicus',
        nameJa: 'コペルニクス・クレーター',
        category: 'craters',
        diameterKm: 96,
        depthKm: 3.8,
        latitude: 9.62,
        longitude: -20.08,
        description: '「月の君主」と称される巨大テラス構造と複雑な三重中央峰を持つ標本的な複合衝突クレーター。雨の海南部に位置。',
        attributes: {
          geologicEra: 'コペルニクス代 (約8億年前)',
          raySystem: '明瞭 (広範囲)',
          centralPeakHeightKm: 1.2,
          namedAfter: '天文学者ニコラウス・コペルニクス'
        }
      },
      {
        id: 'crater-kepler',
        name: 'Kepler',
        nameJa: 'ケプラー・クレーター',
        category: 'craters',
        diameterKm: 29.5,
        depthKm: 2.6,
        latitude: 8.12,
        longitude: -38.01,
        description: '嵐の大洋と島々の海の境界に位置する小型ながら非常に明るい光条系を持つクレーター。',
        attributes: {
          geologicEra: 'コペルニクス代',
          raySystem: '明瞭',
          centralPeakHeightKm: 0.5,
          namedAfter: 'ドイツの天文学者ヨハネス・ケプラー'
        }
      },
      {
        id: 'crater-aristarchus',
        name: 'Aristarchus',
        nameJa: 'アリスタルコス・クレーター',
        category: 'craters',
        diameterKm: 40,
        depthKm: 3.7,
        latitude: 23.73,
        longitude: -47.49,
        description: '月面で最もアルベド（反射率）が高い高輝度クレーター。過渡的月面現象（TLP: 発光やガス噴出）の観測報告が最も多い。',
        attributes: {
          geologicEra: 'コペルニクス代 (約4億5000万年前)',
          raySystem: '極めて高輝度',
          centralPeakHeightKm: 0.8,
          namedAfter: '古代ギリシャの天文学者アリスタルコス'
        }
      },
      {
        id: 'crater-clavius',
        name: 'Clavius',
        nameJa: 'クラビウス・クレーター',
        category: 'craters',
        diameterKm: 231,
        depthKm: 3.5,
        latitude: -58.40,
        longitude: -14.40,
        description: '月面南部の巨大な古い環状クレーター。内部底面には弧を描くように並ぶ小クレーター列が存在する。',
        attributes: {
          geologicEra: 'ネクタリス代 (約39億年前)',
          raySystem: 'なし (侵食された縁)',
          centralPeakHeightKm: 0,
          namedAfter: '数学者・天文学者クリストファー・クラヴィウス'
        }
      },
      {
        id: 'crater-shackleton',
        name: 'Shackleton',
        nameJa: 'シャックルトン・クレーター (南極)',
        category: 'craters',
        diameterKm: 21,
        depthKm: 4.2,
        latitude: -89.67,
        longitude: 0.00,
        description: '月の真の南極点に位置。縁取り部はほぼ恒久的に日光が当たる一方、内部底面は永久影となっており氷の存在が極めて有望視されている。',
        attributes: {
          geologicEra: 'エラトステネス代',
          raySystem: 'なし (永久影領域)',
          centralPeakHeightKm: 0,
          namedAfter: '南極探検家アーネスト・シャックルトン'
        }
      },
      {
        id: 'crater-plato',
        name: 'Plato',
        nameJa: 'プラトー・クレーター',
        category: 'craters',
        diameterKm: 101,
        depthKm: 1.0,
        latitude: 51.62,
        longitude: -9.38,
        description: '雨の海北側の山脈に位置する平坦で黒い玄武岩溶岩に満たされた独特の円形クレーター。',
        attributes: {
          geologicEra: '後期インブリウム代',
          raySystem: 'なし',
          centralPeakHeightKm: 0,
          namedAfter: '哲学者プラトン'
        }
      },
      {
        id: 'crater-giordano-bruno',
        name: 'Giordano Bruno',
        nameJa: 'ジョルダーノ・ブルーノ (月裏面)',
        category: 'craters',
        diameterKm: 22,
        depthKm: 2.1,
        latitude: 35.90,
        longitude: 102.80,
        description: '月の裏面に位置する極めて新鮮で強力な光条を持つ若いクレーター。西暦1178年にカンタベリーの修道士が目撃した爆発現象との関連が議論された。',
        attributes: {
          geologicEra: 'コペルニクス代 (極めて若年)',
          raySystem: '超広範囲 (月裏面全体)',
          centralPeakHeightKm: 0.6,
          namedAfter: '哲学者ジョルダーノ・ブルーノ'
        }
      }
    ]
  },
  {
    id: 'maria',
    title: 'Lunar Maria & Basins Directory',
    titleJa: '月の海・大盆地データベース',
    description: '静かの海、雨の海、嵐の大洋等の面積・玄武岩溶岩厚・Fe/Ti含有量・重力異常マスコン分布データ',
    category: 'geomorphology',
    categoryLabelJa: '海・盆地構造',
    icon: 'Globe',
    badgeColor: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
    downloadFileName: 'lunar_maria_basins_directory.csv',
    columns: [
      { key: 'nameJa', label: '海・盆地名 (日本語)' },
      { key: 'name', label: 'Mare / Basin Name (Latin/EN)' },
      { key: 'diameterKm', label: '直径 / 最大長 (km)', unit: 'km' },
      { key: 'latitude', label: '中心緯度 (deg)', unit: '°' },
      { key: 'longitude', label: '中心経度 (deg)', unit: '°' },
      { key: 'surfaceAreaSqKm', label: '推定表面積 (km²)', unit: 'km²' },
      { key: 'tio2ContentPct', label: 'TiO2 (二酸化チタン) 濃度 (%)', unit: '%' },
      { key: 'hasMascon', label: 'マスコン (正重力異常)' },
      { key: 'description', label: '地質学的特徴' }
    ],
    data: [
      {
        id: 'mare-tranquillitatis',
        name: 'Mare Tranquillitatis',
        nameJa: '静かの海',
        category: 'maria',
        diameterKm: 873,
        latitude: 8.50,
        longitude: 31.40,
        description: 'アポロ11号着陸地。高チタン玄武岩で覆われており、青みがかった暗色を呈する。',
        attributes: {
          surfaceAreaSqKm: 421000,
          tio2ContentPct: 7.5,
          hasMascon: '弱〜中程度',
          rockType: '高チタン玄武岩'
        }
      },
      {
        id: 'mare-imbrium',
        name: 'Mare Imbrium',
        nameJa: '雨の海',
        category: 'maria',
        diameterKm: 1123,
        latitude: 32.80,
        longitude: -15.60,
        description: '月面第2位の広さを持つ巨大衝突盆地。アペニン山脈などの高山に囲まれ、中心部には強力な正重力異常（マスコン）が存在。',
        attributes: {
          surfaceAreaSqKm: 830000,
          tio2ContentPct: 3.2,
          hasMascon: '極めて強い (最大級)',
          rockType: '低〜中チタン玄武岩'
        }
      },
      {
        id: 'oceanus-procellarum',
        name: 'Oceanus Procellarum',
        nameJa: '嵐の大洋',
        category: 'maria',
        diameterKm: 2592,
        latitude: 18.40,
        longitude: -57.40,
        description: '月面最大の暗黒域（海）であり、唯一「大洋」の名を持つ。カリウム、希土類、リンに富むKREEP玄武岩が広く露出。',
        attributes: {
          surfaceAreaSqKm: 4000000,
          tio2ContentPct: 4.8,
          hasMascon: 'なし (構造不規則)',
          rockType: 'KREEP質・玄武岩溶岩流'
        }
      },
      {
        id: 'mare-serenitatis',
        name: 'Mare Serenitatis',
        nameJa: '晴れの海',
        category: 'maria',
        diameterKm: 707,
        latitude: 28.00,
        longitude: 17.50,
        description: '雨の海の東隣に位置するほぼ完全な円形盆地。周囲にはリンクルリッジ（しわ状隆起）が美しく発達。',
        attributes: {
          surfaceAreaSqKm: 303000,
          tio2ContentPct: 5.4,
          hasMascon: '顕著なマスコン',
          rockType: '多層玄武岩'
        }
      },
      {
        id: 'mare-crisium',
        name: 'Mare Crisium',
        nameJa: '危機の海',
        category: 'maria',
        diameterKm: 555,
        latitude: 17.00,
        longitude: 59.10,
        description: '月の東端に位置する孤立した楕円形盆地。周囲を高台に囲まれており、ルナ15・23・24号が着陸。',
        attributes: {
          surfaceAreaSqKm: 176000,
          tio2ContentPct: 2.1,
          hasMascon: '明確なマスコン',
          rockType: '超低チタン・中チタン玄武岩'
        }
      },
      {
        id: 'mare-orientale',
        name: 'Mare Orientale',
        nameJa: '東の海 (オリエンターレ盆地)',
        category: 'maria',
        diameterKm: 900,
        latitude: -19.40,
        longitude: -92.80,
        description: '月の西縁〜裏面境界に位置する、溶岩の充填が少なく同心円状の多重環構造が最も明瞭に保存された教科書的衝突盆地。',
        attributes: {
          surfaceAreaSqKm: 69000,
          tio2ContentPct: 1.5,
          hasMascon: '中心部マスコン＋周囲負重力異常',
          rockType: '薄い玄武岩被覆・角礫岩'
        }
      }
    ]
  },
  {
    id: 'moonquakes',
    title: 'Apollo Seismic & Moonquake Events',
    titleJa: '月震・地震観測データベース',
    description: 'アポロ12, 14, 15, 16号ALSEPパッシブ地震計ネットワークが捉えた月震の代表例。震央は推定値で不確かさが大きく（浅発月震は数百km、多くは個別に未決定）、座標が正確なのは人工衝突のみ。',
    category: 'geophysics',
    categoryLabelJa: '地球物理・月震',
    icon: 'Activity',
    badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
    downloadFileName: 'apollo_passive_seismic_moonquakes.csv',
    columns: [
      { key: 'nameJa', label: '月震イベント分類' },
      { key: 'name', label: 'Event ID / Catalog' },
      { key: 'latitude', label: '推定震央緯度 (deg)', unit: '°' },
      { key: 'longitude', label: '推定震央経度 (deg)', unit: '°' },
      { key: 'focalDepthKm', label: '震源深度 (km)', unit: 'km' },
      { key: 'magnitude', label: '推定マグニチュード (Richter scale)' },
      { key: 'durationMinutes', label: '振動継続時間 (分)', unit: '分' },
      { key: 'causeMechanism', label: '発生原因メカニズム' },
      { key: 'description', label: '観測詳細' }
    ],
    data: [
      {
        id: 'quake-a1-deep',
        name: 'Deep Moonquake Nest A1',
        nameJa: '深発月震ネスト A1 (最頻発)',
        category: 'moonquakes',
        latitude: -15.7,
        longitude: -36.6,
        description: '月内部の深さ約900kmで地球の潮汐力サイクル（27.3日）に同期して周期的に発生する深発月震の代表的震源。アポロ12号観測点の南西約180km、震源位置の推定値（Nakamura）。',
        attributes: {
          focalDepthKm: 900,
          magnitude: 1.8,
          durationMinutes: 45,
          causeMechanism: '地球潮汐応力 (潮汐同期)',
          stationDetected: 'Apollo 12, 14, 15, 16'
        }
      },
      {
        id: 'quake-shallow-1975',
        name: 'Shallow Moonquake (1975, largest HFT)',
        nameJa: '大浅発月震 (1975年・最大級)',
        category: 'moonquakes',
        latitude: 29.8,
        longitude: -98.6,
        description: '観測史上最大級の浅発月震（1975年、体波マグニチュード約5）。月殻浅部（深さ0〜20km）で発生し、散乱減衰が少ないため1時間以上にわたり月全体が鐘のように振動した。震央は概略。',
        attributes: {
          focalDepthKm: 18,
          magnitude: 5.0,
          durationMinutes: 110,
          causeMechanism: '月大域的熱収縮・断層テクトニクス',
          stationDetected: '全観測点'
        }
      },
      {
        id: 'quake-shallow-1973',
        name: 'Shallow Moonquake (high-latitude)',
        nameJa: '浅発月震 (南極高緯度域)',
        category: 'moonquakes',
        latitude: -84.0,
        longitude: 134.0,
        description: '月の高緯度帯付近で観測された浅発月震。若い衝上断層（lobate scarp）との関連が指摘されており（Watters ほか 2019）、将来の恒久有人基地の耐震設計の根拠になる。震央は概略。',
        attributes: {
          focalDepthKm: 25,
          magnitude: 3.2,
          durationMinutes: 70,
          causeMechanism: 'スラスト断層活動 (熱収縮)',
          stationDetected: 'Apollo 14, 15, 16'
        }
      },
      {
        id: 'quake-meteoroid-1972',
        name: 'Major Meteoroid Impact (1972)',
        nameJa: '大型隕石衝突震 (1972年)',
        category: 'moonquakes',
        latitude: 2.1,
        longitude: 130.4,
        description: 'アポロ地震網が検出した最大級の隕石衝突（推定質量 数百kg〜1t 級、月の裏側）。裏面から到来する地震波として記録され、月の内部構造の解析に使われた。位置は概略。',
        attributes: {
          focalDepthKm: 0,
          magnitude: 3.8,
          durationMinutes: 140,
          causeMechanism: '天然隕石・小天体衝突',
          stationDetected: '全観測点'
        }
      },
      {
        id: 'quake-sivb-13-impact',
        name: 'Apollo 13 S-IVB Artificial Impact',
        nameJa: 'アポロ13号 S-IVB段人工衝突実験',
        category: 'moonquakes',
        latitude: -2.75,
        longitude: -27.86,
        description: 'サターンVロケット第3段（S-IVB）を意図的に月面に秒速2.5kmで激突させ、人工地震波により月地殻の厚み（約30〜40km）を測定。',
        attributes: {
          focalDepthKm: 0,
          magnitude: 2.5,
          durationMinutes: 195,
          causeMechanism: '較正用人工ロケットブースター衝突',
          stationDetected: 'Apollo 12 ALSEP'
        }
      }
    ]
  },
  {
    id: 'resources',
    title: 'Lunar South Pole & In-Situ Resources (ISRU)',
    titleJa: '月南極水氷・資源インベントリ',
    description: 'アルテミス計画着陸候補地、永久影クレーター内の水氷推定量、イルメナイト(チタン・酸素源)、太陽光連続照射率。緯度経度は各地形の位置だが、水氷重量比・日照率はミッション文献の推定値で出典により幅がある。',
    category: 'resources',
    categoryLabelJa: '資源・水氷・拠点候補',
    icon: 'Droplets',
    badgeColor: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
    downloadFileName: 'lunar_polar_resources_isru_inventory.csv',
    columns: [
      { key: 'nameJa', label: '資源・拠点候補名 (日本語)' },
      { key: 'name', label: 'Site / Prospect Name (EN)' },
      { key: 'latitude', label: '緯度 (deg)', unit: '°' },
      { key: 'longitude', label: '経度 (deg)', unit: '°' },
      { key: 'estimatedWaterIcePct', label: '推定水氷重量比 (%)', unit: '%' },
      { key: 'sunlightIlluminationPct', label: '年間日照率 (%)', unit: '%' },
      { key: 'temperatureKelvinMin', label: '最低到達温度 (K)', unit: 'K' },
      { key: 'primaryResource', label: '主要資源・利用価値' },
      { key: 'description', label: 'アルテミス計画での戦略的位置づけ' }
    ],
    data: [
      {
        id: 'res-cabeus',
        name: 'Cabeus Crater (LCROSS Impact Site)',
        nameJa: 'カベウス・クレーター (LCROSS水検出地点)',
        category: 'resources',
        latitude: -84.9,
        longitude: -35.5,
        description: 'NASA LCROSS衝突実験によりプルームから水蒸気（約5.5wt%）、メタン、アンモニア、銀などの揮発性物質が直接分光検出された歴史的サイト。',
        attributes: {
          estimatedWaterIcePct: 5.5,
          sunlightIlluminationPct: 12,
          temperatureKelvinMin: 40,
          primaryResource: '水氷 (H2O), メタン (CH4), アンモニア',
          artemisTargetRank: '超重要観測対象'
        }
      },
      {
        id: 'res-connecting-ridge',
        name: 'Connecting Ridge (Shackleton-de Gerlache)',
        nameJa: 'シャックルトン-ド・ジェラシュ連絡尾根',
        category: 'resources',
        latitude: -89.4,
        longitude: -135.0,
        description: 'アルテミス3号有人着陸最有力候補地の一つ。年間85%以上の高日照率と、隣接する極低温永久影域への即時アクセスを兼ね備える。',
        attributes: {
          estimatedWaterIcePct: 2.8,
          sunlightIlluminationPct: 86,
          temperatureKelvinMin: 55,
          primaryResource: '太陽光発電電力 + 隣接永久影水氷',
          artemisTargetRank: '有人基地最優先候補'
        }
      },
      {
        id: 'res-shoemaker',
        name: 'Shoemaker Crater Floor',
        nameJa: 'シューメーカー・クレーター底面',
        category: 'resources',
        latitude: -88.1,
        longitude: 45.9,
        description: 'ルナー・リコネサンス・オービター（LRO）の中性子分光計により大量の水素（水等価水素量）が濃集していることが確認された領域。',
        attributes: {
          estimatedWaterIcePct: 4.2,
          sunlightIlluminationPct: 0,
          temperatureKelvinMin: 35,
          primaryResource: '高純度埋没水氷層',
          artemisTargetRank: '資源採掘探査地'
        }
      },
      {
        id: 'res-faustini',
        name: 'Faustini Crater Rim & Floor',
        nameJa: 'ファウスティーニ・クレーター',
        category: 'resources',
        latitude: -87.3,
        longitude: 77.0,
        description: '深い永久影を持ち熱赤外線温度計（Diviner）で25K（-248℃）という太陽系最低水準の極低温が記録されたコールドトラップ。',
        attributes: {
          estimatedWaterIcePct: 6.0,
          sunlightIlluminationPct: 5,
          temperatureKelvinMin: 25,
          primaryResource: '超低温極冷揮発性物質・二酸化炭素氷',
          artemisTargetRank: '揮発性物質リザーバー'
        }
      },
      {
        id: 'res-aristarchus-pyroclastic',
        name: 'Aristarchus Pyroclastic Glass Deposits',
        nameJa: 'アリスタルコス火山性ガラス・イルメナイト鉱床',
        category: 'resources',
        latitude: 24.5,
        longitude: -48.0,
        description: 'チタン鉄鉱（イルメナイト FeTiO3）に富む広大な火山性火砕物堆積層。酸素抽出および将来の月面金属製錬に最適。',
        attributes: {
          estimatedWaterIcePct: 0.05,
          sunlightIlluminationPct: 50,
          temperatureKelvinMin: 100,
          primaryResource: 'イルメナイト (FeTiO3)・酸素抽出・太陽電池用シリコン',
          artemisTargetRank: '赤道域工業資源拠点'
        }
      }
    ]
  }
];
