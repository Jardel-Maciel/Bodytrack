import { useState, type FormEvent } from "react";

import { useExerciseCatalog } from "@/hooks/useExerciseCatalog";
import type { ExerciseCatalogItem } from "@/types";

import ExerciseImage from "./ExerciseImage";

/** Mesma ideia do backend: minúsculo, sem acento e sem pontuação. */
function normalize(text: string) {
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

interface Props {
  onCreate: (input: { name: string; muscle_group: string | null; exercises: { name: string; order: number }[] }) => Promise<void>;
  onCancel: () => void;
}

export default function NewWorkoutForm({ onCreate, onCancel }: Props) {
  const [name, setName] = useState("");
  const [muscleGroup, setMuscleGroup] = useState("");
  const [exercises, setExercises] = useState<string[]>([""]);
  const [submitting, setSubmitting] = useState(false);
  const { catalog } = useExerciseCatalog();

  // Só para a PRÉVIA no formulário: acha o exercício quando o texto bate exatamente
  // com um nome/apelido. A ligação oficial (inclusive com erro de digitação) é feita no backend.
  const findPreview = (typed: string): ExerciseCatalogItem | undefined => {
    const norm = normalize(typed);
    if (!norm) return undefined;
    return catalog.find((c) => normalize(c.name) === norm || c.aliases.some((a) => normalize(a) === norm));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const cleanExercises = exercises.map((e) => e.trim()).filter(Boolean);
    if (!name.trim() || cleanExercises.length === 0) return;

    setSubmitting(true);
    try {
      await onCreate({
        name: name.trim(),
        muscle_group: muscleGroup.trim() || null,
        exercises: cleanExercises.map((n, i) => ({ name: n, order: i })),
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-3">
      <p className="stat-label">Novo treino</p>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Nome (ex.: Treino A)"
        className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
      />
      <input
        value={muscleGroup}
        onChange={(e) => setMuscleGroup(e.target.value)}
        placeholder="Grupo muscular (opcional)"
        className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
      />

      <div className="space-y-2">
        <p className="text-xs text-foreground-muted">Exercícios</p>
        <datalist id="exercise-catalog-options">
          {catalog.map((c) => (
            <option key={c.id} value={c.name} />
          ))}
        </datalist>
        {exercises.map((value, index) => {
          const preview = findPreview(value);
          return (
            <div key={index} className="flex items-center gap-2">
              {preview && (
                <ExerciseImage
                  catalogId={preview.id}
                  alt=""
                  imageCount={preview.image_count}
                  className="h-10 w-10 shrink-0 rounded-lg border border-border object-cover"
                />
              )}
              <input
                value={value}
                list="exercise-catalog-options"
                onChange={(e) =>
                  setExercises((prev) => prev.map((v, i) => (i === index ? e.target.value : v)))
                }
                placeholder={`Exercício ${index + 1} (digite para ver sugestões)`}
                className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2 text-sm outline-none focus:border-accent"
              />
            </div>
          );
        })}
        <button
          type="button"
          onClick={() => setExercises((prev) => [...prev, ""])}
          className="text-xs text-accent hover:underline"
        >
          + adicionar exercício
        </button>
      </div>

      <div className="flex gap-2 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 rounded-xl border border-border py-2 text-sm text-foreground-muted hover:border-accent"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={submitting}
          className="flex-1 rounded-xl bg-accent py-2 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
        >
          {submitting ? "Salvando…" : "Criar treino"}
        </button>
      </div>
    </form>
  );
}
