export function fmtKg(value: number | null | undefined): string {
  return value == null ? "—" : `${value.toFixed(1)} kg`;
}

export function fmtCm(value: number | null | undefined): string {
  return value == null ? "—" : `${value.toFixed(1)} cm`;
}

export function fmtSigned(value: number | null | undefined, unit: string): string {
  if (value == null) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)} ${unit}`;
}

export function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}
