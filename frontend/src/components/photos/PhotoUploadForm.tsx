import { useState, type FormEvent } from "react";

import type { PhotoAngle } from "@/types";
import { todayIso } from "@/utils/format";

interface Props {
  onUpload: (input: { angle: PhotoAngle; date: string; week_number: number | null; file: File }) => Promise<void>;
}

const ANGLES: { value: PhotoAngle; label: string }[] = [
  { value: "front", label: "Frente" },
  { value: "side", label: "Lado" },
  { value: "back", label: "Costas" },
];

export default function PhotoUploadForm({ onUpload }: Props) {
  const [angle, setAngle] = useState<PhotoAngle>("front");
  const [weekNumber, setWeekNumber] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) return;
    setSubmitting(true);
    try {
      await onUpload({
        angle,
        date: todayIso(),
        week_number: weekNumber ? Number(weekNumber) : null,
        file,
      });
      setFile(null);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-3">
      <p className="stat-label">Check-in fotográfico</p>
      <div className="flex gap-2">
        {ANGLES.map((a) => (
          <button
            key={a.value}
            type="button"
            onClick={() => setAngle(a.value)}
            className={`flex-1 rounded-xl border py-2 text-sm ${
              angle === a.value ? "border-accent bg-accent-muted text-white" : "border-border text-foreground-muted"
            }`}
          >
            {a.label}
          </button>
        ))}
      </div>
      <input
        type="number"
        min={1}
        value={weekNumber}
        onChange={(e) => setWeekNumber(e.target.value)}
        placeholder="Semana (opcional)"
        className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
      />
      <input
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        className="w-full text-sm text-foreground-muted"
      />
      <button
        type="submit"
        disabled={!file || submitting}
        className="w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
      >
        {submitting ? "Enviando…" : "Enviar foto"}
      </button>
      <p className="text-xs text-foreground-muted">
        Fotos são privadas por padrão e nunca usadas para treinar IA.
      </p>
    </form>
  );
}
