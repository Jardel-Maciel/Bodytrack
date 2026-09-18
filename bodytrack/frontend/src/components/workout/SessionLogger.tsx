import { useState } from "react";

import type { Workout } from "@/types";
import { todayIso } from "@/utils/format";

interface SetInput {
  reps: string;
  load_kg: string;
}

interface Props {
  workout: Workout;
  onSubmit: (input: {
    date: string;
    sets: { workout_exercise_id: string; set_number: number; reps: number; load_kg: number }[];
  }) => Promise<void>;
  onCancel: () => void;
}

/** Um bloco de 3 séries por exercício por padrão — o usuário pode adicionar mais. */
export default function SessionLogger({ workout, onSubmit, onCancel }: Props) {
  const [setsByExercise, setSetsByExercise] = useState<Record<string, SetInput[]>>(() =>
    Object.fromEntries(workout.exercises.map((ex) => [ex.id, [{ reps: "", load_kg: "" }, { reps: "", load_kg: "" }, { reps: "", load_kg: "" }]]))
  );
  const [submitting, setSubmitting] = useState(false);

  const updateSet = (exerciseId: string, index: number, field: keyof SetInput, value: string) => {
    setSetsByExercise((prev) => ({
      ...prev,
      [exerciseId]: prev[exerciseId].map((s, i) => (i === index ? { ...s, [field]: value } : s)),
    }));
  };

  const addSet = (exerciseId: string) => {
    setSetsByExercise((prev) => ({ ...prev, [exerciseId]: [...prev[exerciseId], { reps: "", load_kg: "" }] }));
  };

  const handleSubmit = async () => {
    const sets = workout.exercises.flatMap((ex) =>
      setsByExercise[ex.id]
        .map((s, i) => ({ workout_exercise_id: ex.id, set_number: i + 1, reps: Number(s.reps), load_kg: Number(s.load_kg) }))
        .filter((s) => s.reps > 0 && s.load_kg >= 0 && !Number.isNaN(s.reps) && !Number.isNaN(s.load_kg))
    );
    if (sets.length === 0) return;

    setSubmitting(true);
    try {
      await onSubmit({ date: todayIso(), sets });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card space-y-4">
      <p className="stat-label">Registrar sessão — {workout.name}</p>
      {workout.exercises.map((exercise) => (
        <div key={exercise.id} className="space-y-2">
          <p className="text-sm font-medium">{exercise.name}</p>
          {setsByExercise[exercise.id].map((set, index) => (
            <div key={index} className="flex items-center gap-2">
              <span className="w-14 text-xs text-foreground-muted">Série {index + 1}</span>
              <input
                type="number"
                value={set.reps}
                onChange={(e) => updateSet(exercise.id, index, "reps", e.target.value)}
                placeholder="reps"
                className="w-20 rounded-lg border border-border bg-background-elevated px-2 py-1.5 text-sm outline-none focus:border-accent"
              />
              <span className="text-xs text-foreground-muted">×</span>
              <input
                type="number"
                step="0.5"
                value={set.load_kg}
                onChange={(e) => updateSet(exercise.id, index, "load_kg", e.target.value)}
                placeholder="kg"
                className="w-20 rounded-lg border border-border bg-background-elevated px-2 py-1.5 text-sm outline-none focus:border-accent"
              />
            </div>
          ))}
          <button type="button" onClick={() => addSet(exercise.id)} className="text-xs text-accent hover:underline">
            + adicionar série
          </button>
        </div>
      ))}

      <div className="flex gap-2 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 rounded-xl border border-border py-2 text-sm text-foreground-muted hover:border-accent"
        >
          Cancelar
        </button>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={submitting}
          className="flex-1 rounded-xl bg-accent py-2 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
        >
          {submitting ? "Salvando…" : "Salvar sessão"}
        </button>
      </div>
    </div>
  );
}
