import { useEffect, useRef, useState, type FormEvent } from "react";

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
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  // Dois inputs escondidos: o de câmera usa `capture` para abrir a
  // câmera do celular direto (sem passar pelo seletor de arquivos), o
  // de galeria fica sem esse atributo para permitir escolher uma foto
  // já existente. Cada um é acionado por um botão próprio via ref,
  // porque não dá para alternar o atributo `capture` de um mesmo
  // <input> depois que ele já foi renderizado em alguns navegadores.
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const galleryInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

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
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => cameraInputRef.current?.click()}
          className="flex-1 rounded-xl border border-border py-2.5 text-sm font-medium text-foreground-muted hover:border-accent"
        >
          Tirar foto agora
        </button>
        <button
          type="button"
          onClick={() => galleryInputRef.current?.click()}
          className="flex-1 rounded-xl border border-border py-2.5 text-sm font-medium text-foreground-muted hover:border-accent"
        >
          Escolher da galeria
        </button>
      </div>
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        capture="environment"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        className="hidden"
      />
      <input
        ref={galleryInputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        className="hidden"
      />

      {previewUrl && (
        <div className="flex items-center gap-3 rounded-xl border border-border bg-background-elevated p-2">
          <img src={previewUrl} alt="Pré-visualização" className="h-16 w-16 rounded-lg object-cover" />
          <p className="text-xs text-foreground-muted">{file?.name}</p>
        </div>
      )}

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
