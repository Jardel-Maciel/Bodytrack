import { useState, type FormEvent } from "react";

import ExerciseImage from "@/components/workout/ExerciseImage";
import { useExerciseCatalog } from "@/hooks/useExerciseCatalog";
import type { ExerciseCatalogItem, TrainerWorkout, TrainerWorkoutInput } from "@/types";

interface Row {
  key: number;
  id?: string; // presente = exercício que já existe (mantém o histórico do aluno)
  name: string;
  sets: string;
  reps: string;
  rest: string;
  notes: string;
}

interface Props {
  initial?: TrainerWorkout;
  saving: boolean;
  error: string | null;
  onSave: (input: TrainerWorkoutInput) => void;
  onCancel: () => void;
}

const inputClass =
  "w-full rounded-lg border border-border bg-background-elevated px-2.5 py-2 text-sm outline-none focus:border-accent";

function normalize(text: string) {
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

let nextKey = 1;

/** Editor de treino do personal: nome, grupo, observações e a lista de exercícios com séries/reps/descanso. */
export default function TrainerWorkoutEditor({ initial, saving, error, onSave, onCancel }: Props) {
  const { catalog } = useExerciseCatalog();
  const [name, setName] = useState(initial?.name ?? "");
  const [muscleGroup, setMuscleGroup] = useState(initial?.muscle_group ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [rows, setRows] = useState<Row[]>(() =>
    initial?.exercises.length
      ? initial.exercises.map((e) => ({
          key: nextKey++,
          id: e.id,
          name: e.name,
          sets: e.target_sets?.toString() ?? "",
          reps: e.target_reps ?? "",
          rest: e.rest_seconds?.toString() ?? "",
          notes: e.notes ?? "",
        }))
      : [{ key: nextKey++, name: "", sets: "3", reps: "10", rest: "60", notes: "" }]
  );

  const update = (key: number, patch: Partial<Row>) =>
    setRows((prev) => prev.map((r) => (r.key === key ? { ...r, ...patch } : r)));

  const move = (index: number, delta: -1 | 1) =>
    setRows((prev) => {
      const target = index + delta;
      if (target < 0 || target >= prev.length) return prev;
      const copy = [...prev];
      [copy[index], copy[target]] = [copy[target], copy[index]];
      return copy;
    });

  const preview = (typed: string): ExerciseCatalogItem | undefined => {
    const norm = normalize(typed);
    if (!norm) return undefined;
    return catalog.find((c) => normalize(c.name) === norm || c.aliases.some((a) => normalize(a) === norm));
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const exercises = rows
      .filter((r) => r.name.trim())
      .map((r) => ({
        ...(r.id ? { id: r.id } : {}),
        name: r.name.trim(),
        target_sets: r.sets ? Number(r.sets) : null,
        target_reps: r.reps.trim() || null,
        rest_seconds: r.rest ? Number(r.rest) : null,
        notes: r.notes.trim() || null,
      }));
    if (!name.trim() || exercises.length === 0) return;
    onSave({ name: name.trim(), muscle_group: muscleGroup.trim() || null, notes: notes.trim() || null, exercises });
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-3">
      <p className="stat-label">{initial ? "Editar treino" : "Novo treino"}</p>

      <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nome (ex.: Treino A — Peito)" className={inputClass} required />
      <input value={muscleGroup} onChange={(e) => setMuscleGroup(e.target.value)} placeholder="Grupo muscular (opcional)" className={inputClass} />
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Observações para o aluno (opcional)"
        rows={2}
        className={inputClass}
      />

      <datalist id="trainer-exercise-options">
        {catalog.map((c) => (
          <option key={c.id} value={c.name} />
        ))}
      </datalist>

      <div className="space-y-3">
        {rows.map((row, index) => {
          const match = preview(row.name);
          return (
            <div key={row.key} className="space-y-2 rounded-xl border border-border p-2.5">
              <div className="flex items-center gap-2">
                {match && (
                  <ExerciseImage
                    catalogId={match.id}
                    alt=""
                    imageCount={match.image_count}
                    className="h-10 w-10 shrink-0 rounded-lg border border-border object-cover"
                  />
                )}
                <input
                  value={row.name}
                  list="trainer-exercise-options"
                  onChange={(e) => update(row.key, { name: e.target.value })}
                  placeholder={`Exercício ${index + 1} (digite para ver sugestões)`}
                  className={inputClass}
                />
              </div>
              <div className="grid grid-cols-3 gap-2">
                <label className="space-y-0.5 text-[11px] text-foreground-muted">
                  Séries
                  <input type="number" min={1} max={20} value={row.sets} onChange={(e) => update(row.key, { sets: e.target.value })} className={inputClass} />
                </label>
                <label className="space-y-0.5 text-[11px] text-foreground-muted">
                  Reps
                  <input value={row.reps} onChange={(e) => update(row.key, { reps: e.target.value })} placeholder="8-10" maxLength={20} className={inputClass} />
                </label>
                <label className="space-y-0.5 text-[11px] text-foreground-muted">
                  Descanso (s)
                  <input type="number" min={0} value={row.rest} onChange={(e) => update(row.key, { rest: e.target.value })} className={inputClass} />
                </label>
              </div>
              <input value={row.notes} onChange={(e) => update(row.key, { notes: e.target.value })} placeholder="Dica de execução (opcional)" className={inputClass} />
              <div className="flex gap-3 text-xs">
                <button type="button" onClick={() => move(index, -1)} disabled={index === 0} className="text-accent disabled:opacity-30">
                  ↑ subir
                </button>
                <button type="button" onClick={() => move(index, 1)} disabled={index === rows.length - 1} className="text-accent disabled:opacity-30">
                  ↓ descer
                </button>
                <button
                  type="button"
                  onClick={() => setRows((prev) => prev.filter((r) => r.key !== row.key))}
                  disabled={rows.length === 1}
                  className="ml-auto text-danger disabled:opacity-30"
                >
                  remover
                </button>
              </div>
            </div>
          );
        })}
        <button
          type="button"
          onClick={() => setRows((prev) => [...prev, { key: nextKey++, name: "", sets: "3", reps: "10", rest: "60", notes: "" }])}
          className="text-xs text-accent hover:underline"
        >
          + adicionar exercício
        </button>
      </div>

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="flex gap-2 pt-1">
        <button type="button" onClick={onCancel} className="flex-1 rounded-xl border border-border py-2 text-sm text-foreground-muted hover:border-accent">
          Cancelar
        </button>
        <button type="submit" disabled={saving} className="flex-1 rounded-xl bg-accent py-2 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60">
          {saving ? "Salvando…" : "Salvar treino"}
        </button>
      </div>
    </form>
  );
}
