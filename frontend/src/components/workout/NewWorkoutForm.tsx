import { useState, type FormEvent } from "react";

interface Props {
  onCreate: (input: { name: string; muscle_group: string | null; exercises: { name: string; order: number }[] }) => Promise<void>;
  onCancel: () => void;
}

export default function NewWorkoutForm({ onCreate, onCancel }: Props) {
  const [name, setName] = useState("");
  const [muscleGroup, setMuscleGroup] = useState("");
  const [exercises, setExercises] = useState<string[]>([""]);
  const [submitting, setSubmitting] = useState(false);

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
        {exercises.map((value, index) => (
          <input
            key={index}
            value={value}
            onChange={(e) =>
              setExercises((prev) => prev.map((v, i) => (i === index ? e.target.value : v)))
            }
            placeholder={`Exercício ${index + 1}`}
            className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2 text-sm outline-none focus:border-accent"
          />
        ))}
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
