import * as THREE from 'three';

/**
 * Creates high-detail procedural lunar diffuse texture and bump map canvases
 * based on realistic lunar geographical maria, craters, ray systems, and highland regolith.
 */
export function createProceduralMoonTextures(): {
  colorTexture: THREE.CanvasTexture;
  bumpTexture: THREE.CanvasTexture;
} {
  const width = 2048;
  const height = 1024;

  const colorCanvas = document.createElement('canvas');
  colorCanvas.width = width;
  colorCanvas.height = height;
  const colorCtx = colorCanvas.getContext('2d')!;

  const bumpCanvas = document.createElement('canvas');
  bumpCanvas.width = width;
  bumpCanvas.height = height;
  const bumpCtx = bumpCanvas.getContext('2d')!;

  // 1. Base lunar highland regolith color & elevation
  const colorImgData = colorCtx.createImageData(width, height);
  const bumpImgData = bumpCtx.createImageData(width, height);
  const cData = colorImgData.data;
  const bData = bumpImgData.data;

  // Simple pseudo-random hash generator
  function hash(x: number, y: number) {
    const s = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453123;
    return s - Math.floor(s);
  }

  function noise(x: number, y: number) {
    const i = Math.floor(x);
    const j = Math.floor(y);
    const fx = x - i;
    const fy = y - j;

    const u = fx * fx * (3.0 - 2.0 * fx);
    const v = fy * fy * (3.0 - 2.0 * fy);

    const a = hash(i, j);
    const b = hash(i + 1, j);
    const c = hash(i, j + 1);
    const d = hash(i + 1, j + 1);

    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }

  function fbm(x: number, y: number) {
    let val = 0;
    let amp = 0.5;
    for (let o = 0; o < 5; o++) {
      val += amp * noise(x, y);
      x *= 2.1;
      y *= 2.1;
      amp *= 0.5;
    }
    return val;
  }

  // Major lunar maria positions in Lat/Long: (lat, lon, radiusDeg, darkness, roughShape)
  const mariaList = [
    { lat: 18, lon: -57, r: 28, dark: 0.52, name: 'Oceanus Procellarum' },
    { lat: 33, lon: -16, r: 16, dark: 0.55, name: 'Mare Imbrium' },
    { lat: 28, lon: 18, r: 12, dark: 0.54, name: 'Mare Serenitatis' },
    { lat: 8, lon: 31, r: 12, dark: 0.50, name: 'Mare Tranquillitatis' },
    { lat: 17, lon: 59, r: 9, dark: 0.52, name: 'Mare Crisium' },
    { lat: -1, lon: 56, r: 11, dark: 0.56, name: 'Mare Fecunditatis' },
    { lat: -15, lon: 35, r: 10, dark: 0.57, name: 'Mare Nectaris' },
    { lat: -9, lon: -20, r: 9, dark: 0.55, name: 'Mare Cognitum' },
    { lat: -19, lon: -93, r: 14, dark: 0.58, name: 'Mare Orientale' },
    { lat: -50, lon: 170, r: 20, dark: 0.65, name: 'South Pole-Aitken (Farside)' },
    { lat: 51, lon: -9, r: 3.5, dark: 0.48, name: 'Plato' },
    { lat: 43, lon: -31, r: 8, dark: 0.58, name: 'Sinus Iridum' }
  ];

  // Render base noise
  for (let y = 0; y < height; y++) {
    const lat = 90 - (y / height) * 180;
    for (let x = 0; x < width; x++) {
      const lon = (x / width) * 360 - 180;
      const idx = (y * width + x) * 4;

      // Base highland gray brightness
      const n = fbm(x * 0.02, y * 0.02);
      const detail = noise(x * 0.1, y * 0.1) * 0.15;
      let baseVal = 165 + (n * 70) + (detail * 20); // 165 ~ 250
      let bumpVal = 135 + (n * 90);

      // Check Maria influence
      let minMariaDist = 999;
      let mariaDarkness = 1.0;

      for (const m of mariaList) {
        // Spherical-approx distance in degrees
        const dLat = lat - m.lat;
        let dLon = Math.abs(lon - m.lon);
        if (dLon > 180) dLon = 360 - dLon;
        const dist = Math.sqrt(dLat * dLat + (dLon * Math.cos((m.lat * Math.PI) / 180)) ** 2);

        // Irregular noisy boundary
        const perturb = (noise(x * 0.03, y * 0.03) - 0.5) * (m.r * 0.4);
        const effectiveR = m.r + perturb;

        if (dist < effectiveR) {
          const factor = Math.cos((dist / effectiveR) * (Math.PI / 2));
          const blend = Math.pow(factor, 0.75);
          mariaDarkness = Math.min(mariaDarkness, 1.0 - (1.0 - m.dark) * blend);
          bumpVal -= blend * 35; // Basalt seas are topographically low depressions
        }
      }

      baseVal *= mariaDarkness;

      // Color variation (subtle warm/cool basalt hues)
      const r = Math.min(255, Math.max(20, baseVal * 0.98));
      const g = Math.min(255, Math.max(20, baseVal * 0.96));
      const b = Math.min(255, Math.max(20, baseVal * 0.93));

      cData[idx] = r;
      cData[idx + 1] = g;
      cData[idx + 2] = b;
      cData[idx + 3] = 255;

      const bp = Math.min(255, Math.max(10, bumpVal));
      bData[idx] = bp;
      bData[idx + 1] = bp;
      bData[idx + 2] = bp;
      bData[idx + 3] = 255;
    }
  }

  colorCtx.putImageData(colorImgData, 0, 0);
  bumpCtx.putImageData(bumpImgData, 0, 0);

  // 2. Draw prominent Craters and Ray Systems
  const keyCraters = [
    { lat: -43.3, lon: -11.3, r: 12, name: 'Tycho', rays: true, rayLen: 320, rayCount: 16 },
    { lat: 9.6, lon: -20.1, r: 14, name: 'Copernicus', rays: true, rayLen: 160, rayCount: 12 },
    { lat: 8.1, lon: -38.0, r: 8, name: 'Kepler', rays: true, rayLen: 110, rayCount: 8 },
    { lat: 23.7, lon: -47.5, r: 9, name: 'Aristarchus', rays: true, rayLen: 90, rayCount: 8, bright: true },
    { lat: -58.4, lon: -14.4, r: 24, name: 'Clavius', rays: false },
    { lat: 51.6, lon: -9.4, r: 15, name: 'Plato', rays: false, darkFloor: true },
    { lat: 35.9, lon: 102.8, r: 8, name: 'Giordano Bruno', rays: true, rayLen: 220, rayCount: 14 },
    { lat: -13.3, lon: 25.2, r: 5, name: 'Shioli/SLIM', rays: false },
    { lat: 26.1, lon: 3.6, r: 6, name: 'Hadley/Apollo 15', rays: false },
    { lat: -89.7, lon: 0.0, r: 7, name: 'Shackleton', rays: false }
  ];

  function latLonToCanvas(lat: number, lon: number): { cx: number; cy: number } {
    const cx = ((lon + 180) / 360) * width;
    const cy = ((90 - lat) / 180) * height;
    return { cx, cy };
  }

  // Draw Ray Systems
  for (const cr of keyCraters) {
    if (cr.rays) {
      const { cx, cy } = latLonToCanvas(cr.lat, cr.lon);
      const count = cr.rayCount || 10;
      for (let i = 0; i < count; i++) {
        const angle = (i / count) * Math.PI * 2 + (cr.lat * 0.1);
        const len = (cr.rayLen || 100) * (0.7 + Math.sin(i * 3) * 0.3);
        const endX = cx + Math.cos(angle) * len;
        const endY = cy + Math.sin(angle) * len;

        const rayGrad = colorCtx.createLinearGradient(cx, cy, endX, endY);
        rayGrad.addColorStop(0, 'rgba(250, 250, 255, 0.45)');
        rayGrad.addColorStop(0.3, 'rgba(235, 235, 250, 0.25)');
        rayGrad.addColorStop(1, 'rgba(200, 200, 220, 0.0)');

        colorCtx.save();
        colorCtx.beginPath();
        colorCtx.moveTo(cx, cy);
        colorCtx.lineTo(endX, endY);
        colorCtx.strokeStyle = rayGrad;
        colorCtx.lineWidth = Math.max(1.5, cr.r * 0.25);
        colorCtx.stroke();
        colorCtx.restore();
      }
    }
  }

  // Draw Crater Rims, Terraces and Central Peaks
  for (const cr of keyCraters) {
    const { cx, cy } = latLonToCanvas(cr.lat, cr.lon);
    const crRadius = cr.r;

    // Crater Rim Bright Glow (Color Canvas)
    const craterGrad = colorCtx.createRadialGradient(cx, cy, 0, cx, cy, crRadius * 1.5);
    if (cr.darkFloor) {
      craterGrad.addColorStop(0, '#2b2c2f');
      craterGrad.addColorStop(0.65, '#353639');
      craterGrad.addColorStop(0.85, '#a3a5a8');
      craterGrad.addColorStop(1, 'rgba(160, 160, 160, 0)');
    } else if (cr.bright) {
      craterGrad.addColorStop(0, '#ffffff');
      craterGrad.addColorStop(0.4, '#eef2f8');
      craterGrad.addColorStop(0.8, '#cbd2db');
      craterGrad.addColorStop(1, 'rgba(200, 210, 230, 0)');
    } else {
      craterGrad.addColorStop(0, '#55585c');
      craterGrad.addColorStop(0.4, '#81858a');
      craterGrad.addColorStop(0.8, '#d8dbe0');
      craterGrad.addColorStop(1, 'rgba(180, 185, 195, 0)');
    }

    colorCtx.save();
    colorCtx.beginPath();
    colorCtx.arc(cx, cy, crRadius * 1.4, 0, Math.PI * 2);
    colorCtx.fillStyle = craterGrad;
    colorCtx.fill();

    // Central peak for large craters
    if (crRadius >= 8 && !cr.darkFloor) {
      colorCtx.beginPath();
      colorCtx.arc(cx, cy, Math.max(1.5, crRadius * 0.15), 0, Math.PI * 2);
      colorCtx.fillStyle = '#ffffff';
      colorCtx.fill();
    }
    colorCtx.restore();

    // Crater Elevation in Bump Map (Depression + Elevated Rim)
    const bumpGrad = bumpCtx.createRadialGradient(cx, cy, 0, cx, cy, crRadius * 1.3);
    bumpGrad.addColorStop(0, '#202020'); // Deep floor
    bumpGrad.addColorStop(0.6, '#404040');
    bumpGrad.addColorStop(0.8, '#ffffff'); // High rim
    bumpGrad.addColorStop(1, 'rgba(128, 128, 128, 0)');

    bumpCtx.save();
    bumpCtx.beginPath();
    bumpCtx.arc(cx, cy, crRadius * 1.3, 0, Math.PI * 2);
    bumpCtx.fillStyle = bumpGrad;
    bumpCtx.fill();

    if (crRadius >= 8) {
      bumpCtx.beginPath();
      bumpCtx.arc(cx, cy, Math.max(2, crRadius * 0.18), 0, Math.PI * 2);
      bumpCtx.fillStyle = '#e0e0e0';
      bumpCtx.fill();
    }
    bumpCtx.restore();
  }

  // Create Three.js Canvas Textures
  const colorTexture = new THREE.CanvasTexture(colorCanvas);
  colorTexture.wrapS = THREE.RepeatWrapping;
  colorTexture.wrapT = THREE.ClampToEdgeWrapping;
  colorTexture.generateMipmaps = true;
  colorTexture.minFilter = THREE.LinearMipmapLinearFilter;
  colorTexture.magFilter = THREE.LinearFilter;

  const bumpTexture = new THREE.CanvasTexture(bumpCanvas);
  bumpTexture.wrapS = THREE.RepeatWrapping;
  bumpTexture.wrapT = THREE.ClampToEdgeWrapping;
  bumpTexture.generateMipmaps = true;
  bumpTexture.minFilter = THREE.LinearMipmapLinearFilter;
  bumpTexture.magFilter = THREE.LinearFilter;

  return { colorTexture, bumpTexture };
}

/**
 * Converts Latitude and Longitude to 3D Cartesian coordinates on a sphere of radius R
 * Three.js standard spherical mapping:
 * - Latitude: -90° (South Pole) to +90° (North Pole)
 * - Longitude: -180° (West) to +180° (East)
 */
export function latLongToVector3(lat: number, lon: number, radius: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);

  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return new THREE.Vector3(x, y, z);
}

/**
 * Inverse conversion: Vector3 on sphere to Latitude/Longitude
 */
export function vector3ToLatLong(point: THREE.Vector3): { lat: number; lon: number } {
  const normalized = point.clone().normalize();
  const lat = 90 - Math.acos(Math.max(-1, Math.min(1, normalized.y))) * (180 / Math.PI);
  let lon = (Math.atan2(normalized.z, -normalized.x) * (180 / Math.PI)) - 180;
  if (lon < -180) lon += 360;
  if (lon > 180) lon -= 360;
  return { lat, lon };
}
