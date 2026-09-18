import { useState, type FormEvent } from "react";

import { useProject } from "@/contexts/ProjectContext";
import { todayIso } from "@/utils/format";

const WEEK_OPTIONS = [1, 4, 8, 12, 16, 20, 24];

export default function CreateProjectForm() {
  const { createProject } = useProject();
  const [name, setName] = useState("Minha Transformação");
  const [weeks, setWeeks] = useState(16);
  const [startDate, setStartDate] = useState(todayIso());
  const [initialWeight, setInitialWeight] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const start = new Date(`${startDate}T00:00:00`);
      const end = new Date(start);
      end.setDate(end.getDate() + weeks * 7);

      await createProject({
        name,
        start_date: startDate,
        end_date: end.toISOString().slice(0, 10),
        initial_weight_kg: initialWeight ? Number(initialWeight) : null,
      });
    } catch {
      setError("Não foi possível criar o projeto. Tente novamente.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card">
      <h2 className="mb-1 text-base font-semibold">Crie seu primeiro projeto</h2>
      <p className="mb-4 text-sm text-foreground-muted">
        Um projeto é o seu ciclo de transformação (ex.: "16 semanas"). Você poderá criar outros depois.
      </p>
      <form className="space-y-3" onSubmit={handleSubmit}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome do projeto"
          required
          className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
        />
        <div className="grid grid-cols-2 gap-3">
          <label className="text-xs text-foreground-muted">
            Data inicial
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="mt-1 w-full rounded-xl border border-border bg-background-elevated px-3 py-2 text-sm outline-none focus:border-accent"
            />
          </label>
          <label className="text-xs text-foreground-muted">
            Duração
            <select
              value={weeks}
              onChange={(e) => setWeeks(Number(e.target.value))}
              className="mt-1 w-full rounded-xl border border-border bg-background-elevated px-3 py-2 text-sm outline-none focus:border-accent"
            >
              {WEEK_OPTIONS.map((w) => (
                <option key={w} value={w}>
                  {w} semanas
                </option>
              ))}
            </select>
          </label>
        </div>
        <input
          type="number"
          step="0.1"
          min="0"
          value={initialWeight}
          onChange={(e) => setInitialWeight(e.target.value)}
          placeholder="Peso inicial (kg) — opcional"
          className="w-full rounded-xl border border-border bg-background-elevated px-3 py-2.5 text-sm outline-none focus:border-accent"
        />
        {error && <p className="text-sm text-danger">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-xl bg-accent py-2.5 text-sm font-semibold text-white hover:bg-accent-hover disabled:opacity-60"
        >
          {submitting ? "Criando…" : "Começar"}
        </button>
      </form>
    </div>
  );
}
