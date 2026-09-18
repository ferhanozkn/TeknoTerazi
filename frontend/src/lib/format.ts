export function timeAgo(isoDate: string): string {
  const seconds = Math.max(0, (Date.now() - new Date(isoDate).getTime()) / 1000);
  const units: [number, string][] = [
    [60, "saniye"],
    [60, "dakika"],
    [24, "saat"],
    [30, "gün"],
    [12, "ay"],
    [Number.POSITIVE_INFINITY, "yıl"],
  ];

  let value = seconds;
  let unitLabel = "saniye";
  for (const [factor, label] of units) {
    if (value < factor) {
      unitLabel = label;
      break;
    }
    value = Math.floor(value / factor);
    unitLabel = label;
  }

  const rounded = Math.max(1, Math.floor(value));
  return `${rounded} ${unitLabel} önce`;
}

export function timeUntil(isoDate: string): string {
  const seconds = Math.max(0, (new Date(isoDate).getTime() - Date.now()) / 1000);
  const days = Math.floor(seconds / 86400);
  if (days >= 1) return `${days} gün`;
  const hours = Math.floor(seconds / 3600);
  if (hours >= 1) return `${hours} saat`;
  const minutes = Math.floor(seconds / 60);
  return `${Math.max(1, minutes)} dakika`;
}
