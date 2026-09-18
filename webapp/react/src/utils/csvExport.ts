import { LunarDataset, LunarFeature } from '../types';

/**
 * Escapes and formats a single value for CSV compliance (RFC 4180)
 */
function formatCSVField(val: string | number | boolean | null | undefined): string {
  if (val === null || val === undefined) return '""';
  const str = String(val);
  if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return `"${str}"`;
}

/**
 * Converts a LunarDataset into a CSV formatted string with UTF-8 BOM
 */
export function convertDatasetToCSV(dataset: LunarDataset): string {
  const headers = dataset.columns.map(col => col.label);
  const keys = dataset.columns.map(col => col.key);

  const headerRow = headers.map(formatCSVField).join(',');

  const dataRows = dataset.data.map(item => {
    return keys.map(key => {
      if (key in item) {
        return formatCSVField((item as unknown as Record<string, unknown>)[key] as string | number);
      }
      if (item.attributes && key in item.attributes) {
        return formatCSVField(item.attributes[key]);
      }
      return '""';
    }).join(',');
  });

  return [headerRow, ...dataRows].join('\r\n');
}

/**
 * Triggers a browser download for the provided CSV string
 */
export function triggerCSVDownload(csvContent: string, fileName: string): void {
  // \uFEFF is UTF-8 Byte Order Mark (BOM) to ensure correct Japanese character encoding in Excel
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', fileName.endsWith('.csv') ? fileName : `${fileName}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Downloads an entire LunarDataset directly as CSV
 */
export function downloadDatasetAsCSV(dataset: LunarDataset): void {
  const csv = convertDatasetToCSV(dataset);
  triggerCSVDownload(csv, dataset.downloadFileName);
}

/**
 * Downloads a filtered subset of features as CSV
 */
export function downloadFilteredFeaturesAsCSV(
  dataset: LunarDataset,
  filteredData: LunarFeature[],
  customFileName?: string
): void {
  const partialDataset: LunarDataset = {
    ...dataset,
    data: filteredData
  };
  const csv = convertDatasetToCSV(partialDataset);
  const name = customFileName || `${dataset.id}_filtered_${new Date().toISOString().slice(0, 10)}.csv`;
  triggerCSVDownload(csv, name);
}
