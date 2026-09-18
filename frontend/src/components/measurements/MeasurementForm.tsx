import { useEffect, useState } from "react";

import * as measurementService from "@/services/measurementService";
import type { BodyMeasurement } from "@/types";
import { todayIso } from "@/utils/format";

const FIELDS: { key: keyof Omit<BodyMeasurement, "id" | "project_id" | "date">; label: string }[] = [
  { key: "weight_kg", label: "Peso (kg)" },
  { key: "waist_cm", label: "Cintura (cm)" },
  { key: "abdomen_cm", label: "Abdômen (cm)" },
  { key: "hip_cm", label: "Quadril (cm)" },
  { key: "chest_cm", label: "Peito (cm)" },
  { key: "neck_cm", label: "Pescoço (cm)" },
  { key: "shoulders_cm", label: "Ombros (cm)" },
  { key: "arm_right_cm", label: "Braço direito (cm)" },
  { key: "arm_left_cm", label: "Braço esquerdo (cm)" },
  { key: "thigh_right_cm", label: "Coxa direita (cm)" },
  { key: "thigh_left_cm", label: "Coxa esquerda (cm)" },
  { key: "calf_right_cm", label: "Panturrilha direita (cm)" },
  { key: "calf_left_cm", label: "Panturrilha esquerda (cm)" },
];

type FormState = Record<string, string>;

const emptyForm = (): FormState => Object.fromEntries(FIELDS.map((f) => [f.key, ""]));

interface Props {
  projectId: string;
  onSaved: () => void;
}

export default function MeasurementForm({ projectId, onSaved }: Props) {
  const [date, setDate] = useState(todayIso());
  const [values, setValues] = useState<FormState>(emptyForm());
  const [loadingExisting, setLoadingExisting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<number | null>(null);

  // Ao trocar a data, carrega a medida já salva naquele dia (se houver)
  // para o formulário não sobrescrever com vazio campos que já tinham
  // valor — o upsert do backend substitui o registro inteiro.
  useEffect(() => {
    let cancelled = false;
    setLoadingExisting(true);
    setSavedAt(null);
    measurementService
      .getByDate(projectId, date)
      .then((existing) => {
        if (cancelled) return;
        if (existing) {
          setValues(
            Object.fromEntries(
              FIELDS.map((f) => [f.key, existing[f.key] != null ? String(existing[f.key]) : ""])
            )
          );
        } else {
          setValues(emptyForm());
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingExisting(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, date]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = Object.fromEntries(
        FIELDS.map((f) => [f.key, values[f.key] ? Number(values[f.key]) : null])
      ) as Omit<BodyMeasurement, "id" | "project_id" | "date">;
      await measurementService.upsert(projectId, { date, ...payload });
      setSavedAt(Date.now());
      onSaved();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <p className="stat-label">Registrar medidas</p>
        <input
          type="date"
          value={date}
          max={todayIso()}
          onChange={(e) => setDate(e.target.value)}
          className="rounded-lg border border-border bg-background-elevated px-2 py-1 text-xs outline-none focus:border-accent"
        />
      </div>

      {loadingExisting ? (
        <p className="text-sm text-foreground-muted">Carregando…</p>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {FIELDS.map((f) => (
            <label key={f.key} className="text-xs text-foreground-muted">
              {f.label}
              <input
                type="number"
                step="0.1"
                min={0}
                value={values[f.key]}
                onChange={(e) => setValues((prev) => ({ ...prev, [f.key]: e.target.value }))}
                className="mt-1 w-full rounded-xl border border-border bg-background-elevated px-3 py-2 text-sm text-foreground outline-none focus:border-accent"
              />
            </label>
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={handleSave}
        disabled={saving || loadingExisting}
        className="w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
      >
        {saving ? "Salvando…" : "Salvar medidas"}
      </button>
      {savedAt && <p className="text-center text-xs text-success">Medidas salvas.</p>}
      <p className="text-xs text-foreground-muted">
        Preencha só o que quiser acompanhar — deixe o resto em branco. Você pode voltar aqui e
        editar qualquer data depois.
      </p>
    </div>
  );
}
