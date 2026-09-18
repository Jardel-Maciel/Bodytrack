interface Props {
  label: string;
  value: string;
  hint?: string;
}

export default function StatCard({ label, value, hint }: Props) {
  return (
    <div className="card">
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
      {hint && <p className="mt-1 text-xs text-foreground-muted">{hint}</p>}
    </div>
  );
}
